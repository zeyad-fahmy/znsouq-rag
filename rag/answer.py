"""Answer a question: detect store → retrieve → ask Claude with grounding rules."""
import json
import os
import re
from datetime import date

import anthropic
from dotenv import load_dotenv

from rag.loader import DATA_DIR
from rag.retrieve import retrieve

load_dotenv()
MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
_client = None

# ---------- 1. Detect which store the question is about ----------
SELLERS = json.loads((DATA_DIR / "catalog" / "sellers.json").read_text(encoding="utf-8"))
STORE_NAMES = {s["store_name"].lower(): s["seller_id"] for s in SELLERS if s["seller_id"] != "S0000"}


def detect_seller(question: str):
    """Return the seller_id of a store named in the question, or None."""
    q = question.lower()
    for name, sid in sorted(STORE_NAMES.items(), key=lambda x: -len(x[0])):  # longest names first
        if name in q:
            return sid
    m = re.search(r"\bS\d{4}\b", question)  # e.g. "S0017"
    return m.group(0) if m else None


# ---------- 2. Build metadata filters ----------
def platform_filter(mode: str):
    """Platform help docs for this audience (no store pages)."""
    return {"$and": [
        {"audience": {"$in": [mode, "seller and buyer"]}},
        {"type": {"$ne": "store_page"}},
    ]}


def gather_context(question: str, mode: str = "buyer", k: int = 4):
    """Retrieve platform chunks, plus the store's own chunks if a store is mentioned."""
    hits = retrieve(question, k=k, where=platform_filter(mode))
    seller_id = detect_seller(question) if mode == "buyer" else None
    if seller_id:
        hits = retrieve(question, k=3, where={"seller_id": seller_id}) + hits
    return hits, seller_id


# ---------- 3. Prompt ----------
SYSTEM = """You are the ZNSouq support assistant, helping {audience} of ZNSouq, an online marketplace in Egypt.
Today's date is {today}.

Rules:
1. Answer ONLY using the numbered context passages. Do not use outside knowledge about ZNSouq.
2. If the passages don't contain the answer, say you don't know and suggest contacting customer service ({contact}). Never guess policies, prices or dates.
3. ZNSouq platform rules are minimums. If a store page conflicts with a platform rule, the platform rule wins: say so clearly.
4. When a rule depends on a date (e.g. fee changes), compare it with today's date.
5. Cite the passages you used like [1] or [2][3] right after the relevant sentence.
6. Be concise and friendly: a short direct answer first, then key details. Use EGP for money."""

CONTACT = {"buyer": "00001 (demo number) or help@znsouq.example", "seller": "00002 (demo number) or sellers@znsouq.example"}


def format_context(hits):
    blocks = []
    for i, h in enumerate(hits, 1):
        m = h["metadata"]
        blocks.append(f"[{i}] (source: {m['source']} › {m['section']})\n{h['text']}")
    return "\n\n".join(blocks)


# ---------- 4. Ask Claude ----------
def answer(question: str, mode: str = "buyer", k: int = 4):
    global _client
    hits, seller_id = gather_context(question, mode, k)
    system = SYSTEM.format(audience="buyers" if mode == "buyer" else "sellers",
                           today=date.today().isoformat(), contact=CONTACT[mode])
    user = f"<context>\n{format_context(hits)}\n</context>\n\nQuestion: {question}"
    if _client is None:
        _client = anthropic.Anthropic()
    response = _client.messages.create(
        model=MODEL,
        max_tokens=700,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return {"answer": response.content[0].text, "sources": hits, "seller_id": seller_id}
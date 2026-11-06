"""Answer a question: rewrite query → detect store → retrieve → ask Claude with grounding rules."""
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


def client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


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


# ---------- 2. Query rewriting ----------
REWRITE_PROMPT = """Rewrite the user's latest message as one standalone search query for ZNSouq's {audience} help center.
- Keep every specific word from the message (products, categories, store names, numbers, dates), then ADD the words a help article would use (e.g. "get paid" for a seller -> "get paid seller payout schedule"; "stale coffee" -> "stale coffee grocery return").
- If earlier messages are given, resolve references like "it", "that" or "and for X?".
- Keep store names, product names and numbers exactly as written.
Output only the query, nothing else.

{history}Latest message: {question}"""


def rewrite_query(question: str, mode: str = "buyer", history=None):
    """Use Claude to turn a short or vague question into a clear search query."""
    hist = ""
    if history:
        lines = [f"{m['role']}: {m['content'][:300]}" for m in history[-4:]]   # last 4 messages is enough
        hist = "Earlier messages:\n" + "\n".join(lines) + "\n\n"
    msg = client().messages.create(
        model=MODEL,
        max_tokens=100,
        messages=[{"role": "user", "content": REWRITE_PROMPT.format(
            audience="buyer" if mode == "buyer" else "seller", history=hist, question=question)}],
    )
    return msg.content[0].text.strip()


# ---------- 3. Retrieval with filters ----------
def platform_filter(mode: str):
    """Platform help docs for this audience (no store pages)."""
    return {"$and": [
        {"audience": {"$in": [mode, "seller and buyer"]}},
        {"type": {"$ne": "store_page"}},
    ]}


def chunk_key(h):
    return (h["metadata"]["source"], h["metadata"]["section"], h["metadata"]["part"])


def search(question, search_query, k, where, extra=2):
    """Keep the original question's top-k, then ADD up to `extra` new chunks found by the rewrite.
    The rewrite can only add chunks, never push out what the original question found."""
    hits = retrieve(question, k=k, where=where)
    seen = {chunk_key(h) for h in hits}
    if search_query and search_query.strip().lower() != question.strip().lower():
        for h in retrieve(search_query, k=k, where=where):
            if len(hits) >= k + extra:
                break
            if chunk_key(h) not in seen:
                hits.append(h)
                seen.add(chunk_key(h))
    return hits


def gather_context(question: str, mode: str = "buyer", k: int = 4, history=None):
    """Retrieve platform chunks, plus the store's own chunks if a store is mentioned."""
    search_query = rewrite_query(question, mode, history)
    hits = search(question, search_query, k, platform_filter(mode))
    seller_id = detect_seller(question + " " + search_query) if mode == "buyer" else None
    if seller_id:
        hits = search(question, search_query, 3, {"seller_id": seller_id}, extra=1) + hits
    return hits, seller_id, search_query


# ---------- 4. Prompt ----------
SYSTEM = """You are the ZNSouq support assistant, helping {audience} of ZNSouq, an online marketplace in Egypt.
Today's date is {today}.

Rules:
1. Answer ONLY using the numbered context passages. Do not use outside knowledge about ZNSouq.
2. If the passages don't contain the answer, say you don't know and suggest contacting customer service ({contact}). Never guess policies, prices or dates.
3. ZNSouq platform rules are minimums. If a store page conflicts with a platform rule, the platform rule wins: say so clearly.
4. When a rule depends on a date (e.g. fee changes), compare it with today's date.
5. When a passage contains a table, find the row that exactly matches the question (e.g. 3 kg fits "up to 5 kg", not "up to 1 kg") and copy its numbers exactly. Work this out before writing; never correct yourself mid-answer.
6. If passages describe different steps or waiting times, explain them in order ("first..., then...") instead of picking one.
7. Cite the passages you used like [1] or [2][3] right after the relevant sentence.
8. Style: write like a friendly support agent in a chat. Give a complete but compact answer: include every condition, fee, limit or exception from the passages that changes the answer, and skip unrelated details. Use plain prose; use a short list only for 3 or more steps or options. No headings. No emojis. Use EGP for money."""

CONTACT = {"buyer": "00001 (demo number) or help@znsouq.example",
           "seller": "00002 (demo number) or sellers@znsouq.example"}


def format_context(hits):
    blocks = []
    for i, h in enumerate(hits, 1):
        m = h["metadata"]
        blocks.append(f"[{i}] (source: {m['source']} › {m['section']})\n{h['text']}")
    return "\n\n".join(blocks)


# ---------- 5. Ask Claude ----------
def answer(question: str, mode: str = "buyer", k: int = 4, history=None):
    hits, seller_id, search_query = gather_context(question, mode, k, history)
    system = SYSTEM.format(audience="buyers" if mode == "buyer" else "sellers",
                           today=date.today().isoformat(), contact=CONTACT[mode])
    user = f"<context>\n{format_context(hits)}\n</context>\n\n"
    if history:
        # Give Claude the recent conversation so follow-ups like "and for women's fashion?" make sense
        convo = "\n".join(f"{m['role']}: {m['content'][:400]}" for m in history[-4:])
        user += (f"<conversation>\n{convo}\n</conversation>\n\n"
                 f"Latest question: {question}\n(Standalone version: {search_query})")
    else:
        user += f"Question: {question}"
    response = client().messages.create(
        model=MODEL,
        max_tokens=3000,
        thinking={"type": "enabled", "budget_tokens": 1500},   # private reasoning before answering
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    # With thinking on, the reply has a "thinking" block first and the answer in a "text" block
    text = "".join(b.text for b in response.content if b.type == "text")
    return {"answer": text, "sources": hits,
            "seller_id": seller_id, "search_query": search_query}

"""Answer a question: rewrite query → detect store → retrieve → ask Claude with grounding rules."""
import json
import os
import re
from datetime import date

import anthropic
from dotenv import load_dotenv

from rag.loader import DATA_DIR
from rag.retrieve import retrieve
from rag.catalog import hybrid_search, reviews_for
from rag.orders import ORDER_TOOL, lookup_order

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


# ---------- 2. Query rewriting + routing ----------
REWRITE_PROMPT = """You prepare searches for ZNSouq's {audience} support assistant.

1. Rewrite the user's latest message as one standalone search query.
- Keep every specific word from the message (products, categories, store names, numbers, dates), then ADD the words a help article would use (e.g. "get paid" for a seller -> "get paid seller payout schedule"; "stale coffee" -> "stale coffee grocery return").
- If earlier messages are given, resolve references like "it", "that" or "and for X?".

2. Choose which knowledge sources are needed (one or more):
- "policies": rules, fees, delivery, returns, refunds, payments, accounts, sellers' store policies
- "products": a specific product's details, price, sellers offering it, what's in the box, warranty, stock
- "reviews": what customers say or think about a product, its quality or rating

Reply with JSON only: {{"query": "...", "sources": ["policies"]}}

{history}Latest message: {question}"""

ALL_SOURCES = {"policies", "products", "reviews"}


def rewrite_query(question: str, mode: str = "buyer", history=None):
    """Use Claude to (1) turn the question into a clear search query and (2) pick the sources to search."""
    hist = ""
    if history:
        lines = [f"{m['role']}: {m['content'][:300]}" for m in history[-4:]]   # last 4 messages is enough
        hist = "Earlier messages:\n" + "\n".join(lines) + "\n\n"
    msg = client().messages.create(
        model=MODEL,
        max_tokens=150,
        messages=[{"role": "user", "content": REWRITE_PROMPT.format(
            audience="buyer" if mode == "buyer" else "seller", history=hist, question=question)}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text").strip()
    try:
        data = json.loads(re.search(r"\{.*\}", text, re.DOTALL).group(0))
        query = str(data.get("query") or question)
        sources = [s for s in data.get("sources", []) if s in ALL_SOURCES] or ["policies"]
    except (AttributeError, json.JSONDecodeError):
        query, sources = text or question, ["policies"]     # if the JSON is broken, fall back safely
    return query, sources


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
    """Route the question, then retrieve from the chosen sources:
    policies (platform docs + the store's page if a store is named), products, reviews."""
    search_query, sources = rewrite_query(question, mode, history)
    hits, seller_id = [], None
    if "policies" in sources:
        hits = search(question, search_query, k, platform_filter(mode))
        seller_id = detect_seller(question + " " + search_query) if mode == "buyer" else None
        if seller_id:
            hits = search(question, search_query, 3, {"seller_id": seller_id}, extra=1) + hits
    if "products" in sources or "reviews" in sources:
        product_hits = hybrid_search(question, search_query, k=4, types=["product"])
        if "products" in sources:
            hits += product_hits
        if "reviews" in sources and product_hits:
            # step 2: reviews of the best-matching product, looked up by its product_id
            hits += reviews_for(product_hits[0]["metadata"]["product_id"])
    return hits, seller_id, search_query, sources


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
7. Product passages list every seller's offer: when asked about price or sellers, compare all offers and mention stock and condition. Review passages are customer opinions: summarize the common points (good and bad) with the average rating and number of reviews, never present one opinion as a fact, and never invent reviews. If a product isn't in the passages, say you couldn't find it.
8. Cite the passages you used like [1] or [2][3] right after the relevant sentence.
9. Orders: if the customer asks about a specific order, call the lookup_order tool with the order number (format ZN-12345678). If they didn't give an order number, ask for it. Report only what the tool returns and never guess an order's status. If the order is late, add what the passages say they can do (for example a ZNSouq Guarantee claim).
10. Style: write like a friendly support agent in a chat. Give a complete but compact answer: include every condition, fee, limit or exception from the passages that changes the answer, and skip unrelated details. Use plain prose; use a short list only for 3 or more steps or options. No headings. No emojis. Use EGP for money."""

CONTACT = {"buyer": "00001 (demo number) or help@znsouq.example",
           "seller": "00002 (demo number) or sellers@znsouq.example"}


def format_context(hits):
    blocks = []
    for i, h in enumerate(hits, 1):
        m = h["metadata"]
        blocks.append(f"[{i}] (source: {m['source']} › {m['section']})\n{h['text']}")
    return "\n\n".join(blocks)


# ---------- 5. Ask Claude ----------
def answer(question: str, mode: str = "buyer", k: int = 4, history=None, customer_id=None):
    hits, seller_id, search_query, sources = gather_context(question, mode, k, history)
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

    messages = [{"role": "user", "content": user}]
    tools = [ORDER_TOOL] if mode == "buyer" else []      # only buyers have orders
    tool_calls = []
    for _ in range(3):                                   # at most 3 rounds of tool use
        request = dict(model=MODEL, max_tokens=3000, system=system, messages=messages,
                       thinking={"type": "enabled", "budget_tokens": 1500})   # private reasoning
        if tools:
            request["tools"] = tools
        response = client().messages.create(**request)
        if response.stop_reason != "tool_use":
            break                                        # Claude has its final answer
        # Claude asked to use a tool: run it, then send the result back in a new message
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "lookup_order":
                output = lookup_order(block.input.get("order_id", ""), customer_id)
                tool_calls.append({"tool": block.name, "input": block.input, "output": output})
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(output)})
        messages.append({"role": "user", "content": results})

    # With thinking on, the reply has "thinking" blocks first and the answer in "text" blocks
    text = "".join(b.text for b in response.content if b.type == "text")
    return {"answer": text or "Sorry, I couldn't complete that request. Please try again.",
            "sources": hits, "seller_id": seller_id, "search_query": search_query,
            "routes": sources, "tool_calls": tool_calls}

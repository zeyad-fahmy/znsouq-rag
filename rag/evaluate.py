"""Run the eval set: answer each question, check retrieval, and let Claude grade the answer.
Run from the project root:  python -m rag.evaluate"""
import json
import os
import re
from collections import defaultdict
from datetime import datetime

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import anthropic

from datetime import date

from rag.answer import CONTACT, MODEL, answer, format_context
from rag.loader import DATA_DIR

# Nothing is skipped any more: order questions use the lookup_order tool
SKIP_TYPES = set()

JUDGE_PROMPT = """You are grading a customer-support chatbot for a fictional marketplace.

Question: {question}

Expected answer (must include these facts): {expected}

Optional extra details (NOT required; never FAIL an answer for leaving these out): {nice}

What the chatbot was given (its only allowed knowledge):
- From its instructions: today's date is {today}; customer service contact is {contact}.
- Passages and tool results:
<passages>
{passages}
</passages>

Chatbot answer: {answer}

Grade the chatbot answer:
- PASS if it gives the must-include facts correctly and states nothing that contradicts the expected answer, the optional details or the passages.
- FAIL if a must-include fact is missing or wrong, or it states something that is not supported by the passages (invented).
Extra details are fine when the passages support them. Judge ONLY by the expected answer and the passages: do not use your own knowledge of how marketplaces usually work. Wording does not matter.

Reply with JSON only, no code fences: {{"verdict": "PASS" or "FAIL", "reason": "<one sentence, at most 25 words>"}}"""

client = anthropic.Anthropic()
# The grader can be a different (stronger) model than the bot. Set JUDGE_MODEL in .env; defaults to the bot's model.
JUDGE_MODEL = os.getenv("JUDGE_MODEL", MODEL)


def judge(question, expected, bot_answer, nice="", passages="", mode="buyer"):
    msg = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            question=question, expected=expected, nice=nice or "(none)",
            passages=passages[:12000] or "(none)", today=date.today().isoformat(),
            contact=CONTACT[mode], answer=bot_answer)}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")   # skip thinking blocks
    match = re.search(r"\{.*\}", text, re.DOTALL)        # find the JSON even if extra text appears
    try:
        return json.loads(match.group(0))
    except (AttributeError, json.JSONDecodeError):
        return {"verdict": "FAIL", "reason": f"Could not parse judge output: {text[:100]}"}


def retrieval_hit(expected_sources, hits):
    """True if at least one expected source document was retrieved."""
    if not expected_sources:
        return None                                       # nothing to retrieve (out-of-scope questions)
    retrieved = [h["metadata"]["source"] for h in hits]
    return any(r.startswith(e) for e in expected_sources for r in retrieved)   # exact doc (or product) match


def main():
    questions = [json.loads(line) for line in (DATA_DIR / "eval" / "questions.jsonl").open(encoding="utf-8")]
    questions = [q for q in questions if q["type"] not in SKIP_TYPES]
    print(f"Bot model: {MODEL}  |  Judge model: {JUDGE_MODEL}\n")
    results = []
    for q in questions:
        mode = "seller" if q["audience"] == "seller" else "buyer"
        r = answer(q["question"], mode=mode, customer_id=q.get("customer_id"))   # eval "logs in" as that customer
        passages = format_context(r["sources"])
        if r.get("tool_calls"):                          # tool results are allowed knowledge too
            passages += "\n\nTool results:\n" + "\n".join(json.dumps(t["output"]) for t in r["tool_calls"])
        grade = judge(q["question"], q["expected_answer"], r["answer"], q.get("nice_to_have", ""), passages, mode)
        hit = retrieval_hit(q["sources"], r["sources"])
        results.append({**q, "mode": mode, "bot_answer": r["answer"], "retrieval_hit": hit,
                        "search_query": r.get("search_query"), "routes": r.get("routes"),
                        "tool_calls": r.get("tool_calls"),
                        "retrieved": [h["metadata"]["source"] for h in r["sources"]], **grade})
        mark = "✅" if grade["verdict"] == "PASS" else "❌"
        print(f"{mark} {q['id']} [{q['type']}] {q['question'][:70]}")
        if grade["verdict"] != "PASS":
            print(f"     ↳ {grade['reason']}  | retrieval hit: {hit}")
            print(f"     ↳ search query used: {r.get('search_query')}  | routes: {r.get('routes')}")

    # ---- Summary
    passed = sum(r["verdict"] == "PASS" for r in results)
    print(f"\nAnswer accuracy: {passed}/{len(results)} = {passed / len(results):.0%}")
    hits = [r["retrieval_hit"] for r in results if r["retrieval_hit"] is not None]
    print(f"Retrieval hit rate: {sum(hits)}/{len(hits)} = {sum(hits) / len(hits):.0%}")
    by_type = defaultdict(lambda: [0, 0])
    for r in results:
        by_type[r["type"]][0] += r["verdict"] == "PASS"
        by_type[r["type"]][1] += 1
    print("\nBy question type:")
    for t, (p, n) in sorted(by_type.items()):
        print(f"  {t:<16} {p}/{n}")

    os.makedirs("eval_results", exist_ok=True)
    out = f"eval_results/run_{datetime.now():%Y%m%d_%H%M}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nFull results saved to {out}")


if __name__ == "__main__":
    main()

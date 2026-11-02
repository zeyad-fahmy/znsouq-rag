"""Run the eval set: answer each question, check retrieval, and let Claude grade the answer.
Run from the project root:  python -m rag.evaluate"""
import json
import os
import re
from collections import defaultdict
from datetime import datetime

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import anthropic

from rag.answer import MODEL, answer
from rag.loader import DATA_DIR

# Types we can answer with the current index (products/reviews come in step 7, orders in step 9)
SKIP_TYPES = {"product", "reviews", "needs_tool"}

JUDGE_PROMPT = """You are grading a customer-support chatbot for a fictional marketplace.

Question: {question}

Expected answer (ground truth): {expected}

Chatbot answer: {answer}

Grade the chatbot answer:
- PASS if it gives the key facts of the expected answer correctly and states nothing that contradicts it.
- FAIL if a key fact is missing or wrong, or it invents facts not supported by the expected answer.
Extra correct detail is fine. Wording does not matter.

Reply with JSON only: {{"verdict": "PASS" or "FAIL", "reason": "<one short sentence>"}}"""

client = anthropic.Anthropic()


def judge(question, expected, bot_answer):
    msg = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            question=question, expected=expected, answer=bot_answer)}],
    )
    text = msg.content[0].text
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
    return any(r.startswith(e.split("#")[0]) for e in expected_sources for r in retrieved)


def main():
    questions = [json.loads(line) for line in (DATA_DIR / "eval" / "questions.jsonl").open(encoding="utf-8")]
    questions = [q for q in questions if q["type"] not in SKIP_TYPES]
    results = []
    for q in questions:
        mode = "seller" if q["audience"] == "seller" else "buyer"
        r = answer(q["question"], mode=mode)
        grade = judge(q["question"], q["expected_answer"], r["answer"])
        hit = retrieval_hit(q["sources"], r["sources"])
        results.append({**q, "mode": mode, "bot_answer": r["answer"], "retrieval_hit": hit,
                        "retrieved": [h["metadata"]["source"] for h in r["sources"]], **grade})
        mark = "✅" if grade["verdict"] == "PASS" else "❌"
        print(f"{mark} {q['id']} [{q['type']}] {q['question'][:70]}")
        if grade["verdict"] != "PASS":
            print(f"     ↳ {grade['reason']}  | retrieval hit: {hit}")

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
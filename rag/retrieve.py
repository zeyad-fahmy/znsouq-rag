"""Retrieve the most relevant chunks for a question."""
from rag.index import get_collection

# bge models work best when the QUESTION (not the documents) gets this instruction prefix
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_collection = None


def collection():
    """Open the Chroma collection once and reuse it (loading the model is slow)."""
    global _collection
    if _collection is None:
        _collection = get_collection()
    return _collection


def retrieve(question: str, k: int = 4, where: dict | None = None):
    """Return the k most similar chunks, optionally filtered by metadata."""
    res = collection().query(
        query_texts=[QUERY_PREFIX + question],
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"text": text, "metadata": meta, "score": round(1 - dist, 3)})
    return hits


def show(hits, chars: int = 200):
    """Print hits in a readable way (for notebooks)."""
    for i, h in enumerate(hits, 1):
        m = h["metadata"]
        print(f"#{i}  score={h['score']}  {m['source']}  ›  {m['section']}")
        print("    " + h["text"][:chars].replace("\n", " ") + "\n")
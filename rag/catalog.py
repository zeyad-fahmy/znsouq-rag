"""Products + reviews: turn catalog data into text chunks, index them, and search them with
HYBRID search (vector similarity + BM25 keyword matching).

Build the catalog index once (takes ~5-15 minutes on a laptop CPU):
    python -m rag.catalog
"""
import json
import re
from collections import defaultdict

from rank_bm25 import BM25Okapi

from rag.index import get_collection
from rag.loader import DATA_DIR
from rag.retrieve import QUERY_PREFIX

CATALOG_COLLECTION = "znsouq_catalog_bge_small"
REVIEWS_PER_CHUNK = 8
CAT_DIR = DATA_DIR / "catalog"


# ---------- 1. Load the raw data ----------
def load_jsonl(name):
    with (CAT_DIR / name).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def load_sellers():
    sellers = json.loads((CAT_DIR / "sellers.json").read_text(encoding="utf-8"))
    return {s["seller_id"]: s["store_name"] for s in sellers}


# ---------- 2. Structured data -> readable text ----------
def offer_line(o, store_names):
    store = store_names.get(o["seller_id"], o["seller_id"])
    shipped = "fulfilled by ZNSouq (FBZ)" if o["fulfillment"] == "FBZ" else "shipped by the seller"
    stock = "out of stock" if o["stock"] == 0 else f"{o['stock']} in stock"
    extra = f", {o['seller_warranty_months']}-month store warranty" if o["seller_warranty_months"] else ""
    return (f"- {store} ({o['seller_id']}): {o['price']:,} EGP, {o['condition']}, {shipped}, {stock}{extra}")


def product_to_text(p, store_names):
    attrs = ", ".join(f"{v}" for v in p["attributes"].values())
    warranty = (f"{p['warranty']['type']}, {p['warranty']['months']} months"
                if p["warranty"]["months"] else "No warranty")
    rating = (f"{p['rating']} out of 5 from {p['review_count']} reviews" if p["review_count"] else "No reviews yet")
    lines = [
        f"Product: {p['title']} (product ID {p['product_id']})",
        f"Category: {p['category']} | Type: {p['product_type']} | Brand: {p['brand']} | Options: {attrs}",
        f"Description: {p['description']}",
        "Features: " + "; ".join(p["features"]),
        f"In the box: {p['in_the_box']}",
        f"Warranty: {warranty}",
        f"Customer rating: {rating}",
        f"Offers ({len(p['offers'])} seller{'s' if len(p['offers']) > 1 else ''}):",
    ] + [offer_line(o, store_names) for o in p["offers"]]
    if p["large_bulky_delivery"]:
        lines.append("Delivery: large/bulky item (fixed large-item delivery fee applies).")
    return "\n".join(lines)


def reviews_to_chunks(p, reviews):
    """Group a product's reviews into chunks of up to REVIEWS_PER_CHUNK (most helpful first)."""
    reviews = sorted(reviews, key=lambda r: -r["helpful_votes"])
    chunks = []
    for start in range(0, len(reviews), REVIEWS_PER_CHUNK):
        group = reviews[start:start + REVIEWS_PER_CHUNK]
        header = (f"Customer reviews for {p['title']} (product ID {p['product_id']}). "
                  f"Average rating {p['rating']} out of 5 from {p['review_count']} reviews.")
        body = "\n".join(f"- {r['rating']}/5 \"{r['title']}\": {r['body']}" for r in group)
        chunks.append((header + "\n" + body, start // REVIEWS_PER_CHUNK))
    return chunks


def build_catalog_chunks():
    store_names = load_sellers()
    products = load_jsonl("products.jsonl")
    by_product = defaultdict(list)
    for r in load_jsonl("reviews.jsonl"):
        by_product[r["product_id"]].append(r)

    chunks = []
    for p in products:
        base_meta = {"product_id": p["product_id"], "category": p["category"], "brand": p["brand"],
                     "title": p["title"], "audience": "buyer"}
        chunks.append({"id": f"product#{p['product_id']}", "text": product_to_text(p, store_names),
                       "metadata": {**base_meta, "type": "product", "section": "Product details", "part": 0,
                                    "source": f"catalog/products.jsonl#{p['product_id']}"}})
        for text, part in reviews_to_chunks(p, by_product.get(p["product_id"], [])):
            chunks.append({"id": f"reviews#{p['product_id']}#{part}", "text": text,
                           "metadata": {**base_meta, "type": "reviews", "section": "Customer reviews", "part": part,
                                        "source": f"catalog/reviews.jsonl#{p['product_id']}"}})
    return chunks


# ---------- 3. Build the vector index ----------
def build_catalog_index(batch_size=500):
    chunks = build_catalog_chunks()
    col = get_collection(CATALOG_COLLECTION)
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        col.upsert(ids=[c["id"] for c in batch], documents=[c["text"] for c in batch],
                   metadatas=[c["metadata"] for c in batch])
        print(f"  indexed {min(i + batch_size, len(chunks)):,} / {len(chunks):,}")
    print(f"Indexed {col.count():,} catalog chunks into '{CATALOG_COLLECTION}'")


# ---------- 4. Keyword search (BM25) ----------
def tokenize(text):
    """Lowercase words; keep codes like 'ze-518' and 'znp-ele-00042' together."""
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


_bm25 = None
_bm25_chunks = None


def bm25_index():
    """Build the BM25 keyword index in memory once (a few seconds)."""
    global _bm25, _bm25_chunks
    if _bm25 is None:
        _bm25_chunks = build_catalog_chunks()
        _bm25 = BM25Okapi([tokenize(c["text"]) for c in _bm25_chunks])
    return _bm25, _bm25_chunks


def keyword_search(query, n=20, types=None):
    bm25, chunks = bm25_index()
    scores = bm25.get_scores(tokenize(query))
    ranked = sorted(range(len(scores)), key=lambda i: -scores[i])
    out = []
    for i in ranked:
        if scores[i] <= 0 or len(out) >= n:
            break
        if types is None or chunks[i]["metadata"]["type"] in types:
            out.append(chunks[i])
    return out


# ---------- 5. Vector search ----------
_catalog_col = None


def vector_search(query, n=20, types=None):
    global _catalog_col
    if _catalog_col is None:
        _catalog_col = get_collection(CATALOG_COLLECTION)
    where = {"type": {"$in": list(types)}} if types else None
    res = _catalog_col.query(query_texts=[QUERY_PREFIX + query], n_results=n, where=where,
                             include=["documents", "metadatas"])
    return [{"id": i, "text": t, "metadata": m}
            for i, t, m in zip(res["ids"][0], res["documents"][0], res["metadatas"][0])]


# ---------- 6. Hybrid = combine both rankings (Reciprocal Rank Fusion) ----------
def fuse(query, types=None, rrf_k=60):
    """Vector search and keyword search each vote: a chunk at rank r gets 1 / (rrf_k + r).
    Chunks near the top of BOTH lists get the most votes."""
    votes, found = defaultdict(float), {}
    for results in (vector_search(query, types=types), keyword_search(query, types=types)):
        for rank, c in enumerate(results, 1):
            votes[c["id"]] += 1 / (rrf_k + rank)
            found[c["id"]] = c
    ranked = sorted(votes, key=lambda cid: -votes[cid])
    return [{"text": found[cid]["text"], "metadata": found[cid]["metadata"], "score": round(votes[cid], 4)}
            for cid in ranked]


def hybrid_search(question, search_query=None, k=4, types=None, extra=1):
    """Same rule as for policies: keep the original question's top-k,
    then let the rewritten query ADD up to `extra` new chunks."""
    hits = fuse(question, types)[:k]
    seen = {(h["metadata"]["source"], h["metadata"]["part"]) for h in hits}
    if search_query and search_query.strip().lower() != question.strip().lower():
        for h in fuse(search_query, types):
            if len(hits) >= k + extra:
                break
            key = (h["metadata"]["source"], h["metadata"]["part"])
            if key not in seen:
                hits.append(h)
                seen.add(key)
    return hits


def reviews_for(product_id, max_chunks=3):
    """Two-step retrieval: once we know WHICH product, fetch its reviews directly by product_id
    (an exact metadata lookup), instead of hoping a search finds the right review chunks."""
    _, chunks = bm25_index()
    found = [c for c in chunks if c["metadata"]["type"] == "reviews" and c["metadata"]["product_id"] == product_id]
    return [{"text": c["text"], "metadata": c["metadata"], "score": "by product ID"} for c in found[:max_chunks]]


if __name__ == "__main__":
    build_catalog_index()

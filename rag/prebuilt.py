"""Ship the indexes WITHOUT re-embedding on the server.

Locally (once, after building the indexes):
    python -m rag.prebuilt export     -> writes data/embeddings/docs.npz and catalog.npz (~10 MB)

On the server (automatic, called by app.py at start-up):
    ensure_indexes()  -> if Chroma is empty, loads the saved vectors in seconds
                         instead of embedding 11,000+ chunks again (which takes minutes).
"""
import sys

import numpy as np

from rag.catalog import CATALOG_COLLECTION, build_catalog_chunks, build_catalog_index
from rag.index import COLLECTION, build_index, get_collection
from rag.loader import DATA_DIR, load_chunks

EMB_DIR = DATA_DIR / "embeddings"


def doc_chunks():
    """Help-center chunks with the same IDs index.py uses."""
    chunks = load_chunks()
    for c in chunks:
        m = c["metadata"]
        c["id"] = f"{m['source']}#{m['section']}#{m['part']}"
    return chunks


def export():
    """Save every stored vector (as compact float16) together with its chunk ID."""
    EMB_DIR.mkdir(parents=True, exist_ok=True)
    for name, collection in (("docs", COLLECTION), ("catalog", CATALOG_COLLECTION)):
        data = get_collection(collection).get(include=["embeddings"])
        vectors = np.asarray(data["embeddings"], dtype=np.float16)
        np.savez_compressed(EMB_DIR / f"{name}.npz", ids=np.array(data["ids"]), vectors=vectors)
        print(f"Saved {len(data['ids']):,} vectors from '{collection}' -> data/embeddings/{name}.npz")


def load_from_file(name, collection, chunks, batch_size=1000):
    """Fill an empty collection from the saved vectors. Returns False if the file doesn't match the data."""
    path = EMB_DIR / f"{name}.npz"
    if not path.exists():
        return False
    saved = np.load(path)
    by_id = {c["id"]: c for c in chunks}
    ids = [str(i) for i in saved["ids"]]
    if set(ids) != set(by_id):                    # data changed since export -> vectors are stale
        print(f"{path.name} doesn't match the current data; re-embedding instead.")
        return False
    col = get_collection(collection)
    vectors = saved["vectors"].astype(np.float32)
    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        col.upsert(ids=batch,
                   embeddings=vectors[i:i + batch_size],
                   documents=[by_id[x]["text"] for x in batch],
                   metadatas=[by_id[x]["metadata"] for x in batch])
    print(f"Loaded {col.count():,} vectors into '{collection}' from {path.name}")
    return True


def ensure_indexes():
    """Make sure both collections exist and are filled (fast path: saved vectors)."""
    if get_collection(COLLECTION).count() == 0:
        if not load_from_file("docs", COLLECTION, doc_chunks()):
            build_index()                         # slow path: embed from scratch
    if get_collection(CATALOG_COLLECTION).count() == 0:
        if not load_from_file("catalog", CATALOG_COLLECTION, build_catalog_chunks()):
            build_catalog_index()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export()
    else:
        ensure_indexes()

"""Embed chunks and store them in a local Chroma database."""
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from rag.loader import load_chunks

DB_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"      # 384 dimensions, runs locally, free
COLLECTION = "znsouq_docs_bge_small"       # named after the model (one model per index!)


def get_collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},   # use cosine similarity
    )


def build_index():
    chunks = load_chunks()
    col = get_collection()
    ids = [f"{c['metadata']['source']}#{c['metadata']['section']}#{c['metadata']['part']}" for c in chunks]
    col.upsert(                                 # upsert = insert, or update if the id exists
        ids=ids,
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    print(f"Indexed {col.count()} chunks into '{COLLECTION}' at {DB_DIR}")


if __name__ == "__main__":
    build_index()
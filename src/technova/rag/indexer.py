from pathlib import Path

from langchain_community.vectorstores import FAISS

from technova.rag.chunker import split_documents
from technova.rag.embedder import get_embeddings
from technova.rag.loader import load_documents

INDEX_DIR = Path(__file__).resolve().parents[3] / "data" / "faiss_index"


def build_index() -> FAISS:
    chunks = split_documents(load_documents())
    vector_store = FAISS.from_documents(chunks, get_embeddings())
    vector_store.save_local(str(INDEX_DIR))
    return vector_store


if __name__ == "__main__":
    store = build_index()
    print(f"Indexed {store.index.ntotal} chunks into {INDEX_DIR}")
import sys

from langchain_community.vectorstores import FAISS

from technova.rag.embedder import get_embeddings
from technova.rag.indexer import INDEX_DIR
from functools import lru_cache


@lru_cache(maxsize=1)
def load_index() -> FAISS:
    return FAISS.load_local(
        str(INDEX_DIR),
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )


def search(query: str, k: int = 3):
    store = load_index()
    return store.similarity_search_with_score(query, k=k)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "How many sick leave days do I get?"
    print(f"Question: {query}\n")
    for doc, score in search(query):
        preview = doc.page_content.replace("\n", " ")
        print(f"[{score:.3f}] {doc.metadata['source']}")
        print(f"         {preview}...\n")
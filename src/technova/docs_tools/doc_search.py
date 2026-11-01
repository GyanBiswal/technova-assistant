import sys

from technova.rag.retriever import load_index


def search_documents(query: str, max_docs: int = 3, k: int = 10) -> list[dict]:
    store = load_index()
    results = store.similarity_search_with_score(query, k=k)

    best_per_file = {}
    for doc, score in results:
        source = doc.metadata["source"]
        if source not in best_per_file or score < best_per_file[source]["score"]:
            best_per_file[source] = {
                "source": source,
                "score": float(score),
                "snippet": doc.page_content.replace("\n", " ")[:120],
            }

    ranked = sorted(best_per_file.values(), key=lambda item: item["score"])
    return ranked[:max_docs]


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "work from home"
    print(f"Search: {query}\n")
    for item in search_documents(query):
        print(f"[{item['score']:.3f}] {item['source']}")
        print(f"         {item['snippet']}...\n")
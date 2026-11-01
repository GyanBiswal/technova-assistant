import sys

from technova.llm.groq_client import get_llm
from technova.rag.retriever import load_index

SYSTEM_PROMPT = """You are the internal knowledge assistant for TechNova Solutions.
Answer the question using ONLY the context provided below.
If the context does not contain the answer, reply with exactly this sentence and nothing else (no Sources line): I couldn't find that in the company documents.
Never use outside knowledge. Keep the answer short and factual.
Otherwise, end with a line in this format: Sources: file1.md, file2.md (only files you actually used)."""


def format_context(docs) -> str:
    return "\n\n".join(
        f"[Source: {doc.metadata['source']}]\n{doc.page_content}" for doc in docs
    )


def answer_question(question: str, k: int = 3) -> dict:
    store = load_index()
    docs = store.similarity_search(question, k=k)
    context = format_context(docs)

    llm = get_llm()
    response = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", f"Context:\n{context}\n\nQuestion: {question}"),
        ]
    )
    return {
        "answer": response.content,
        "retrieved_sources": sorted({doc.metadata["source"] for doc in docs}),
    }


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How many sick leave days do I get?"
    result = answer_question(question)
    print(f"Question: {question}\n")
    print(result["answer"])
    print(f"\n(retrieved from: {', '.join(result['retrieved_sources'])})")
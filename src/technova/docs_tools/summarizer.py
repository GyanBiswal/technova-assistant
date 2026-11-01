import sys

from technova.llm.groq_client import get_llm
from technova.rag.loader import DOCS_DIR

SUMMARY_PROMPT = """You summarize TechNova Solutions company documents.
Summarize the document in 3 to 5 short bullet points.
Use only information from the document. Keep all numbers, dates, and limits exactly as written.
Do not add anything that is not in the document."""


def list_document_names() -> list[str]:
    return sorted(path.name for path in DOCS_DIR.glob("*.md"))


def read_document(name: str) -> str:
    available = list_document_names()
    if name not in available:
        raise ValueError(f"Unknown document: {name}. Available: {', '.join(available)}")
    return (DOCS_DIR / name).read_text(encoding="utf-8")


def summarize_document(name: str) -> str:
    text = read_document(name)
    response = get_llm().invoke(
        [
            ("system", SUMMARY_PROMPT),
            ("human", f"Document: {name}\n\n{text}"),
        ]
    )
    return response.content


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "leave_policy.md"
    try:
        print(summarize_document(name))
    except ValueError as error:
        print(error)
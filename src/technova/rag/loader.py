from pathlib import Path

from langchain_core.documents import Document

DOCS_DIR = Path(__file__).resolve().parents[3] / "data" / "documents"


def load_documents(docs_dir: Path = DOCS_DIR) -> list[Document]:
    documents = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        documents.append(Document(page_content=text, metadata={"source": path.name}))
    return documents


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    for doc in docs:
        print(f"- {doc.metadata['source']}: {len(doc.page_content)} characters")
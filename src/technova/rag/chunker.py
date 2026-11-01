from langchain_core.documents import Document
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

from technova.rag.loader import load_documents

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


if __name__ == "__main__":
    chunks = split_documents(load_documents())
    sizes = [len(chunk.page_content) for chunk in chunks]
    print(f"{len(chunks)} chunks created (smallest {min(sizes)}, largest {max(sizes)} characters)")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- chunk {i} | {chunk.metadata['source']} | {len(chunk.page_content)} chars ---")
        print(chunk.page_content)
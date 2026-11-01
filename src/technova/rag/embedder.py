from langchain_huggingface import HuggingFaceEmbeddings

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=MODEL_NAME)


if __name__ == "__main__":
    import numpy as np

    embeddings = get_embeddings()

    query = "How many sick days do I get?"
    candidates = [
        "Sick leave can be taken when an employee is unwell.",
        "NovaDesk is a customer support platform.",
    ]

    query_vector = np.array(embeddings.embed_query(query))
    print(f"Each embedding has {len(query_vector)} numbers")

    for text in candidates:
        vector = np.array(embeddings.embed_query(text))
        score = np.dot(query_vector, vector) / (
            np.linalg.norm(query_vector) * np.linalg.norm(vector)
        )
        print(f"{score:.2f}  {text}")
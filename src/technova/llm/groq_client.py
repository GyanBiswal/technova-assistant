from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"


def get_llm() -> ChatGroq:
    return ChatGroq(model=MODEL_NAME, temperature=0, max_retries=2)


if __name__ == "__main__":
    llm = get_llm()
    response = llm.invoke(
        [
            ("system", "You are a helpful assistant. Answer in one short sentence."),
            ("human", "What is TechNova Solutions?"),
        ]
    )
    print(response.content)
    print(response.response_metadata.get("token_usage"))
from technova.graph.state import State
from technova.llm.groq_client import get_llm
from technova.docs_tools.doc_search import search_documents
from technova.docs_tools.summarizer import summarize_document
from technova.rag.answerer import answer_question

ROUTES = ("knowledge", "summarize", "data")

ROUTER_PROMPT = """You route questions for the TechNova company assistant.
Reply with exactly one word, chosen from:
knowledge - questions about company policies, products, pricing, procedures, and the narrative of the Q3 sales report (targets, highlights, risks, plans)
summarize - requests to summarize or give an overview of a specific document
data - questions about company records: employees, managers, projects, tasks, and sales figures by region or product
Reply with only that one word."""


def classify(state: State) -> dict:
    response = get_llm().invoke(
        [("system", ROUTER_PROMPT), ("human", state["question"])]
    )
    answer = response.content.strip().lower()
    route = next((name for name in ROUTES if name in answer), "knowledge")
    return {"route": route}

def knowledge(state: State) -> dict:
    result = answer_question(state["question"])
    return {"answer": result["answer"], "sources": result["retrieved_sources"]}


def summarize(state: State) -> dict:
    matches = search_documents(state["question"], max_docs=1)
    if not matches:
        return {"answer": "I couldn't find a matching document.", "sources": []}
    name = matches[0]["source"]
    summary = summarize_document(name)
    return {"document": name, "answer": f"Summary of {name}:\n{summary}", "sources": [name]}


def data(state: State) -> dict:
    return {"answer": "[data route not built yet]", "sources": []}

if __name__ == "__main__":
    tests = [
        ("How many sick leave days do I get?", "knowledge"),
        ("Who is Sneha's manager?", "data"),
        ("What tasks does Karthik have?", "data"),
        ("Summarize the expense policy", "summarize"),
        ("Which region earned the most revenue in Q3?", "data"),
        ("What is the Q4 revenue target?", "knowledge"),
        ("What's the weather today?", "knowledge"),
    ]
    for question, expected in tests:
        route = classify({"question": question})["route"]
        flag = "ok " if route == expected else "DIFF"
        print(f"{flag} {route:<10} (expected {expected:<10}) {question}")
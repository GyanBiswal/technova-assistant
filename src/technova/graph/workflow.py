import sys

from langgraph.graph import END, START, StateGraph

from technova.graph.data_nodes import after_plan, plan_data_call, respond_data, run_data_call
from technova.graph.nodes import classify, knowledge, summarize
from technova.graph.state import State


def pick_route(state: State) -> str:
    return state["route"]


def build_graph():
    graph = StateGraph(State)
    graph.add_node("classify", classify)
    graph.add_node("knowledge", knowledge)
    graph.add_node("summarize", summarize)
    graph.add_node("plan_data_call", plan_data_call)
    graph.add_node("run_data_call", run_data_call)
    graph.add_node("respond_data", respond_data)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        pick_route,
        {"knowledge": "knowledge", "summarize": "summarize", "data": "plan_data_call"},
    )
    for node in ("knowledge", "summarize"):
        graph.add_edge(node, END)
    graph.add_conditional_edges(
        "plan_data_call", after_plan, {"run": "run_data_call", "end": END}
    )
    graph.add_edge("run_data_call", "respond_data")
    graph.add_edge("respond_data", END)
    return graph.compile()


app = build_graph()


def ask(question: str) -> State:
    return app.invoke({"question": question})


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How many sick leave days do I get?"
    result = ask(question)
    print(f"route: {result['route']}")
    print(result.get("answer", "(no answer was produced)"))
    print("sources:", result.get("sources", []))
import sys
from functools import lru_cache
from typing import Annotated, TypedDict

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from technova.graph.data_nodes import to_openai_tool
from technova.graph.tools import get_tool_schemas, run_tool
from technova.llm.groq_client import get_llm
from technova.mcp_client.client import ToolCallError, format_for_llm

MAX_STEPS = 5
MAX_CALLS_PER_STEP = 3
MAX_RESULT_CHARS = 4000
MAX_TOTAL_TOKENS = 6000

AGENT_PROMPT = """You are the TechNova internal assistant. Use the tools to answer.
You may call tools one after another when a question needs it, for example look up an employee, then use what you learned for a second lookup.
Rules:
- Policy, product and report questions: use search_knowledge and answer ONLY from the passages it returns.
- To summarize or give an overview of a document, call read_document (search_knowledge returns only fragments, so never use it for summaries) and cover every section of the document.
- Questions about employees, projects, tasks and sales figures: use the record tools and answer ONLY from their results.
- If the tools do not contain the answer, say you couldn't find it. Never guess or use outside knowledge.
- Keep answers short. Keep names, numbers and dates exactly as returned. Money: 1 lakh = 100,000 rupees.
- When you used documents, end with: Sources: file1.md, file2.md"""


class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    steps: int

def tokens_used(messages) -> int:
    return sum(
        (message.usage_metadata or {}).get("total_tokens", 0)
        for message in messages
        if isinstance(message, AIMessage)
    )

def build_agent():
    schemas = get_tool_schemas()
    allowed = {schema["name"] for schema in schemas}
    llm = get_llm().bind_tools([to_openai_tool(schema) for schema in schemas])

    def agent(state: AgentState) -> dict:
        response = llm.invoke([SystemMessage(content=AGENT_PROMPT), *state["messages"]])
        return {"messages": [response], "steps": state.get("steps", 0) + 1}

    def tools(state: AgentState) -> dict:
        results = []
        for index, call in enumerate(state["messages"][-1].tool_calls):
            if index >= MAX_CALLS_PER_STEP:
                results.append(
                    ToolMessage(
                        content="Skipped: too many tool calls at once.",
                        tool_call_id=call["id"],
                        status="error",
                    )
                )
                continue
            try:
                text = format_for_llm(run_tool(call["name"], call["args"], allowed))
                results.append(
                    ToolMessage(content=text[:MAX_RESULT_CHARS], tool_call_id=call["id"])
                )
            except ToolCallError as error:
                results.append(
                    ToolMessage(content=str(error), tool_call_id=call["id"], status="error")
                )
        return {"messages": results}

    def limit_reached(state: AgentState) -> dict:
        return {
            "messages": [
                AIMessage(content="I couldn't finish that within my step limit, so I'd rather not guess.")
            ]
        }

    def after_agent(state: AgentState) -> str:
        if not state["messages"][-1].tool_calls:
            return "end"
        if state["steps"] >= MAX_STEPS or tokens_used(state["messages"]) >= MAX_TOTAL_TOKENS:
            return "limit"
        return "tools"

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent)
    graph.add_node("tools", tools)
    graph.add_node("limit_reached", limit_reached)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent", after_agent, {"tools": "tools", "limit": "limit_reached", "end": END}
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("limit_reached", END)
    return graph.compile()


@lru_cache(maxsize=1)
def get_agent():
    return build_agent()


def ask_agent(question: str) -> dict:
    final = get_agent().invoke({"messages": [HumanMessage(content=question)]})
    messages = final["messages"]
    return {
        "answer": messages[-1].content,
        "steps": final.get("steps", 0),
        "tools_used": [
            call["name"]
            for message in messages
            if isinstance(message, AIMessage)
            for call in message.tool_calls
        ],
        "tokens": tokens_used(messages),
    }


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Who is Sneha's manager?"
    result = ask_agent(question)
    print(result["answer"])
    print(f"tools: {result['tools_used']} | steps: {result['steps']} | tokens: {result['tokens']}")
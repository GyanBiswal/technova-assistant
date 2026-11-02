import time

import anyio

from technova.graph.state import State
from technova.llm.groq_client import get_llm
from technova.mcp_client.client import (
    ToolCallError,
    call_tool,
    format_for_llm,
    list_tool_schemas,
)

PLANNER_PROMPT = """You look up TechNova company records by calling exactly one tool.
Choose the tool and arguments that best answer the user's question.
Use argument values exactly as the question gives them (names, regions, products).
If no tool can answer the question, do not call a tool."""

NO_TOOL_ANSWER = "I couldn't find a company-records lookup that answers that."


def to_openai_tool(schema: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": schema["name"],
            "description": schema["description"],
            "parameters": schema["input_schema"],
        },
    }


def plan_data_call(state: State) -> dict:
    schemas = anyio.run(list_tool_schemas)
    allowed = {schema["name"] for schema in schemas}

    llm = get_llm().bind_tools([to_openai_tool(schema) for schema in schemas])
    response = llm.invoke([("system", PLANNER_PROMPT), ("human", state["question"])])

    if not response.tool_calls or response.tool_calls[0]["name"] not in allowed:
        return {"answer": NO_TOOL_ANSWER, "sources": []}

    call = response.tool_calls[0]
    return {"tool_call": {"name": call["name"], "args": call["args"]}}


RESPONDER_PROMPT = """You answer questions about TechNova company records.
Use ONLY the tool result provided. Keep names, figures and dates exactly as given.
If the result is empty, say no matching record was found.
If the result does not contain what was asked, say so plainly instead of guessing.
Money amounts: state the unit clearly (1 lakh = 100,000 rupees).
Keep the answer short."""


def after_plan(state: State) -> str:
    return "run" if "tool_call" in state else "end"


def run_data_call(state: State) -> dict:
    call = state["tool_call"]
    try:
        data = anyio.run(call_tool, call["name"], call["args"])
    except ToolCallError as error:
        return {"error": str(error)}
    return {"tool_result": format_for_llm(data)}


def respond_data(state: State) -> dict:
    tool = state["tool_call"]["name"]
    sources = [f"database: {tool}"]
    if "error" in state:
        return {
            "answer": "The data lookup was rejected, so I can't answer that right now.",
            "sources": sources,
        }
    response = get_llm().invoke(
        [
            ("system", RESPONDER_PROMPT),
            (
                "human",
                f"Question: {state['question']}\n\n"
                f"Tool: {tool}\nTool result (JSON): {state['tool_result']}",
            ),
        ]
    )
    return {"answer": response.content, "sources": sources}

if __name__ == "__main__":
    tests = [
        "Who is Sneha's manager?",
        "What tasks does Karthik have?",
        "Which tasks are overdue?",
        "What were South region NovaInsight sales?",
        "What's the status of Project Atlas?",
        "How many leave days does Priya have left?",
    ]
    for question in tests:
        result = plan_data_call({"question": question})
        print(f"{question}\n   -> {result.get('tool_call') or result['answer']}")
        time.sleep(8)
import sys
from pathlib import Path

import anyio
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
import time
from contextlib import asynccontextmanager
import json

SRC_DIR = Path(__file__).resolve().parents[2]


def server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "technova.mcp_server.server"],
        env={"PYTHONPATH": str(SRC_DIR)},
    )


class ToolCallError(Exception):
    """Raised when the MCP server reports that a tool call failed."""


@asynccontextmanager
async def connect():
    async with Client(stdio_client(server_params())) as client:
        yield client


async def list_tool_schemas() -> list[dict]:
    async with connect() as client:
        result = await client.list_tools()
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
        }
        for tool in result.tools
    ]


async def call_tool(name: str, arguments: dict | None = None):
    async with connect() as client:
        result = await client.call_tool(name, arguments or {})
    if result.is_error:
        raise ToolCallError(result.content[0].text)
    data = result.structured_content
    if data is None:
        return result.content[0].text
    if set(data) == {"result"}:
        return data["result"]
    return data


def format_for_llm(data) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

async def main() -> None:
    schemas = await list_tool_schemas()
    print([schema["name"] for schema in schemas])

    start = time.perf_counter()
    employees = await call_tool("find_employee", {"name": "Sneha"})
    print(employees[0]["name"], "| manager:", employees[0]["manager"])
    print(f"one call took {time.perf_counter() - start:.2f}s")

    sales = await call_tool("get_sales_summary", {"region": "East"})
    print("East revenue (lakh):", sales["total_lakh"])

    try:
        await call_tool("get_tasks", {"status": "Blocked"})
    except ToolCallError as error:
        print("Tool error:", str(error).splitlines()[0])

if __name__ == "__main__":
    anyio.run(main)
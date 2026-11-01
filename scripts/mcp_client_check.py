import anyio

from technova.mcp_client.client import (
    ToolCallError,
    call_tool,
    format_for_llm,
    list_tool_schemas,
)


async def main() -> None:
    schemas = await list_tool_schemas()
    names = sorted(schema["name"] for schema in schemas)
    assert names == ["find_employee", "get_project_status", "get_sales_summary", "get_tasks"], names
    assert all(schema["description"] and schema["input_schema"] for schema in schemas), schemas

    employees = await call_tool("find_employee", {"name": "Tara"})
    assert employees[0]["manager"] == "Rohan Iyer", employees

    atlas = await call_tool("get_project_status", {"name": "Atlas"})
    assert atlas[0]["lead"] == "Rohan Iyer", atlas

    sales = await call_tool("get_sales_summary", {})
    assert sales["total_lakh"] == 230.0, sales

    try:
        await call_tool("get_tasks", {"status": "Blocked"})
    except ToolCallError:
        pass
    else:
        raise AssertionError("expected ToolCallError for an invalid status")

    compact = format_for_llm(sales)
    print(f"sales summary as compact JSON: {len(compact)} characters")
    print("All MCP client checks passed")


anyio.run(main)
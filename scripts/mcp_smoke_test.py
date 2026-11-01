import anyio
from mcp import Client

from technova.mcp_server.server import mcp


async def main() -> None:
    async with Client(mcp, raise_exceptions=True) as client:
        tools = await client.list_tools()
        names = sorted(tool.name for tool in tools.tools)
        assert names == ["find_employee", "get_project_status", "get_sales_summary", "get_tasks"], names

        employee = (await client.call_tool("find_employee", {"name": "Sneha"})).structured_content["result"]
        assert len(employee) == 1 and employee[0]["manager"] == "Rohan Iyer", employee

        nobody = (await client.call_tool("find_employee", {"name": "zzz"})).structured_content["result"]
        assert nobody == [], nobody

        atlas = (await client.call_tool("get_project_status", {"name": "Atlas"})).structured_content["result"]
        assert atlas[0]["task_counts"] == {"Done": 1, "In Progress": 3, "To Do": 1}, atlas

        karthik = (await client.call_tool("get_tasks", {"assignee": "Karthik"})).structured_content["result"]
        assert len(karthik) == 4, karthik

        todo = (await client.call_tool("get_tasks", {"project": "Atlas", "status": "To Do"})).structured_content["result"]
        assert len(todo) == 1 and todo[0]["assignee"] == "Vikram Singh", todo

        blocked = await client.call_tool("get_tasks", {"status": "Blocked"})
        assert blocked.is_error, blocked

        sales = (await client.call_tool("get_sales_summary", {})).structured_content
        assert sales["deals"] == 16 and sales["total_lakh"] == 230.0, sales

        by_region = {}
        for row in sales["breakdown"]:
            by_region[row["region"]] = by_region.get(row["region"], 0) + row["total_rs"]
        assert by_region == {"East": 2500000, "North": 5500000, "South": 8500000, "West": 6500000}, by_region

        south = (await client.call_tool("get_sales_summary", {"region": "South", "product": "NovaInsight"})).structured_content
        assert south["total_lakh"] == 40.0, south

        print("All MCP tool checks passed")

anyio.run(main)
from mcp.server import MCPServer
from technova.mcp_server.db import query
from typing import Any, Literal

mcp = MCPServer("TechNova Company Data")

FIND_EMPLOYEE_SQL = """
SELECT e.id, e.name, e.email, e.department, e.role, e.hire_date, e.location,
       m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id
WHERE e.name LIKE ?
ORDER BY e.id
"""

PROJECT_SQL = """
SELECT p.id, p.name, p.product, p.status, p.start_date, p.end_date,
       l.name AS lead
FROM projects p
JOIN employees l ON p.lead_id = l.id
WHERE p.name LIKE ?
ORDER BY p.id
"""

TASK_COUNT_SQL = """
SELECT status, COUNT(*) AS count
FROM tasks
WHERE project_id = ?
GROUP BY status
"""


@mcp.tool()
def find_employee(name: str) -> list[dict]:
    """Look up TechNova employees by name (partial, case-insensitive match).
    Returns each match with id, name, email, department, role, hire_date,
    location and manager name. Returns an empty list if nobody matches."""
    return query(FIND_EMPLOYEE_SQL, (f"%{name}%",))

@mcp.tool()
def get_project_status(name: str) -> list[dict]:
    """Look up TechNova projects by name (partial, case-insensitive match).
    Returns each match with id, name, product, status (Planning, In Progress,
    On Hold or Completed), lead name, start_date, end_date (null if not finished)
    and task_counts, the number of tasks in each status.
    Returns an empty list if no project matches."""
    projects = query(PROJECT_SQL, (f"%{name}%",))
    for project in projects:
        counts = query(TASK_COUNT_SQL, (project["id"],))
        project["task_counts"] = {row["status"]: row["count"] for row in counts}
    return projects

@mcp.tool()
def get_tasks(
    assignee: str | None = None,
    project: str | None = None,
    status: Literal["To Do", "In Progress", "Done"] | None = None,
    overdue_only: bool = False,
) -> list[dict]:
    """List TechNova tasks, optionally filtered. All filters are optional and
    combine with AND. assignee and project are partial, case-insensitive name
    matches. status must be one of: To Do, In Progress, Done. Set overdue_only
    to true to return only unfinished tasks whose due date has passed.
    Each task includes title, status, priority (Low, Medium, High), due_date,
    project and assignee. Returns at most 50 tasks, ordered by due date."""
    sql = """
    SELECT t.id, t.title, t.status, t.priority, t.due_date,
           p.name AS project, e.name AS assignee
    FROM tasks t
    JOIN projects p ON t.project_id = p.id
    JOIN employees e ON t.assignee_id = e.id
    WHERE 1 = 1
    """
    params = []
    if assignee:
        sql += " AND e.name LIKE ?"
        params.append(f"%{assignee}%")
    if project:
        sql += " AND p.name LIKE ?"
        params.append(f"%{project}%")
    if status:
        sql += " AND t.status = ?"
        params.append(status)
    if overdue_only:
        sql += " AND t.status != 'Done' AND t.due_date < date('now')"
    sql += " ORDER BY t.due_date LIMIT 50"
    return query(sql, tuple(params))


@mcp.tool()
def get_sales_summary(
    region: Literal["North", "South", "East", "West"] | None = None,
    product: Literal["NovaDesk", "NovaInsight"] | None = None,
) -> dict[str, Any]:
    """Summarize TechNova sales revenue. Optionally filter by region (North,
    South, East, West) and/or product (NovaDesk, NovaInsight); filters combine
    with AND. The database covers Q3 2026 only (1 July to 30 September 2026).
    Returns a breakdown per region and product with deal count and revenue,
    plus overall total_rs (rupees) and total_lakh (1 lakh = 100,000 rupees)."""
    sql = """
    SELECT region, product, COUNT(*) AS deals, SUM(amount_rs) AS total_rs
    FROM sales
    WHERE 1 = 1
    """
    params = []
    if region:
        sql += " AND region = ?"
        params.append(region)
    if product:
        sql += " AND product = ?"
        params.append(product)
    sql += " GROUP BY region, product ORDER BY region, product"

    rows = query(sql, tuple(params))
    total_rs = sum(row["total_rs"] for row in rows)
    return {
        "breakdown": rows,
        "deals": sum(row["deals"] for row in rows),
        "total_rs": total_rs,
        "total_lakh": total_rs / 100000,
    }

if __name__ == "__main__":
    mcp.run()
import time

from technova.graph.workflow import ask

CASES = [
    ("How many sick leave days do I get?", "knowledge", "leave_policy.md", "8"),
    ("What is the Q4 revenue target?", "knowledge", "q3_2026_sales_report.md", "250"),
    ("Summarize the expense policy", "summarize", "expense_policy.md", "10,000"),
    ("Who is Sneha's manager?", "data", "database: find_employee", "Rohan"),
    ("Which region earned the most revenue in Q3?", "data", "database: get_sales_summary", "South"),
    ("What tasks does Karthik have?", "data", "database: get_tasks", "Karthik"),
]

failures = []
for question, route, source, fact in CASES:
    try:
        result = ask(question)
    except Exception as error:
        failures.append(f"{question!r} raised {type(error).__name__}: {error}")
        continue
    problems = []
    if result.get("route") != route:
        problems.append(f"route {result.get('route')!r} != {route!r}")
    if source not in result.get("sources", []):
        problems.append(f"source {source!r} missing from {result.get('sources')}")
    if fact not in result.get("answer", ""):
        problems.append(f"{fact!r} not in answer")
    print(("FAIL " if problems else "ok   ") + question)
    if problems:
        failures.append(f"{question!r}: " + "; ".join(problems))
    time.sleep(12)

if failures:
    print("\n".join(failures))
    raise SystemExit(1)
print("All graph checks passed")
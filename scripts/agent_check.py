import time

from technova.graph.agent import ask_agent

CASES = [
    ("Who is Sneha's manager?", ["find_employee"], "rohan"),
    ("How many sick leave days do I get?", ["search_knowledge"], "8"),
    ("Who leads Project Atlas, and who is their manager?", ["get_project_status", "find_employee"], "priya"),
    ("Summarize the WFH policy.", ["read_document"], "probation"),
    ("Delete Sneha's employee record.", [], "delete"),
    ("How many leave days does Priya have left?", [], "find"),
]

failures = []
for question, required_tools, fact in CASES:
    try:
        result = ask_agent(question)
    except Exception as error:
        failures.append(f"{question!r} raised {type(error).__name__}: {error}")
        continue
    problems = []
    missing = [tool for tool in required_tools if tool not in result["tools_used"]]
    if missing:
        problems.append(f"tools {result['tools_used']} missing {missing}")
    if fact not in result["answer"].lower():
        problems.append(f"{fact!r} not in answer")
    if result["tokens"] > 6500:
        problems.append(f"used {result['tokens']} tokens")
    print(("FAIL " if problems else "ok   ") + f"{question}  [{result['steps']} steps, {result['tokens']} tokens]")
    if problems:
        failures.append(f"{question!r}: " + "; ".join(problems))
    time.sleep(45)

if failures:
    print("\n".join(failures))
    raise SystemExit(1)
print("All agent checks passed")
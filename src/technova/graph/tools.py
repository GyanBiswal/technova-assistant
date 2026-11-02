import anyio

from technova.docs_tools.summarizer import list_document_names, read_document
from technova.mcp_client.client import ToolCallError, call_tool, list_tool_schemas
from technova.rag.retriever import load_index


def search_knowledge(query: str, k: int = 3) -> list[dict]:
    docs = load_index().similarity_search(query, k=k)
    return [{"source": doc.metadata["source"], "text": doc.page_content} for doc in docs]


def local_tool_schemas() -> list[dict]:
    return [
        {
            "name": "search_knowledge",
            "description": (
                "Search TechNova's company documents (leave, work-from-home and expense "
                "policies, onboarding guide, product overview and pricing, the Q3 2026 sales "
                "report) for a specific fact. Returns only the 3 most relevant short passages, "
                "each with its source file, so it can NOT summarize a document or give an "
                "overview. Answer only from these passages."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"}
                },
                "required": ["query"],
            },
        },
        {
            "name": "read_document",
            "description": (
                "Read one whole TechNova document. ALWAYS use this when the user asks to "
                "summarize a document or wants an overview of it. "
                "Use search_knowledge instead for specific questions."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"name": {"type": "string", "enum": list_document_names()}},
                "required": ["name"],
            },
        },
    ]


def get_tool_schemas() -> list[dict]:
    return anyio.run(list_tool_schemas) + local_tool_schemas()


def run_tool(name: str, args: dict, allowed: set[str]):
    if name not in allowed:
        raise ToolCallError(f"Unknown tool: {name}")
    try:
        if name == "search_knowledge":
            return search_knowledge(args["query"])
        if name == "read_document":
            return {"name": args["name"], "text": read_document(args["name"])}
    except (KeyError, TypeError, ValueError) as error:
        raise ToolCallError(f"Invalid arguments for {name}: {error}") from error
    return anyio.run(call_tool, name, args)


if __name__ == "__main__":
    schemas = get_tool_schemas()
    allowed = {schema["name"] for schema in schemas}
    print([schema["name"] for schema in schemas])

    chunks = run_tool("search_knowledge", {"query": "sick leave certificate"}, allowed)
    print("search_knowledge ->", len(chunks), "chunks, first from", chunks[0]["source"])

    doc = run_tool("read_document", {"name": "leave_policy.md"}, allowed)
    print("read_document ->", len(doc["text"]), "characters")

    print("find_employee ->", run_tool("find_employee", {"name": "Sneha"}, allowed)[0]["name"])

    for bad_name, bad_args in [("delete_employee", {}), ("read_document", {"name": "../../.env"})]:
        try:
            run_tool(bad_name, bad_args, allowed)
        except ToolCallError as error:
            print(f"{bad_name} -> ToolCallError: {error}")
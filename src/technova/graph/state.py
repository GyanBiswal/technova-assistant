from typing import TypedDict


from typing import TypedDict


class State(TypedDict, total=False):
    question: str
    route: str
    document: str
    answer: str
    sources: list[str]
    error: str
    tool_call: dict
    tool_result: str
"""LangGraph state definitions.

This module defines the data structures that are passed between LangGraph
nodes. For the MVP we only provide a minimal placeholder class.
"""

from typing import TypedDict


class AgentState(TypedDict):
    question: str
    semantic_context: dict
    generated_sql: str
    query_result: list
    answer: str
    conversation_history: list[dict]
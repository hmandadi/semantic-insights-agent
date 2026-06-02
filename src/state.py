"""LangGraph state definitions.

This module defines the data structures that are passed between LangGraph
nodes. For the MVP we only provide a minimal placeholder class.
"""

from dataclasses import dataclass


@dataclass
class AgentState:
    """Container for the agent's intermediate data.

    Attributes:
        user_query: The natural‑language question supplied by the user.
        sql_query: The generated SQL statement (populated later).
        context: Optional dictionary for additional information.
    """

    user_query: str = ""
    sql_query: str = ""
    context: dict | None = None

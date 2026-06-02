"""
LangGraph node definitions.

Each node accepts AgentState and returns AgentState.
"""

from src.state import AgentState
from src.llm_service import LLMService
from src.db import execute_query


def sql_generator_node(state: AgentState) -> AgentState:
    """
    Generate SQL from natural language question.
    """

    question = state["question"]
    semantic_context = state["semantic_context"]

    llm = LLMService()

    generated_sql = llm.generate_sql(
        question=question,
        semantic_context=str(semantic_context)
    )

    state["generated_sql"] = generated_sql

    return state


def sql_executor_node(state: AgentState) -> AgentState:
    """
    Execute SQL against PostgreSQL.
    """

    sql = state["generated_sql"]

    result_df = execute_query(sql)

    state["query_result"] = result_df.to_dict(
        orient="records"
    )

    return state


def insight_node(state: AgentState) -> AgentState:
    """
    Convert query results into a human-readable answer.
    """

    state["answer"] = str(
        state["query_result"]
    )

    return state
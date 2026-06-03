"""LangGraph orchestration.

The ``graph`` module wires the individual node functions into a workflow.
"""

from langgraph.graph import StateGraph, END

from src.state import AgentState
from src.nodes import sql_generator_node, sql_executor_node, insight_node


def build_graph():
    """Build and compile the LangGraph workflow.

    Flow:
        START -> sql_generator -> sql_executor -> insight -> END

    Returns:
        Compiled StateGraph ready for execution.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("sql_generator", sql_generator_node)
    workflow.add_node("sql_executor", sql_executor_node)
    workflow.add_node("insight", insight_node)

    # Define edges
    workflow.set_entry_point("sql_generator")
    workflow.add_edge("sql_generator", "sql_executor")
    workflow.add_edge("sql_executor", "insight")
    workflow.add_edge("insight", END)

    # Compile and return
    return workflow.compile()
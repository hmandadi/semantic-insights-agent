"""LangGraph orchestration.

The ``graph`` module wires the individual node functions into a workflow.
For the MVP we provide a simple ``run`` function that executes the placeholder
nodes sequentially.
"""

from .state import AgentState
from .nodes import generate_prompt, call_llm


def run(user_query: str) -> AgentState:
    """Execute the LangGraph workflow for a given user query.

    Steps (placeholder):
    1. Initialise ``AgentState`` with the user query.
    2. Generate a prompt.
    3. Call the LLM (mock).

    Returns the final ``AgentState`` containing the generated SQL.
    """
    state = AgentState(user_query=user_query)
    state = generate_prompt(state)
    state = call_llm(state)
    return state

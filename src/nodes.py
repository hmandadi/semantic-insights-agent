"""LangGraph node definitions.

Each node represents a step in the workflow (e.g., generate prompt,
call LLM, translate to SQL). The MVP includes only placeholder functions
that return ``TODO`` strings.
"""

from .state import AgentState


def generate_prompt(state: AgentState) -> AgentState:
    """Create a prompt for the LLM based on the user query.

    TODO: Implement actual prompt templating.
    """
    # Placeholder – in a real implementation you would build a prompt string.
    state.context = {"prompt": f"Translate to SQL: {state.user_query}"}
    return state


def call_llm(state: AgentState) -> AgentState:
    """Invoke the LLM to generate a SQL query.

    TODO: Replace with actual OpenAI API call.
    """
    # Placeholder response.
    state.sql_query = "SELECT * FROM placeholder_table;"
    return state

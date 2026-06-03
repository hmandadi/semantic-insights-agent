"""Agent Service module.

Provides a high-level service for running the semantic insights agent workflow.
"""

from src.semantic_service import SemanticService
from src.graph import build_graph
from src.state import AgentState


class AgentService:
    """Service for executing the semantic insights agent workflow."""

    def __init__(self) -> None:
        """Initialize the AgentService with required dependencies."""
        self.semantic_service = SemanticService()
        self.graph = build_graph()

    def run(self, question: str) -> dict:
        """Execute the agent workflow for a given question.

        Args:
            question: The natural language question to process.

        Returns:
            A dictionary containing:
                - generated_sql: The SQL generated from the question
                - query_result: The results from executing the SQL
                - answer: The business insight generated from the results
        """
        # Build initial state
        initial_state: AgentState = {
            "question": question,
            "semantic_context": self.semantic_service.get_manifest(),
            "generated_sql": "",
            "query_result": [],
            "answer": ""
        }

        # Invoke LangGraph workflow
        result = self.graph.invoke(initial_state)

        # Return the required fields
        return {
            "generated_sql": result["generated_sql"],
            "query_result": result["query_result"],
            "answer": result["answer"]
        }
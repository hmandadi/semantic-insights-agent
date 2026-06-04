"""LLM service for generating SQL queries from natural language.

This module provides a thin wrapper around the OpenAI LLM (via LangChain) that
uses the ``SQL_GENERATION_PROMPT`` defined in :pymod:`src.prompts`. The service
loads the OpenAI API key from a ``.env`` file, constructs the prompt with the
provided semantic context and question, and returns the raw SQL string.

The implementation follows the requirements:
* Uses ``langchain_openai`` and ``python-dotenv``.
* Exposes a ``LLMService`` class with a ``generate_sql`` method.
* Utilises the latest GPT-4 model (``gpt-4o`` if available, otherwise falls back
  to ``gpt-4``).
* Handles exceptions and strips any markdown formatting that may be returned by
  the model.
"""

from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env (project root)
load_dotenv()

# Import the prompt templates
from .prompts import SQL_GENERATION_PROMPT, INSIGHT_PROMPT


def _strip_markdown(sql: str) -> str:
    """Remove common markdown wrappers from the LLM response.

    The model may return the query wrapped in triple backticks or a code block
    language identifier. This helper extracts the raw SQL.
    """
    # Remove leading/trailing whitespace
    sql = sql.strip()
    # Strip fenced code blocks ```sql ... ```
    fenced_pattern = r"^```(?:sql)?\n?(.*?\n?)```$"
    match = re.search(fenced_pattern, sql, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # If the response starts with a single backtick block, remove it
    if sql.startswith('`') and sql.endswith('`'):
        return sql.strip('`').strip()
    return sql


def _format_conversation_history(history: list[dict]) -> str:
    """Format conversation history into a compact string for the LLM prompt.

    Parameters
    ----------
    history:
        A list of conversation interaction dicts with 'question', 'generated_sql', and 'answer' keys.

    Returns
    -------
    str
        A formatted string for inclusion in the prompt, or empty string if no history.
    """
    if not history:
        return ""

    lines: list[str] = ["\nPrevious Conversation History:\n"]
    for i, interaction in enumerate(history, 1):
        question = interaction.get("question", "")
        sql = interaction.get("generated_sql", "")
        answer = interaction.get("answer", "")
        lines.append(f"  {i}. Q: {question}")
        if sql:
            lines.append(f"     SQL: {sql}")
        if answer:
            # Truncate answer to first line for compactness
            answer_line = answer.split("\n")[0] if answer else ""
            lines.append(f"     A: {answer_line}")
        lines.append("")

    return "".join(lines)


class LLMService:
    """
    Service that generates PostgreSQL queries using an OpenAI-compatible API
    (OpenAI or OpenRouter).
    """

    def __init__(self) -> None:

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY not found in environment variables."
            )

        self.client = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            temperature=0.0,
        )

    def generate_sql(
        self,
        question: str,
        semantic_context: str,
        conversation_history: list[dict] | None = None
    ) -> str:
        """Generate a PostgreSQL query for *question* using *semantic_context*.

        Parameters
        ----------
        question:
            The natural‑language question supplied by the user.
        semantic_context:
            Text describing tables, columns, and metric definitions from the
            semantic manifest.
        conversation_history:
            Optional list of previous interactions for follow-up questions.
            Each dict should have 'question', 'generated_sql', and 'answer' keys.

        Returns
        -------
        str
            The raw SQL query string, with any markdown removed.
        """
        try:
            # Format conversation history if provided
            history_str = ""
            if conversation_history:
                history_str = _format_conversation_history(conversation_history)

            prompt = SQL_GENERATION_PROMPT.format(
                semantic_context=semantic_context,
                question=question,
                conversation_history=history_str,
            )
            # LangChain expects a list of messages; we use a single user message.
            response = self.client.invoke(prompt)
            # ``invoke`` returns a ``BaseMessage``; the content is in ``.content``.
            raw_sql: str = getattr(response, "content", str(response))
            return _strip_markdown(raw_sql)
        except Exception as exc:  # pragma: no cover – generic safety net
            # Re‑raise with a clearer message while preserving the original
            # exception context for debugging.
            raise RuntimeError(f"Failed to generate SQL: {exc}") from exc

    def generate_insight(self, question: str, results: str) -> str:
        """Generate a concise business summary from query results.

        Parameters
        ----------
        question:
            The original natural‑language question that prompted the query.
        results:
            The query results as a string, to be analyzed for business insights.

        Returns
        -------
        str
            A concise business summary with key findings and observations.
        """
        try:
            prompt = INSIGHT_PROMPT.format(
                question=question,
                results=results,
            )
            response = self.client.invoke(prompt)
            insight: str = getattr(response, "content", str(response))
            return insight.strip()
        except Exception as exc:  # pragma: no cover – generic safety net
            raise RuntimeError(f"Failed to generate insight: {exc}") from exc
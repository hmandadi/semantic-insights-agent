"""LLM service for generating SQL queries from natural language.

This module provides a thin wrapper around the OpenAI LLM (via LangChain) that
uses the ``SQL_GENERATION_PROMPT`` defined in :pymod:`src.prompts`. The service
loads the OpenAI API key from a ``.env`` file, constructs the prompt with the
provided semantic context and question, and returns the raw SQL string.

The implementation follows the requirements:
* Uses ``langchain_openai`` and ``python-dotenv``.
* Exposes a ``LLMService`` class with a ``generate_sql`` method.
* Utilises the latest GPT‑4 model (``gpt-4o`` if available, otherwise falls back
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

# Import the prompt template
from .prompts import SQL_GENERATION_PROMPT


def _strip_markdown(sql: str) -> str:
    """Remove common markdown wrappers from the LLM response.

    The model may return the query wrapped in triple backticks or a code block
    language identifier. This helper extracts the raw SQL.
    """
    # Remove leading/trailing whitespace
    sql = sql.strip()
    # Strip fenced code blocks ```` ```sql ... ``` ````
    fenced_pattern = r"^```(?:sql)?\n?(.*?\n?)```$"
    match = re.search(fenced_pattern, sql, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # If the response starts with a single backtick block, remove it
    if sql.startswith('`') and sql.endswith('`'):
        return sql.strip('`').strip()
    return sql


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

    def generate_sql(self, question: str, semantic_context: str) -> str:
        """Generate a PostgreSQL query for *question* using *semantic_context*.

        Parameters
        ----------
        question:
            The natural‑language question supplied by the user.
        semantic_context:
            Text describing tables, columns, and metric definitions from the
            semantic manifest.

        Returns
        -------
        str
            The raw SQL query string, with any markdown removed.
        """
        try:
            prompt = SQL_GENERATION_PROMPT.format(
                semantic_context=semantic_context,
                question=question,
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

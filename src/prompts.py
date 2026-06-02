"""Prompt templates for the LLM.

In a full implementation this file would contain Jinja‑style templates or
functions that render prompts based on the semantic manifest. For the MVP we
provide a simple constant placeholder.
"""

DEFAULT_PROMPT = "Translate the following natural language question to a SQL query: {question}"

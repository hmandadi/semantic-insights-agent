"""Prompt templates for the LLM.

This module defines prompt strings used by the language model to generate
SQL queries from natural‑language questions. The prompts are designed to work
with the semantic layer defined in ``config/semantic_manifest.yaml``. The
``SQL_GENERATION_PROMPT`` includes placeholders for the semantic context – a
string representation of the tables, columns, and metric definitions – and the
user's question.

The prompt enforces the following requirements:
* Only tables and columns defined in the semantic layer may be referenced.
* Generated SQL must be valid PostgreSQL syntax.
* The response should contain **only** the SQL query – no markdown, no
  explanations.
* Joins should be used when the question involves multiple tables.
* Aggregations must follow the rules defined in the ``metrics`` section of the
  manifest.

Placeholders:
    {semantic_context} – a textual description of the available tables,
    columns, and metrics.
    {question} – the natural‑language question supplied by the user.
"""

# Prompt used by the LLM to generate a PostgreSQL query from a natural language
# question, respecting the semantic manifest.
SQL_GENERATION_PROMPT = (
    "You are an expert SQL generator. Use only the tables, columns, and metrics"
    " defined in the following semantic context. Generate a valid PostgreSQL"
    " query that answers the question. Return **only** the SQL statement,"
    " without any markdown or explanation.\n\n"
    "Semantic Context:\n{semantic_context}\n\n"
    "Question: {question}\n"
    "SQL Query:"
)

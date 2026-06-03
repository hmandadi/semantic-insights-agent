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
    "You are an expert PostgreSQL SQL generator. Your task is to generate a valid"
    " PostgreSQL SELECT query that answers the user's question.\n\n"
    "CRITICAL RULES:\n"
    "1. Use ONLY the table names exactly as listed in the semantic context below.\n"
    "2. Use ONLY the column names exactly as listed in the semantic context below.\n"
    "3. Do NOT invent or guess table or column names.\n"
    "4. Use the relationships defined in the semantic context to JOIN tables when"
    "   the question involves columns from multiple tables.\n"
    "5. Use the metric expressions (e.g., SUM(fact_sales.revenue)) when the question"
    "   asks for aggregated values.\n"
    "6. Return ONLY the SQL statement — no markdown, no code fences, no explanations.\n\n"
    "Semantic Context:\n{semantic_context}\n\n"
    "Question: {question}\n"
    "SQL Query:"
)

INSIGHT_PROMPT = """
You are a senior business analyst.

Question:
{question}

Query Results:
{results}

Rules:

- revenue values represent currency in USD.
- Keep revenue values as numeric decimals in query results.
- Do NOT add '$' symbols or comma formatting in query results.
- Currency formatting should only be applied in the UI layer.

- Explain findings in business language.
- Mention key observations.
- Do not output JSON.
- Do not output SQL.

Business Summary:
"""

"""Database utility module.

Provides a thin wrapper around ``psycopg2`` for connecting to a PostgreSQL
database and executing read‑only SQL queries, returning the results as a
``pandas.DataFrame``.  Connection parameters are loaded from a ``.env`` file
using ``python-dotenv``.

The module is deliberately simple yet production‑ready: it validates that only
SELECT statements are executed, logs actions and errors, and ensures that the
database connection is properly closed.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any

import pandas as pd
import psycopg2
from psycopg2 import sql as pg_sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Configure a basic logger only once (idempotent)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Load environment variables from .env located at the project root
load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")))


def _get_env_var(name: str) -> str:
    """Retrieve a required environment variable.

    Raises:
        KeyError: If the variable is missing.
    """
    value = os.getenv(name)
    if value is None:
        logger.error("Environment variable %s is not set", name)
        raise KeyError(f"Environment variable {name} is required but not set")
    return value


def get_connection() -> psycopg2.extensions.connection:
    """Create and return a new PostgreSQL connection.

    Connection parameters are read from the ``.env`` file:

    - ``DB_HOST``
    - ``DB_PORT`` (optional, defaults to 5432)
    - ``DB_NAME``
    - ``DB_USER``
    - ``DB_PASSWORD``
    """
    try:
        conn = psycopg2.connect(
            host=_get_env_var("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=_get_env_var("DB_NAME"),
            user=_get_env_var("DB_USER"),
            password=_get_env_var("DB_PASSWORD"),
            sslmode="require"
        )
        logger.info("PostgreSQL connection established")
        return conn
    except Exception as exc:
        logger.exception("Failed to create PostgreSQL connection: %s", exc)
        raise


_SELECT_ONLY_REGEX = re.compile(r"^\s*SELECT\b", re.IGNORECASE)


def validate_sql(sql: str) -> None:
    """Validate that the supplied SQL is a read‑only SELECT statement.

    The function raises a ``ValueError`` if the statement does not start with
    ``SELECT`` (ignoring leading whitespace) or if it contains any prohibited
    keywords such as INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
    """
    if not _SELECT_ONLY_REGEX.match(sql):
        raise ValueError("Only SELECT statements are allowed.")

    # Disallow dangerous keywords anywhere in the statement (case‑insensitive)
    prohibited = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]
    upper_sql = sql.upper()
    for kw in prohibited:
        if kw in upper_sql:
            raise ValueError(f"Prohibited keyword detected in SQL: {kw}")


def execute_query(sql: str) -> pd.DataFrame:
    """Execute a SELECT query and return the result as a ``pandas.DataFrame``.

    Args:
        sql: The SELECT statement to execute.

    Returns:
        DataFrame containing the query results.
    """
    logger.info("Executing query: %s", sql)
    validate_sql(sql)
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            df = pd.DataFrame(rows)
            logger.info("Query executed successfully, %d rows returned", len(df))
            return df
    except Exception as exc:
        logger.exception("Error executing query: %s", exc)
        raise
    finally:
        if conn is not None:
            conn.close()
            logger.info("PostgreSQL connection closed")

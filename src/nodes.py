"""
LangGraph node definitions.

Each node accepts AgentState and returns AgentState.
"""

from src.state import AgentState
from src.llm_service import LLMService
from src.db import execute_query


def _format_semantic_context(manifest: dict) -> str:
    """Convert the semantic manifest dict into a human-readable string for the LLM.

    This produces a clearly structured description of tables, columns, metrics,
    dimensions, and relationships so the LLM can accurately reference the correct
    names in generated SQL.
    """
    lines: list[str] = []

    # Tables and their columns
    tables = manifest.get("tables", {})
    if tables:
        lines.append("Tables:")
        for table_name, table_def in tables.items():
            desc = table_def.get("description", "") if isinstance(table_def, dict) else ""
            lines.append(f"  - {table_name}: {desc}")
            columns = table_def.get("columns", {}) if isinstance(table_def, dict) else {}
            if columns:
                lines.append("    Columns:")
                for col_name, col_def in columns.items():
                    col_type = col_def.get("type", "") if isinstance(col_def, dict) else ""
                    col_desc = col_def.get("description", "") if isinstance(col_def, dict) else ""
                    lines.append(f"      - {col_name} ({col_type}): {col_desc}")
            # Table-level relationships
            rels = table_def.get("relationships", []) if isinstance(table_def, dict) else []
            if rels:
                lines.append("    Relationships:")
                for rel in rels:
                    if isinstance(rel, dict):
                        for target, join_expr in rel.items():
                            lines.append(f"      - {target}: {join_expr}")
                    else:
                        lines.append(f"      - {rel}")

    # Metrics
    metrics = manifest.get("metrics", {})
    if metrics:
        lines.append("\nMetrics:")
        for metric_name, metric_def in metrics.items():
            expr = metric_def.get("expression", "") if isinstance(metric_def, dict) else ""
            biz_name = metric_def.get("business_name", metric_name) if isinstance(metric_def, dict) else metric_name
            lines.append(f"  - {biz_name} ({metric_name}): {expr}")

    # Dimensions
    dimensions = manifest.get("dimensions", {})
    if dimensions:
        lines.append("\nDimensions:")
        for dim_name, dim_def in dimensions.items():
            table = dim_def.get("table", "") if isinstance(dim_def, dict) else ""
            column = dim_def.get("column", "") if isinstance(dim_def, dict) else ""
            biz_name = dim_def.get("business_name", dim_name) if isinstance(dim_def, dict) else dim_name
            lines.append(f"  - {biz_name}: {table}.{column}")

    # Top-level relationships
    top_rels = manifest.get("relationships", {})
    if top_rels:
        lines.append("\nRelationships:")
        for table_name, joins in top_rels.items():
            if isinstance(joins, dict):
                for dim, join_info in joins.items():
                    if isinstance(join_info, dict):
                        jt = join_info.get("join_table", "")
                        jk = join_info.get("join_key", "")
                        lines.append(f"  - {table_name} -> {jt} on {table_name}.{jk} = {jt}.{jk}")

    return "\n".join(lines)


def sql_generator_node(state: AgentState) -> AgentState:
    """
    Generate SQL from natural language question.
    """

    question = state["question"]
    semantic_context = state["semantic_context"]

    llm = LLMService()

    formatted_context = _format_semantic_context(semantic_context)

    generated_sql = llm.generate_sql(
        question=question,
        semantic_context=formatted_context
    )

    state["generated_sql"] = generated_sql

    return state


def sql_executor_node(state: AgentState) -> AgentState:
    """
    Execute SQL against PostgreSQL.
    """

    sql = state["generated_sql"]

    result_df = execute_query(sql)

    state["query_result"] = result_df.to_dict(
        orient="records"
    )

    return state


def insight_node(state: AgentState) -> AgentState:
    """
    Convert query results into a human-readable business summary.
    """

    question = state["question"]
    results = state["query_result"]

    llm = LLMService()

    insight = llm.generate_insight(
        question=question,
        results=str(results)
    )

    state["answer"] = insight

    return state

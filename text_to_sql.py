from src.semantic_service import SemanticService
from src.nodes import sql_generator_node
from src.db import execute_query

semantic_service = SemanticService()

state = {
    "question": "Show revenue by region",
    "semantic_context": semantic_service.get_manifest(),
    "generated_sql": "",
    "query_result": [],
    "answer": ""
}

# Generate SQL
state = sql_generator_node(state)

print("\nGenerated SQL:")
print(state["generated_sql"])

# Execute SQL
df = execute_query(state["generated_sql"])

print("\nResults:")
print(df)
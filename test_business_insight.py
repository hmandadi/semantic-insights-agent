from src.semantic_service import SemanticService
from src.nodes import (
    sql_generator_node,
    sql_executor_node,
    insight_node
)

# Load semantic model
semantic_service = SemanticService()

# Initial state
state = {
    "question": "Show revenue by region",
    "semantic_context": semantic_service.get_manifest(),
    "generated_sql": "",
    "query_result": [],
    "answer": ""
}

print("\n" + "=" * 60)
print("QUESTION")
print("=" * 60)
print(state["question"])

# Step 1 - Generate SQL
state = sql_generator_node(state)

print("\n" + "=" * 60)
print("GENERATED SQL")
print("=" * 60)
print(state["generated_sql"])

# Step 2 - Execute SQL
state = sql_executor_node(state)

print("\n" + "=" * 60)
print("QUERY RESULTS")
print("=" * 60)

for row in state["query_result"]:
    print(row)

# Step 3 - Generate Business Insight
state = insight_node(state)

print("\n" + "=" * 60)
print("BUSINESS INSIGHT")
print("=" * 60)
print(state["answer"])
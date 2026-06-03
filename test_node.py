from src.semantic_service import SemanticService
from src.nodes import sql_generator_node


semantic_service = SemanticService()

state = {
    "question": "Show revenue by region",
    "semantic_context": semantic_service.load_manifest(),
    "generated_sql": "",
    "query_result": [],
    "answer": ""
}

updated_state = sql_generator_node(state)

print(updated_state["generated_sql"])
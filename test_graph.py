from src.graph import build_graph
from src.semantic_service import SemanticService

graph = build_graph()

semantic_service = SemanticService()

result = graph.invoke(
    {
        "question": "Show revenue by region",
        "semantic_context": semantic_service.get_manifest(),
        "generated_sql": "",
        "query_result": [],
        "answer": "",
        "conversation_history": []
    }
)

print(result["answer"])
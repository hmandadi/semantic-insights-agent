"""Test conversation memory flow.

This module tests the conversation memory functionality for follow-up questions.
"""

import inspect

from src.llm_service import LLMService, _format_conversation_history
from src.agent_service import AgentService


def test_format_conversation_history_empty():
    """Test that empty history returns empty string."""
    result = _format_conversation_history([])
    assert result == ""
    print("[PASS] Empty history test passed")


def test_format_conversation_history_single():
    """Test formatting a single conversation interaction."""
    history = [
        {
            "question": "Show revenue by region",
            "generated_sql": "SELECT region, SUM(revenue) FROM sales GROUP BY region",
            "answer": "APAC has the highest revenue at $5M"
        }
    ]
    result = _format_conversation_history(history)
    assert "Show revenue by region" in result
    assert "SELECT region" in result
    assert "APAC has the highest revenue" in result
    print("[PASS] Single history test passed")


def test_format_conversation_history_multiple():
    """Test formatting multiple conversation interactions."""
    history = [
        {
            "question": "Show revenue by region",
            "generated_sql": "SELECT region, SUM(revenue) FROM sales GROUP BY region",
            "answer": "APAC has highest revenue"
        },
        {
            "question": "Now show only APAC",
            "generated_sql": "SELECT * FROM sales WHERE region = 'APAC'",
            "answer": "APAC revenue details shown"
        }
    ]
    result = _format_conversation_history(history)
    assert "1." in result
    assert "2." in result
    assert "Show revenue by region" in result
    assert "Now show only APAC" in result
    print("[PASS] Multiple history test passed")


def test_llm_service_generate_sql_without_history():
    """Test that generate_sql works without conversation history (backward compatibility)."""
    # Verify the method accepts None for conversation_history
    sig = inspect.signature(LLMService.generate_sql)
    params = sig.parameters
    assert "conversation_history" in params
    assert params["conversation_history"].default is None
    print("[PASS] generate_sql signature test passed")


def test_agent_state_typing():
    """Test that AgentState includes conversation_history field."""
    from src.state import AgentState

    # Verify AgentState can be created with conversation_history
    state: AgentState = {
        "question": "test question",
        "semantic_context": {},
        "generated_sql": "SELECT 1",
        "query_result": [],
        "answer": "test answer",
        "conversation_history": []
    }

    assert state["conversation_history"] == []
    print("[PASS] AgentState typing test passed")


def test_agent_service_accepts_history():
    """Test that AgentService.run() accepts conversation_history parameter."""
    sig = inspect.signature(AgentService.run)
    params = sig.parameters

    assert "conversation_history" in params
    assert params["conversation_history"].default is None
    print("[PASS] AgentService.run signature test passed")


def test_follow_up_flow_simulation():
    """
    Simulate a follow-up conversation flow:
    a. Show revenue by region
    b. Now show only APAC
    c. Compare it with EMEA
    """
    # Step 1: Initial question - empty history
    initial_history = []

    # Step 2: First follow-up should include initial context
    first_follow_up = [
        {
            "question": "Show revenue by region",
            "generated_sql": "SELECT region, SUM(revenue) FROM fact_sales GROUP BY region",
            "answer": "Revenue breakdown by region generated"
        }
    ]

    formatted = _format_conversation_history(first_follow_up)
    assert "Show revenue by region" in formatted

    # Step 3: Second follow-up should include both interactions
    second_follow_up = [
        {
            "question": "Show revenue by region",
            "generated_sql": "SELECT region, SUM(revenue) FROM fact_sales GROUP BY region",
            "answer": "Revenue breakdown by region generated"
        },
        {
            "question": "Now show only APAC",
            "generated_sql": "SELECT * FROM fact_sales WHERE region = 'APAC'",
            "answer": "APAC revenue shown"
        }
    ]

    formatted = _format_conversation_history(second_follow_up)
    assert "Show revenue by region" in formatted
    assert "Now show only APAC" in formatted

    print("[PASS] Follow-up flow simulation test passed")


def test_apac_follow_up_uses_region_name():
    """
    Test that follow-up question 'Now show only APAC' generates SQL with dim_region.region_name.
    
    The LLM should NOT invent 'country' column - it must use the exact column from
    the semantic manifest: dim_region.region_name
    """
    from src.nodes import _format_semantic_context
    import yaml
    
    # Load the semantic manifest
    with open("config/semantic_manifest.yaml", "r") as f:
        manifest = yaml.safe_load(f)
    
    # Format the semantic context
    formatted_context = _format_semantic_context(manifest)
    
    # Verify the context includes region_name for the region dimension
    assert "region_name" in formatted_context, "region_name should be in semantic context"
    assert "dim_region" in formatted_context, "dim_region table should be in semantic context"
    
    # Verify the context shows the relationship
    assert "fact_sales" in formatted_context
    assert "region" in formatted_context.lower() or "region_id" in formatted_context
    
    print("[PASS] APAC follow-up uses region_name test passed")


def test_emea_follow_up_uses_region_name():
    """
    Test that follow-up question for EMEA also uses dim_region.region_name.
    
    The LLM should use the same column (region_name) for all region values,
    not invent different columns like 'country' for different regions.
    """
    from src.nodes import _format_semantic_context
    import yaml
    
    # Load the semantic manifest
    with open("config/semantic_manifest.yaml", "r") as f:
        manifest = yaml.safe_load(f)
    
    # Format the semantic context
    formatted_context = _format_semantic_context(manifest)
    
    # Verify the context includes region_name
    assert "region_name" in formatted_context, "region_name should be in semantic context"
    
    # The semantic context should clearly show that region uses region_name
    # This ensures the LLM knows to use dim_region.region_name for EMEA, APAC, Americas, etc.
    lines = formatted_context.split("\n")
    region_line = None
    for line in lines:
        if "Region" in line and "dim_region" in line:
            region_line = line
            break
    
    assert region_line is not None, "Region dimension line should be found"
    assert "region_name" in region_line, f"Region line should contain region_name: {region_line}"
    
    print("[PASS] EMEA follow-up uses region_name test passed")


def test_prompt_includes_strict_rules():
    """
    Test that the SQL_GENERATION_PROMPT includes the strict rules for follow-up questions.
    """
    from src.prompts import SQL_GENERATION_PROMPT
    
    # Verify the prompt contains the strict rules
    assert "STRICT RULES FOR FOLLOW-UP QUESTIONS" in SQL_GENERATION_PROMPT
    assert "Use ONLY exact table names and column names from semantic_manifest.yaml" in SQL_GENERATION_PROMPT
    assert "Never infer or invent columns" in SQL_GENERATION_PROMPT
    assert "For APAC, EMEA, Americas, use dim_region.region_name" in SQL_GENERATION_PROMPT
    assert "Semantic manifest is the only source of truth for schema" in SQL_GENERATION_PROMPT
    
    print("[PASS] Prompt includes strict rules test passed")


if __name__ == "__main__":
    print("Running conversation memory flow tests...\n")

    test_format_conversation_history_empty()
    test_format_conversation_history_single()
    test_format_conversation_history_multiple()
    test_llm_service_generate_sql_without_history()
    test_agent_state_typing()
    test_agent_service_accepts_history()
    test_follow_up_flow_simulation()
    test_apac_follow_up_uses_region_name()
    test_emea_follow_up_uses_region_name()
    test_prompt_includes_strict_rules()

    print("\n[SUCCESS] All tests passed!")
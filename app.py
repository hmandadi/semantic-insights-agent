"""Streamlit entry point for the Semantic Insights Agent.

This minimal app provides a text input for a user question and displays the
generated SQL query using the placeholder LangGraph workflow defined in
``src.graph``. All heavy‑lifting (LLM calls, database access) is mocked.
"""

# Streamlit may not be installed in the development environment. Provide a
# lightweight fallback that mimics the required API surface so the script can
# be executed (e.g., during tests) without raising an import error.
try:
    import streamlit as st
except ModuleNotFoundError:  # pragma: no cover
    class _DummyStreamlit:
        def title(self, *args, **kwargs):
            print("[title]", *args)

        def write(self, *args, **kwargs):
            print(*args)

        def text_input(self, *args, **kwargs):
            # In a non‑interactive fallback, simply return an empty string.
            return ""

        def subheader(self, *args, **kwargs):
            print("[subheader]", *args)

        def code(self, *args, **kwargs):
            print(*args)

    st = _DummyStreamlit()
from src.graph import run

st.title("Semantic Insights Agent")
st.write("Enter a business question and receive a generated SQL query (mock).")

question = st.text_input("Business question")
if question:
    state = run(question)
    st.subheader("Generated SQL Query")
    st.code(state.sql_query, language="sql")

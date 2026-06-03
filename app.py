"""Streamlit entry point for the Semantic Insights Agent.

This app provides a text input for a user question and displays the
generated SQL query, query results, and business insight.
"""

import streamlit as st
import pandas as pd

from src.agent_service import AgentService


st.title("Semantic Insights Agent")

# Input
question = st.text_input("Enter your business question:")

# Button
if st.button("Analyze"):
    if question and isinstance(question, str):
        try:
            # Initialize service
            agent = AgentService()
            
            # Run the workflow
            result = agent.run(question)
            
            # Display Generated SQL
            st.subheader("Generated SQL")
            st.code(result["generated_sql"], language="sql")
            
            # Display Query Results
            st.subheader("Query Results")
            if result["query_result"]:
                df = pd.DataFrame(result["query_result"])
                st.dataframe(df)
            else:
                st.write("No results returned.")
            
            # Display Business Insight
            st.subheader("Business Insight")
            st.markdown(result["answer"])
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
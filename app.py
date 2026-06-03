"""
Semantic Insights Agent

Enterprise Semantic Analytics Application

Features:
- Natural language business questions
- AI-generated SQL
- Query result visualization
- KPI summary cards
- Business insights generation
"""

import traceback

import pandas as pd
import streamlit as st

from src.agent_service import AgentService
from src.visualization_service import VisualizationService


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Semantic Insights Agent",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Semantic Insights Agent")
st.markdown(
    """
    Enterprise AI Analytics Assistant that converts natural language
    business questions into SQL, executes queries against enterprise
    data, generates business insights, and visualizes results.
    """
)
st.markdown("### Try an Example")

col1, col2 = st.columns(2)

with col1:
    if st.button("Revenue by Region"):
        st.session_state["question"] = "Show revenue by region"

    if st.button("Top Customers"):
        st.session_state["question"] = "Show top 5 customers by revenue"

with col2:
    if st.button("Revenue by Product"):
        st.session_state["question"] = "Show revenue by product"

    if st.button("Quantity by Region"):
        st.session_state["question"] = "Show quantity sold by region"

question = st.text_input(
    "Ask a business question",
    value=st.session_state.get("question", ""),
    placeholder="Example: What are the top 5 products by revenue?"
)

# ==================================================
# CACHED SERVICES
# ==================================================

@st.cache_resource
def get_agent():
    return AgentService()


@st.cache_resource
def get_visualization_service():
    return VisualizationService()


agent = get_agent()
viz_service = get_visualization_service()

df = None


# ==================================================
# ANALYZE BUTTON
# ==================================================

if st.button("Analyze", type="primary"):

    if not question or not question.strip():
        st.warning("Please enter a business question.")
        st.stop()

    try:
        with st.spinner("Analyzing your question..."):
            result = agent.run(question)

        generated_sql = result.get("generated_sql", "")
        query_result = result.get("query_result", [])
        answer = result.get("answer", "No insights generated.")

        # ==========================================
        # GENERATED SQL
        # ==========================================

        st.subheader("Generated SQL")

        if generated_sql:
            st.code(generated_sql, language="sql")
        else:
            st.info("No SQL generated.")

        # ==========================================
        # QUERY RESULTS
        # ==========================================

        if query_result and len(query_result) > 0:

            df = pd.DataFrame(query_result)

            # ======================================
            # KPI CARDS
            # ======================================

            st.subheader("Summary Metrics")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="Rows Returned",
                    value=f"{len(df):,}"
                )

            with col2:
                st.metric(
                    label="Columns Returned",
                    value=len(df.columns)
                )

            with col3:
                st.metric(
                    label="Question Length",
                    value=f"{len(question)} chars"
                )

            # ======================================
            # RESULTS TABLE
            # ======================================

            st.subheader("Query Results")

            column_config = {}

            revenue_keywords = [
                "revenue",
                "sales",
                "amount",
                "total_revenue"
            ]

            revenue_col = None

            for col in df.columns:
                col_lower = str(col).lower()

                if any(keyword in col_lower for keyword in revenue_keywords):
                    revenue_col = col
                    break

            if revenue_col:
                column_config[revenue_col] = st.column_config.NumberColumn(
                    "Revenue",
                    format="%,.2f"
                )

            st.dataframe(
                df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No results returned.")

        # ==========================================
        # VISUALIZATION
        # ==========================================

        if df is not None and not df.empty:
            try:
                chart_data = viz_service.prepare_chart_data(df)
                chart_type = viz_service.get_chart_type(chart_data)

                if chart_type:
                    st.subheader("Visualization")

                    x_col, y_col = viz_service.get_chart_columns(chart_data)

                    if x_col and y_col:
                        if chart_type == "bar":
                            st.bar_chart(
                                chart_data,
                                x=x_col,
                                y=y_col,
                                use_container_width=True
                            )

                        elif chart_type == "line":
                            st.line_chart(
                                chart_data.set_index(x_col),
                                use_container_width=True
                            )

                        elif chart_type == "area":
                            st.area_chart(
                                chart_data.set_index(x_col),
                                use_container_width=True
                            )
                else:
                    st.info("No visualization available for this result set.")

            except Exception as viz_error:
                st.warning(
                    f"Visualization could not be generated: {viz_error}"
                )

        # ==========================================
        # BUSINESS INSIGHT
        # ==========================================

        st.subheader("Business Insight")

        if answer:
            st.markdown(answer)
        else:
            st.info("No insight generated.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

        with st.expander("Debug Details"):
            st.code(traceback.format_exc())

st.markdown("---")

st.markdown(
    """
    <div style='text-align:center'>
        <h4>Semantic Insights Agent v1.0</h4>
        <p>
            LangGraph | PostgreSQL | Streamlit | Python | LLM
        </p>
        <p>
            Designed & Developed by Harshavardhan Mandadi
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
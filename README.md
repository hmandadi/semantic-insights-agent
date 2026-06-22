# Semantic Insights Agent

## Project Overview
The **Semantic Insights Agent** is a cloud-hosted conversational AI analytics platform that enables business users to interact with enterprise data using natural language. The solution combines semantic metadata, LangGraph-based agentic workflows, Large Language Models (LLMs), Text-to-SQL orchestration, conversational memory, and PostgreSQL to translate business questions into governed data queries, generate AI-powered insights, and deliver interactive analytics for data-driven decision-making.

## Architecture Overview
```
Semantic Insights Agent (Streamlit UI)
    └─> LangGraph workflow (graph.py, nodes.py, state.py)
        └─> Prompts (prompts.py)
        └─> Database layer (db.py) → PostgreSQL
        └─> Semantic manifest (config/semantic_manifest.yaml)
```
* **Streamlit** – lightweight UI for entering questions and displaying results.
* **LangGraph** – orchestrates the LLM‑driven reasoning steps.
* **LLM (OpenAI)** – generates natural‑language to SQL translations.
* **PostgreSQL** – stores the underlying data warehouse.
* **YAML semantic layer** – defines business concepts and governance rules.

## Folder Structure
```
semantic-insights-agent/
├── .gitignore
├── .env.example
├── README.md
├── requirements.txt
├── config/
│   └── semantic_manifest.yaml   # placeholder for semantic definitions
├── src/
│   ├── __init__.py
│   ├── state.py                # LangGraph state definitions
│   ├── nodes.py                # individual LangGraph nodes
│   ├── graph.py                # graph orchestration
│   ├── db.py                   # PostgreSQL helper utilities
│   └── prompts.py              # prompt templates for the LLM
└── app.py                      # Streamlit entry point


# Semantic Insights Agent

## Project Overview
The **Semantic Insights Agent** is an enterprise‑grade semantic analytics prototype. It translates natural‑language business questions into governed SQL queries using a semantic layer, LangGraph orchestration, PostgreSQL, and large language models (LLMs). This repository contains a minimal MVP suitable for learning and portfolio demonstration.

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


# TechNova Solutions: AI-Powered Enterprise Knowledge Assistant

An AI assistant that answers employee questions using company documents (RAG)
and company data (MCP tools), orchestrated with LangGraph.

**Status:** Part 5: document search, summarization, and document Q&A working

## Planned stack
Groq (gpt-oss-120b) · FAISS · LangChain · LangGraph · MCP · SQLite · Streamlit

## Setup

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python scripts/seed_db.py   # builds data/technova.db from data/schema.sql
    PYTHONPATH=src python -m technova.rag.indexer   # builds the FAISS index from data/documents
    PYTHONPATH=src python -m technova.rag.answerer "How many sick leave days do I get?"
    PYTHONPATH=src python -m technova.docs_tools.doc_search "work from home"
    PYTHONPATH=src python -m technova.docs_tools.summarizer leave_policy.md

Copy `.env.example` to `.env` and fill in your keys.
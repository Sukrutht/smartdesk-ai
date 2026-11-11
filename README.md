# SmartDesk AI

AI-powered IT support and knowledge management learning project built with Python and FastAPI.

**Status:** starter implementation. Configure your Gemini API key, run tests, and verify the AI workflows before describing this as complete or production-ready.

## Planned capabilities
- Upload PDF support documents and extract text.
- Chunk documents, create embeddings, and store vectors in ChromaDB.
- Retrieve relevant passages and draft answers with document references.
- Classify support tickets and suggest priority and first responses.
- Store ticket records in SQLite by default, with PostgreSQL configurable.

## Stack
Python, FastAPI, Gemini API, ChromaDB, SQLAlchemy, SQLite/PostgreSQL, PyPDF, Pytest, Docker.

## Setup
See `.env.example` for configuration. Never commit your real `.env` or API keys.

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for API documentation.

## Important limitations
This is a learning prototype. AI output requires human review. Scanned PDF OCR, authentication/authorization, rate limiting, tenant isolation, audit logging, and production security controls are not included. Do not upload confidential customer or company data.

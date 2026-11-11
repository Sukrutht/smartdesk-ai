# SmartDesk AI

An AI-assisted IT support and knowledge management application built with **Python, FastAPI, Google Gemini, ChromaDB, and PostgreSQL**. The project combines support-ticket triage with document-grounded question answering through a Retrieval-Augmented Generation (RAG) workflow.

**Live demo:** https://smartdesk-ai-api.onrender.com  
**API documentation:** https://smartdesk-ai-api.onrender.com/docs

## Features

- **AI ticket triage:** Submit an issue title and description; Gemini suggests a support category, priority, and first response.
- **Ticket management:** List tickets and update their status.
- **PDF knowledge base:** Upload text-based PDF support documents, extract page text, split it into overlapping chunks, generate embeddings, and index the chunks in ChromaDB.
- **Grounded knowledge assistant:** Retrieve relevant document chunks and ask Gemini to answer using only the retrieved context. Answers include source document names, page numbers, excerpts, and relevance values.
- **Safer fallback behavior:** The assistant indicates when an answer is not present in the indexed documents. Gemini quota/rate-limit errors are returned as user-friendly messages.
- **Responsive web interface:** A lightweight HTML/CSS/JavaScript dashboard for ticket creation, ticket tracking, PDF upload, and knowledge questions.

## Technology stack

| Area | Technologies |
|---|---|
| Language | Python |
| Backend | FastAPI, Uvicorn |
| Generative AI | Google Gemini API |
| RAG and vector search | ChromaDB, embeddings, semantic retrieval |
| Document processing | PyPDF, text chunking |
| Database and ORM | PostgreSQL, SQLite, SQLAlchemy |
| API testing | Pytest, FastAPI TestClient, Swagger UI |
| Deployment and tools | Render, Docker, GitHub Actions, Git |

## Architecture overview

1. A user submits a support ticket through the dashboard or API.
2. FastAPI sends the ticket details to Gemini for category, priority, and suggested-response generation.
3. The ticket result is stored in the relational database through SQLAlchemy.
4. For knowledge questions, a user uploads a text-based PDF.
5. PyPDF extracts text by page; the application chunks the text and requests Gemini embeddings.
6. ChromaDB stores the chunks, embeddings, document names, and page metadata.
7. A question is embedded and used to retrieve relevant chunks. Gemini receives those chunks as context and is instructed not to invent answers outside that context.
8. The response includes source references to the retrieved document pages.

## Run locally

### Prerequisites

- Python 3.11+
- A Google Gemini API key
- Git

### Setup

```bash
git clone https://github.com/Sukrutht/smartdesk-ai.git
cd smartdesk-ai

python -m venv .venv
```

Activate the environment:

**Windows**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file using `.env.example` as a reference and set your own Gemini API key and database configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
DATABASE_URL=sqlite:///./smartdesk.db
CHROMA_PATH=./chroma_data
MAX_UPLOAD_MB=10
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 for the dashboard or http://127.0.0.1:8000/docs for interactive API documentation.\n\n### Run with Docker\n\n\`\`\`bash\ndocker build -t smartdesk-ai .\ndocker run --env-file .env -p 8000:8000 smartdesk-ai\n\`\`\`

## Main API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application and AI configuration status |
| GET | `/diagnostics/database` | Database connectivity check |
| POST | `/documents/upload` | Upload and index a PDF |
| POST | `/ask` | Ask a question using indexed documents |
| GET | `/knowledge/stats` | Return indexed chunk count |
| POST | `/tickets` | Create and classify a support ticket |
| GET | `/tickets` | List support tickets |
| PATCH | `/tickets/{ticket_id}` | Update ticket status |

## Tests

Run the automated tests with:

```bash
pytest -q
```

GitHub Actions runs the test suite on pushes and pull requests.

## Deployment configuration

The application is configured for deployment on Render. The deployed service uses a Neon PostgreSQL connection supplied through the `DATABASE_URL` environment variable. Set `GEMINI_API_KEY` in the hosting provider's environment settings; never commit real credentials.

## Current limitations

This is a **portfolio/learning project**, not a production-ready enterprise helpdesk.

- Authentication, authorization, user roles, and tenant isolation are not implemented.
- AI-generated ticket classifications and suggested responses require human review.
- Only text-based PDFs are supported; scanned/image-only PDFs require OCR, which is not included.
- PDF upload is limited by the configured `MAX_UPLOAD_MB` value (10 MB by default).
- ChromaDB currently uses local persistent storage at `CHROMA_PATH`. On the Render free service this is configured under `/tmp`, which is ephemeral; indexed documents may need to be uploaded again after a service restart or redeploy.
- Ticket records use the configured relational database; the hosted deployment is configured to use Neon PostgreSQL.
- Gemini usage is subject to the API key's model access, quota, and rate limits.
- Production controls such as rate limiting, audit logging, malware scanning, OCR, and comprehensive security hardening are not included.

Do not upload confidential company, customer, or personal documents to the public demo.

## License

No license has been added yet. All rights are reserved unless a license is provided.

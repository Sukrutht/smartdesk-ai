# SmartDesk AI — phone-friendly learning guide

This guide is designed for learning in short sessions on a phone. Read one concept, explain it aloud in your own words, then answer the check question before moving on.

## 1. What problem does the project solve?

IT support teams repeatedly answer questions already explained in manuals and troubleshoot recurring issues. SmartDesk AI lets a support person upload a manual, ask a question in normal language, and receive an answer linked to the relevant document pages. It also helps organize new support tickets.

**Interview explanation:** “I built SmartDesk AI, a Python-based support knowledge assistant. It indexes PDF manuals, retrieves relevant passages using vector similarity, and uses an LLM to generate an answer grounded in those passages. It also classifies support tickets and stores them in a relational database.”

## 2. Understand the architecture first

- **Client:** A user or API testing tool sends HTTP requests.
- **FastAPI:** Receives requests, validates input, calls services, and returns JSON.
- **PDF extraction:** `pypdf` reads selectable text from a PDF.
- **Chunking:** Long text is split into smaller overlapping passages so retrieval can find focused context.
- **Embedding:** An embedding model converts text into a list of numbers (a vector) representing semantic meaning.
- **ChromaDB:** Stores vectors and metadata and finds passages semantically similar to a question.
- **LLM:** Gemini reads the retrieved passages and writes a natural-language answer.
- **SQL database:** Stores structured ticket information such as title, category, priority and status.

## 3. What is an API?

An API is a defined way for two software systems to communicate. In this project, `POST /ask` accepts a JSON question and returns a JSON answer with sources. `GET /tickets` returns saved tickets.

**HTTP methods:** GET reads data, POST creates/processes data, PATCH partially updates data, DELETE removes data.

**Check yourself:** Why is `POST /documents/upload` a POST endpoint rather than GET?

## 4. What is an LLM?

A Large Language Model is a model trained on large amounts of text that can understand prompts and generate text. SmartDesk sends Gemini a carefully written prompt plus retrieved document passages. The model generates an answer. It does not automatically know your private manuals; the app supplies relevant passages as context.

**Check yourself:** What is the difference between your Python code and the LLM in this application?

## 5. What is RAG?

RAG means Retrieval-Augmented Generation. It has three main stages:

1. **Retrieve:** Search for passages relevant to the user's question.
2. **Augment:** Add those passages to the prompt as context.
3. **Generate:** Ask the LLM to answer using that context.

RAG is useful when answers must use a changing or private knowledge base. It can reduce unsupported answers, but it does not guarantee correctness.

**Check yourself:** Why do we retrieve manual passages instead of asking Gemini the question without context?

## 6. What are embeddings and vector search?

An embedding is a numeric representation of text. Texts with similar meanings tend to have vectors that are close in the embedding space. ChromaDB compares the question vector with stored document vectors and returns the closest passages. This is semantic search: it can find related meaning even when exact words differ.

**Check yourself:** How is semantic search different from searching for an exact keyword?

## 7. Why chunk documents?

A whole manual may be too large and too broad to send for every question. Chunking divides it into smaller passages. Overlap carries a little text from one chunk into the next so a sentence or idea near a boundary is less likely to be split apart.

In this project the chunk target is 900 characters with 120 characters of overlap. These are starter settings, not universally optimal values.

**Check yourself:** What might happen if chunks are too small or too large?

## 8. Why use two databases?

- **ChromaDB** stores embeddings and supports similarity search over document chunks.
- **SQLite/PostgreSQL** stores structured business records such as support tickets and their statuses.

A vector database is not a replacement for a relational database. They solve different data problems.

## 9. Ticket classification

When a ticket is submitted, the app asks Gemini to return a category, priority and suggested first response in JSON. Python validates the allowed category and priority values before saving the ticket. A human must review the suggestion; the AI must not claim it fixed the issue.

**Check yourself:** Why should a support engineer review AI-assigned priority?

## 10. Code tour — files to understand

- `app/main.py`: API routes and request flow.
- `app/ai.py`: Gemini HTTP requests, embeddings and ticket classification.
- `app/knowledge.py`: PDF extraction, chunking, vector indexing and retrieval.
- `app/models.py`: SQLAlchemy ticket table.
- `app/schemas.py`: Pydantic request/response validation.
- `app/database.py`: database connection and session lifecycle.
- `app/config.py`: environment-based settings.
- `tests/test_chunking.py`: basic tests for text splitting.

## 11. Security and limitations to explain honestly

The API key belongs in a server-side environment variable, never in a public GitHub repository or browser code. The starter does not yet include login/authentication, role permissions, rate limits, tenant isolation, audit logging or production monitoring. It supports text-based PDFs, not scanned image PDFs. Do not upload confidential documents. AI output can be inaccurate and requires human review.

## 12. Suggested 12-session study plan

1. Project problem, use cases and architecture.
2. Python project structure, imports, functions and async/await.
3. HTTP, JSON, REST APIs and FastAPI routes.
4. Pydantic validation and error handling.
5. PDF text extraction and document chunking.
6. LLMs, prompts, tokens and model APIs.
7. Embeddings and vector representations.
8. ChromaDB and semantic similarity search.
9. RAG retrieval, context construction and grounded answers.
10. SQLAlchemy, relational tables and ticket CRUD.
11. Testing, environment variables, Git and GitHub.
12. Limitations, security, deployment concepts and interview practice.

## 13. Interview questions to practise

1. Explain SmartDesk AI in one minute.
2. What problem does RAG solve?
3. What are embeddings?
4. Why do you chunk documents?
5. What is the difference between ChromaDB and PostgreSQL?
6. What happens from the moment a user submits a question until the answer is returned?
7. How do you show the source of an AI answer?
8. How do you handle a question not answered by the documents?
9. Why must an API key be stored in an environment variable?
10. What would you improve before using this in a real company?

Do not claim deployment, production readiness, accuracy metrics or user adoption unless you have actually measured or completed them.

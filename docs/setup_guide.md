# Full Environment Setup Guide

## 1. Local LLM Setup (Ollama)
The backend utilizes Ollama to perform NLP tasks entirely locally, avoiding third-party API costs and preserving data privacy.

1. Install Ollama from [ollama.com](https://ollama.com).
2. Ensure Ollama is running on your host machine.
3. Pull the required models in your terminal:
   ```bash
   ollama pull nomic-embed-text:latest
   ollama pull llama3.2:3b
   ```
*(Note: `nomic-embed-text:latest` produces 768-dimensional embeddings, which exactly matches our pgvector configuration).*

## 2. Docker Setup
We use Docker Compose to orchestrate the Frontend, Backend, and PostgreSQL database.
The backend is configured to talk to your local host's Ollama instance via `http://host.docker.internal:11434`.

1. Install Docker Desktop.
2. In the project root, duplicate `.env.example` to `.env` and fill in a `JWT_SECRET_KEY` (e.g. `openssl rand -hex 32`).
3. Build and start the containers:
   ```bash
   docker compose up --build -d
   ```

## 3. Database Migrations & Initial Setup
The `docker-compose.yml` automatically runs Alembic migrations on startup via the `faq_backend` container. This will:
- Create all tables (`users`, `faq_documents`, `faq_chunks`, `conversations`, `messages`).
- Create the pgvector extension.
- Build the HNSW index on `faq_chunks.embedding` using `vector_cosine_ops`.

If you ever need to run migrations manually:
```bash
docker exec faq_backend alembic upgrade head
```

## 4. Accessing the Application
- **Frontend App**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Postgres DB**: `localhost:5432` (Username: `postgres`, DB: `faq_chatbot`)

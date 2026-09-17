# Architecture

This document describes the high-level architecture of the AI FAQ Chatbot.

## Technology Stack
- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons
- **Backend**: FastAPI (Python), SQLAlchemy, Pydantic, Alembic
- **Database**: PostgreSQL 16 with pgvector extension
- **LLM/Embeddings**: Local Ollama (`llama3.2:3b` and `nomic-embed-text:latest`)

## High-Level Data Flow

### Flow
```text
User
 ↓
React (Frontend)
 ↓
JWT Authentication
 ↓
FastAPI (Backend)
 ├── Conversation Service
 │      ↓
 │   PostgreSQL
 │      ├── Conversations
 │      └── Messages
 │
 ├── FAQ Service & Ingestion
 │      ↓
 │   PostgreSQL (Documents/Chunks)
 │
 └── RAG Service
        ↓
     pgvector
        ↓
     FAQ Context
        ↓
     Ollama LLM
        ↓
     Grounded Answer
        ↓
     Store Assistant Message
        ↓
     PostgreSQL
```

## Components

### 1. Ingestion Pipeline
Processes `.txt`, `.csv`, and `.pdf` files.
- Extracts text.
- Splits into chunks using `RecursiveCharacterTextSplitter`.
- Stores metadata (Document) and chunks (FAQChunk) in PostgreSQL.

### 2. Embedding Service
Uses `nomic-embed-text:latest` to generate 768-dimensional vectors for text chunks.

### 3. RAG Service
Searches `pgvector` for similar contexts and builds a highly restricted prompt that prevents hallucination and prompt-injections, then asks `llama3.2:3b` for a grounded answer.

### 4. Conversation Service
Natively persists User and Assistant conversations inside PostgreSQL. Uses cascading deletions and heavily validates JSON Web Tokens to enforce rigid ownership.

## Containerization
The system runs via Docker Compose with three containers:
- `faq_postgres`: Database instance with pgvector
- `faq_backend`: FastAPI Python server
- `faq_frontend`: React Vite server

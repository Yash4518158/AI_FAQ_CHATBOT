# API Documentation
This document will contain all REST API specifications.

## FAQ Endpoints
Base path: `/faqs`
Auth: Bearer Token required for all routes

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/faqs/ingest` | Ingest a file (.txt, .csv, .pdf) | `multipart/form-data` | 200 OK (Ingestion Summary) |
| POST | `/faqs/` | Create a new FAQ | `{"title": "...", "content": "..."}` | 201 Created (FAQ Object) |
| GET | `/faqs/` | List current user's FAQs | - | 200 OK (List of FAQs) |
| GET | `/faqs/{id}` | Get specific FAQ | - | 200 OK (FAQ Object) |
| PUT | `/faqs/{id}` | Update specific FAQ | `{"title": "...", "content": "..."}` | 200 OK (FAQ Object) |
| DELETE | `/faqs/{id}` | Delete specific FAQ | - | 204 No Content |
| POST | `/faqs/ask` | Generates a grounded LLM answer | `{"query": "...", "top_k": 5}` | 200 OK (Answer Object) |

### Ask FAQs
**POST** `/faqs/ask`
Generates a grounded LLM answer using semantic similarity search. Now automatically creates or reuses conversations.

**Request Body**
```json
{
  "query": "How do I reset my password?",
  "conversation_id": "optional-uuid",
  "top_k": 5
}
```

**Response (200 OK)**
```json
{
  "conversation_id": "new-or-existing-uuid",
  "query": "How do I reset my password?",
  "answer": "To reset your password, click the forgot password link on the login page.",
  "sources": [
    {
      "chunk_id": "ab83c1...",
      "document_id": "92f3a7...",
      "document_title": "Account Issues",
      "similarity": 0.8921
    }
  ]
}
```

## Conversations
Base path: `/conversations`
Requires JWT authentication.

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/conversations` | List user's conversations | - | 200 OK (List[ConversationResponse]) |
| GET | `/conversations/{id}` | Get specific conversation | - | 200 OK (ConversationResponse) |
| GET | `/conversations/{id}/messages` | List messages chronologically | - | 200 OK (List[MessageResponse]) |
| PATCH | `/conversations/{id}` | Update conversation title | `{"title": "..."}` | 200 OK (ConversationResponse) |
| DELETE | `/conversations/{id}` | Delete conversation | - | 204 No Content |

## Embeddings
Base path: `/faqs`
Auth: Bearer Token required for all routes

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/faqs/{id}/embed` | Embed document's chunks | - | 200 OK (Embedding Summary) |
| POST | `/faqs/embed-all` | Embed all user's chunks | - | 200 OK (Embedding Summary) |

## Future Endpoints
Will include endpoints for Chat interaction and vector search in Phase 7.

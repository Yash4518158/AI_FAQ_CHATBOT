# Database Schema

## Users Table
`users`
- `id`: String (UUID) Primary Key
- `name`: String
- `email`: String (Unique)
- `password_hash`: String
- `created_at`: DateTime

## FAQ Documents Table
`faq_documents`
- `id`: String (UUID) Primary Key
- `title`: String
- `content`: Text
- `created_at`: DateTime
- `created_by`: String (Foreign Key -> users.id)

## Conversations Table (`conversations`)
Stores user conversation sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String | PK, UUID default | Unique ID |
| `user_id` | String | FK(`users.id`) | Owner of the conversation |
| `title` | String(100) | Not Null | Auto-generated title |
| `created_at` | DateTime | default now | Creation time |
| `updated_at` | DateTime | auto-update | Last updated time |

## Messages Table (`messages`)
Stores individual messages within a conversation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String | PK, UUID default | Unique ID |
| `conversation_id` | String | FK(`conversations.id`) | Belongs to conversation |
| `role` | Enum | Not Null | 'user' or 'assistant' |
| `content` | Text | Not Null | Message text |
| `sources` | JSONB | Nullable | Source metadata from RAG |
| `created_at` | DateTime | default now | Message timestamp |

## Relationships
- A `User` can have many `FAQDocument`s.
- An `FAQDocument` can have many `FAQChunk`s.
- A `User` can have many `Conversation`s.
- A `Conversation` can have many `Message`s.
- Cascade deletion ensures `FAQDocument` deletion removes all its `FAQChunk`s.
- Cascade deletion ensures `Conversation` deletion removes all its `Message`s.

## FAQ Chunks Table (pgvector)
`faq_chunks`
- `id`: String (UUID) Primary Key
- `document_id`: String (Foreign Key -> faq_documents.id ON DELETE CASCADE)
- `chunk_index`: Integer
- `text_chunk`: Text
- `embedding`: Vector (pgvector, dimensions TBD based on Ollama model in Phase 6).

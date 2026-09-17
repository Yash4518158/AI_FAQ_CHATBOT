import os
import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.faq import FAQChunk, FAQDocument

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest")
DIMENSION = 768

def check_ollama_and_model():
    """Verify Ollama is reachable and model is installed."""
    try:
        res = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        res.raise_for_status()
        models = [m['name'] for m in res.json().get('models', [])]
        if not any(m.startswith(EMBEDDING_MODEL.split(":")[0]) for m in models):
            raise ValueError(f"Model '{EMBEDDING_MODEL}' is not installed in Ollama. Please run: ollama pull {EMBEDDING_MODEL}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Ollama is unreachable at {OLLAMA_URL}: {str(e)}")

def generate_query_embedding(text: str) -> list[float]:
    """Generates an embedding for a query string."""
    if not text.strip():
        raise ValueError("Cannot embed empty text.")
        
    try:
        res = requests.post(f"{OLLAMA_URL}/api/embeddings", json={
            "model": EMBEDDING_MODEL,
            "prompt": text
        }, timeout=30)
        res.raise_for_status()
        
        emb = res.json().get('embedding')
        if not emb or not isinstance(emb, list):
            raise ValueError("Ollama returned an invalid or empty embedding.")
            
        if len(emb) != DIMENSION:
            raise ValueError(f"Expected dimension {DIMENSION}, got {len(emb)}")
            
        return emb
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to generate embedding: {str(e)}")

def embed_document_chunks(document_id: str, user_id: str, db: Session):
    """Embeds all chunks for a document that have NULL embeddings."""
    # 1. Verify ownership
    doc = db.query(FAQDocument).filter(FAQDocument.id == document_id, FAQDocument.created_by == user_id).first()
    if not doc:
        raise ValueError("Document not found or unauthorized.")
        
    # 2. Verify Ollama
    check_ollama_and_model()
    
    # 3. Get chunks
    all_chunks = db.query(FAQChunk).filter(FAQChunk.document_id == document_id).all()
    if not all_chunks:
        raise ValueError("Document has no chunks.")
        
    null_chunks = [c for c in all_chunks if c.embedding is None]
    
    # 4. Embed
    embedded_count = 0
    for chunk in null_chunks:
        try:
            emb = generate_query_embedding(chunk.text_chunk)
            chunk.embedding = emb
            embedded_count += 1
        except ValueError as e:
            # We skip storing this chunk's embedding but continue others, 
            # or we can abort the whole transaction. 
            # The prompt says: "If embedding generation fails: do not store an invalid vector, provide a useful error, maintain database consistency"
            # Since we haven't committed, raising here rolls back the transaction in the route.
            raise ValueError(f"Failed to embed chunk {chunk.chunk_index}: {str(e)}")
            
    # Commit changes
    db.commit()
    
    return {
        "document_id": document_id,
        "chunks_processed": len(all_chunks),
        "chunks_embedded": embedded_count,
        "chunks_skipped": len(all_chunks) - embedded_count,
        "model": EMBEDDING_MODEL,
        "embedding_dimension": DIMENSION,
        "status": "success"
    }

def embed_all_documents(user_id: str, db: Session):
    """Embeds all NULL chunks for all documents owned by the user."""
    check_ollama_and_model()
    
    docs = db.query(FAQDocument).filter(FAQDocument.created_by == user_id).all()
    
    total_processed = 0
    total_embedded = 0
    total_skipped = 0
    
    for doc in docs:
        all_chunks = db.query(FAQChunk).filter(FAQChunk.document_id == doc.id).all()
        null_chunks = [c for c in all_chunks if c.embedding is None]
        
        total_processed += len(all_chunks)
        total_skipped += (len(all_chunks) - len(null_chunks))
        
        for chunk in null_chunks:
            try:
                emb = generate_query_embedding(chunk.text_chunk)
                chunk.embedding = emb
                total_embedded += 1
            except ValueError as e:
                raise ValueError(f"Failed on doc {doc.id}, chunk {chunk.chunk_index}: {str(e)}")
                
    db.commit()
    
    return {
        "chunks_processed": total_processed,
        "chunks_embedded": total_embedded,
        "chunks_skipped": total_skipped,
        "model": EMBEDDING_MODEL,
        "embedding_dimension": DIMENSION,
        "status": "success"
    }

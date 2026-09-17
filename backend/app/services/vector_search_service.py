from typing import Optional
from sqlalchemy.orm import Session
from app.models.faq import FAQChunk, FAQDocument
from app.services.embedding_service import generate_query_embedding

MAX_TOP_K = 20

def search_similar_chunks(
    query: str,
    user_id: str,
    db: Session,
    top_k: int = 5,
    document_id: Optional[str] = None
) -> dict:
    """
    Performs a vector similarity search across FAQ chunks using pgvector's cosine distance.
    """
    # Validate query
    query = query.strip()
    if not query:
        raise ValueError("Query cannot be empty or whitespace.")
    if len(query) > 1000:
        raise ValueError("Query is too long. Maximum allowed is 1000 characters.")
        
    # Validate top_k
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")
    if top_k > MAX_TOP_K:
        raise ValueError(f"top_k cannot exceed {MAX_TOP_K}.")
        
    # Generate query embedding
    try:
        query_vector = generate_query_embedding(query)
    except ValueError as e:
        raise ValueError(f"Failed to generate query embedding: {str(e)}")
        
    # Build SQLAlchemy Query
    # Calculate cosine distance using pgvector operator <=>
    # We want to order by distance ascending (smaller distance = more similar)
    distance_col = FAQChunk.embedding.cosine_distance(query_vector).label("distance")
    
    base_query = db.query(FAQChunk, distance_col).join(FAQDocument)
    
    # 1. Ignore NULL embeddings
    base_query = base_query.filter(FAQChunk.embedding.isnot(None))
    
    # 2. Apply ownership filtering (CRITICAL)
    base_query = base_query.filter(FAQDocument.created_by == user_id)
    
    # 3. Apply optional document_id filtering
    if document_id:
        base_query = base_query.filter(FAQDocument.id == document_id)
        
    # 4. Order and Limit
    results = base_query.order_by(distance_col).limit(top_k).all()
    
    # Format the response
    formatted_results = []
    for chunk, distance in results:
        # Convert distance to similarity score: similarity = 1 - cosine_distance
        # Ensure it's bound between 0 and 1 gracefully if slight floating point variance
        similarity = max(0.0, min(1.0, 1.0 - distance))
        
        formatted_results.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "document_title": chunk.document.title,
            "text": chunk.text_chunk,
            "similarity": round(similarity, 4),
            "metadata": chunk.chunk_metadata
        })
        
    return {
        "query": query,
        "results": formatted_results,
        "top_k": top_k,
        "results_count": len(formatted_results)
    }

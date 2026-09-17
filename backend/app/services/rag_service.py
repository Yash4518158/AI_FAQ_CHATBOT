from typing import Optional
from sqlalchemy.orm import Session
from app.services.vector_search_service import search_similar_chunks
from app.services.llm_service import generate_answer

RAG_SYSTEM_PROMPT = """You are a helpful FAQ assistant.
Answer the user's question using ONLY the provided knowledge-base context.

CONTEXT:
<knowledge_base>
{context}
</knowledge_base>

USER QUESTION:
<question>
{query}
</question>

RULES:
1. Answer strictly based on the provided CONTEXT. Do not use outside knowledge.
2. If the answer is not present in the CONTEXT, you MUST reply exactly: "I couldn't find enough information about that in the FAQ knowledge base."
3. Provide a clear, concise answer.
"""

def answer_question(
    query: str,
    user_id: str,
    db: Session,
    top_k: int = 5,
    document_id: Optional[str] = None
) -> dict:
    """Orchestrates RAG: Searches similar chunks, constructs context, and generates LLM answer."""
    
    # 1. Retrieve similar chunks
    search_response = search_similar_chunks(
        query=query,
        user_id=user_id,
        db=db,
        top_k=top_k,
        document_id=document_id
    )
    
    results = search_response.get("results", [])
    
    # 2. Filter and construct context
    # If no results returned or similarity is extremely poor, we can preemptively abort LLM call.
    # We will enforce a basic threshold of 0.3 for relevance, but this is debatable. 
    # The prompt explicitly handles "no context" well, but saving a slow LLM call is better.
    # The user instruction: "If no usable relevant chunks are returned: Do NOT call the LLM unnecessarily. Return a controlled "insufficient information" response."
    
    # Let's filter out completely irrelevant chunks
    valid_chunks = [r for r in results if r["similarity"] > 0.3]
    
    if not valid_chunks:
        return {
            "query": query,
            "answer": "I couldn't find enough information about that in the FAQ knowledge base.",
            "sources": []
        }
        
    context_blocks = []
    for i, r in enumerate(valid_chunks):
        title = r.get("document_title", "Unknown")
        text = r.get("text", "")
        context_blocks.append(f"SOURCE {i+1}:\nDocument: {title}\nChunk:\n{text}\n")
        
    context_str = "\n".join(context_blocks)
    
    # 3. Construct Prompt
    prompt = RAG_SYSTEM_PROMPT.format(context=context_str, query=query)
    
    # 4. Generate Answer
    answer = generate_answer(prompt)
    
    # 5. Return structured response
    sources = [
        {
            "chunk_id": r["chunk_id"],
            "document_id": r["document_id"],
            "document_title": r["document_title"],
            "similarity": r["similarity"]
        } for r in valid_chunks
    ]
    
    return {
        "query": query,
        "answer": answer,
        "sources": sources
    }

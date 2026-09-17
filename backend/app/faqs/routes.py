from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
from app.database.connection import get_db
from app.models.user import User
from app.models.faq import FAQDocument
from app.schemas.faq import FAQDocumentCreate, FAQDocumentUpdate, FAQDocumentResponse, FAQSearchRequest, FAQAskRequest
from app.auth.dependencies import get_current_user
from app.ingestion.service import process_file_ingestion
from app.services.embedding_service import embed_document_chunks, embed_all_documents
from app.services.vector_search_service import search_similar_chunks
from app.services.rag_service import answer_question

from app.services import conversation_service
from app.schemas.conversation import FAQAskResponse

router = APIRouter(prefix="/faqs", tags=["FAQs"])

@router.post("/ask", response_model=FAQAskResponse)
def ask_faqs(
    request: FAQAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Handle Conversation
        conv_id = request.conversation_id
        if conv_id:
            # Verify ownership
            conversation_service.get_conversation_by_id(db, current_user.id, conv_id)
        else:
            # Auto-create conversation
            title = request.query[:100]
            conv = conversation_service.create_conversation(db, current_user.id, title)
            conv_id = conv.id
            
        # Store user message
        conversation_service.add_message(db, conv_id, "user", request.query)
        db.commit() # Commit user message first

        try:
            # Run RAG
            results = answer_question(
                query=request.query,
                user_id=current_user.id,
                db=db,
                top_k=request.top_k,
                document_id=request.document_id
            )
            
            # Store assistant message
            conversation_service.add_message(db, conv_id, "assistant", results["answer"], results.get("sources", []))
            db.commit()
            
            return FAQAskResponse(
                conversation_id=conv_id,
                query=results["query"],
                answer=results["answer"],
                sources=results.get("sources", [])
            )
        except Exception as llm_error:
            # If LLM generation fails, do not store a fake message
            # The user message is safely committed, which is fine.
            raise llm_error
            
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"RAG failed: {str(e)}")

@router.post("/search")
def search_faqs(
    request: FAQSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        results = search_similar_chunks(
            query=request.query,
            user_id=current_user.id,
            db=db,
            top_k=request.top_k,
            document_id=request.document_id
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/{document_id}/embed")
def embed_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return embed_document_chunks(document_id, current_user.id, db)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred during embedding: {str(e)}")

@router.post("/embed-all")
def embed_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return embed_all_documents(current_user.id, db)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred during embedding: {str(e)}")

@router.post("/ingest")
async def ingest_faq_file(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    max_size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", 10))
    file_bytes = await file.read()
    
    if len(file_bytes) > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum upload size of {max_size_mb}MB")
        
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
        
    try:
        doc, chunk_count = process_file_ingestion(file_bytes, file.filename, current_user.id, db)
        db.commit()
        return {
            "document_id": doc.id,
            "filename": file.filename,
            "chunks_created": chunk_count,
            "status": "success"
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred during ingestion: {str(e)}")

@router.post("/", response_model=FAQDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_faq(faq_in: FAQDocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_faq = FAQDocument(
        title=faq_in.title,
        content=faq_in.content,
        created_by=current_user.id
    )
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return new_faq

@router.get("/", response_model=List[FAQDocumentResponse])
def get_faqs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Fetch FAQs created by the current user (or all if admin, but here just user's)
    faqs = db.query(FAQDocument).filter(FAQDocument.created_by == current_user.id).all()
    return faqs

@router.get("/{faq_id}", response_model=FAQDocumentResponse)
def get_faq(faq_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    faq = db.query(FAQDocument).filter(FAQDocument.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    if faq.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this FAQ")
    return faq

@router.put("/{faq_id}", response_model=FAQDocumentResponse)
def update_faq(faq_id: str, faq_in: FAQDocumentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    faq = db.query(FAQDocument).filter(FAQDocument.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    if faq.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this FAQ")
    
    if faq_in.title is not None:
        faq.title = faq_in.title
    if faq_in.content is not None:
        faq.content = faq_in.content
        
    db.commit()
    db.refresh(faq)
    return faq

@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(faq_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    faq = db.query(FAQDocument).filter(FAQDocument.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    if faq.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this FAQ")
    
    db.delete(faq)
    db.commit()
    return None

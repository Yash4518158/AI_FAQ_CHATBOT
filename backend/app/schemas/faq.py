from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class FAQChunkResponse(BaseModel):
    id: str
    chunk_index: int
    text_chunk: str

    class Config:
        from_attributes = True

class FAQSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: Optional[str] = None

class FAQAskRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    top_k: int = 5
    document_id: Optional[str] = None

class FAQDocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)

class FAQDocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)

class FAQDocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime
    created_by: str
    
    # We optionally include chunks if needed, but typically we might just return the doc
    chunks: List[FAQChunkResponse] = []

    class Config:
        from_attributes = True

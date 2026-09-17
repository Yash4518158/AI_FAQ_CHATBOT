from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    sources: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    query: str

class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FAQAskResponse(BaseModel):
    conversation_id: str
    query: str
    answer: str
    sources: List[Any]

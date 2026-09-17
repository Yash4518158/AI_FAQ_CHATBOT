from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.auth.routes import get_current_user
from app.schemas.user import UserResponse
from app.schemas.conversation import ConversationResponse, ConversationUpdate, MessageResponse
from app.services import conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("", response_model=List[ConversationResponse])
def get_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return conversation_service.get_user_conversations(db, current_user.id, limit, offset)

@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return conversation_service.get_conversation_by_id(db, current_user.id, conversation_id)

@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return conversation_service.update_conversation_title(db, current_user.id, conversation_id, data.title)

@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    conversation_service.delete_conversation(db, current_user.id, conversation_id)
    return None

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return conversation_service.get_conversation_messages(db, current_user.id, conversation_id, limit, offset)

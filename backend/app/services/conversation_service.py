from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.conversation import Conversation, Message, MessageRole

def create_conversation(db: Session, user_id: str, title: str) -> Conversation:
    # Truncate title just in case
    title = title[:100]
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_user_conversations(db: Session, user_id: str, limit: int = 20, offset: int = 0):
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.created_at.desc()).offset(offset).limit(limit).all()

def get_conversation_by_id(db: Session, user_id: str, conversation_id: str) -> Conversation:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    return conv

def update_conversation_title(db: Session, user_id: str, conversation_id: str, title: str) -> Conversation:
    conv = get_conversation_by_id(db, user_id, conversation_id)
    conv.title = title[:100]
    db.commit()
    db.refresh(conv)
    return conv

def delete_conversation(db: Session, user_id: str, conversation_id: str):
    conv = get_conversation_by_id(db, user_id, conversation_id)
    db.delete(conv)
    db.commit()

def add_message(db: Session, conversation_id: str, role: str, content: str, sources: list = None) -> Message:
    # We assume the conversation ownership was already verified before calling this
    message = Message(
        conversation_id=conversation_id,
        role=MessageRole(role),
        content=content,
        sources=sources
    )
    db.add(message)
    # We do not commit here to allow atomic transactions in the route
    return message

def get_conversation_messages(db: Session, user_id: str, conversation_id: str, limit: int = 50, offset: int = 0):
    # Enforce ownership
    get_conversation_by_id(db, user_id, conversation_id)
    
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).offset(offset).limit(limit).all()

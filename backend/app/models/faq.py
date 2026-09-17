from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
import uuid
from app.database.connection import Base

class FAQDocument(Base):
    __tablename__ = "faq_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    source = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, ForeignKey("users.id"), nullable=False)

    # Relationships
    author = relationship("User")
    chunks = relationship("FAQChunk", back_populates="document", cascade="all, delete-orphan")

class FAQChunk(Base):
    __tablename__ = "faq_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("faq_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text_chunk = Column(Text, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    embedding = Column(Vector(768), nullable=True)

    # Relationships
    document = relationship("FAQDocument", back_populates="chunks")

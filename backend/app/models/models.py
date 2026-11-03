import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(100), nullable=False, default="user_1")
    title = Column(String(255), nullable=False, default="New Conversation")
    default_language = Column(String(10), nullable=False, default="hi")
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.timestamp")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False) # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    original_question = Column(Text, nullable=True)
    rewritten_question = Column(Text, nullable=True)
    answer_language = Column(String(10), nullable=True)
    sources = Column(JSON, nullable=True) # list of source dicts
    timestamp = Column(DateTime, default=utc_now)

    conversation = relationship("Conversation", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    domain = Column(String(100), nullable=False, default="General") # e.g. HR, IT Security, Physics
    document_type = Column(String(100), nullable=False, default="Policy") # e.g. Company Policy, Textbook
    language = Column(String(10), nullable=False, default="en") # Primary language of document
    total_pages = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    status = Column(String(50), default="processing") # 'processing', 'completed', 'failed'
    error_message = Column(Text, nullable=True)
    file_hash = Column(String(64), nullable=True, index=True) # SHA256 hash
    uploaded_at = Column(DateTime, default=utc_now)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String(64), primary_key=True) # Matches vector DB chunk_id
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(100), nullable=False)
    section = Column(String(255), nullable=True) # e.g. Clause 4.2 or Chapter 3
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)

    document = relationship("Document", back_populates="chunks")

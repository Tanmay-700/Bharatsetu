from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ConversationCreate(BaseModel):
    user_id: Optional[str] = "user_1"
    title: Optional[str] = "New Conversation"
    default_language: Optional[str] = "hi"

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    original_question: Optional[str] = None
    rewritten_question: Optional[str] = None
    answer_language: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    default_language: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True

class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = []
    summary: Optional[str] = None

class ChatRequest(BaseModel):
    conversation_id: str
    question: str
    answer_language: Optional[str] = "hi"
    user_id: Optional[str] = "user_1"

class DocumentResponse(BaseModel):
    id: str
    filename: str
    domain: str
    document_type: str
    language: str
    total_pages: int
    total_chunks: int
    status: str
    error_message: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True

class TranslationRequest(BaseModel):
    text: str
    source_language: Optional[str] = "auto"
    target_language: str

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str

class JevRouteResponse(BaseModel):
    question: str
    predicted_domains: List[str]
    confidence: float
    explanation: Optional[str] = None

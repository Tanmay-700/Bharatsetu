from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.services.chat.conversation_service import ConversationService
from app.schemas.schemas import ConversationCreate, ConversationResponse, ConversationDetailResponse

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.post("", response_model=ConversationResponse)
async def create_conversation(req: ConversationCreate):
    """Create a new chat conversation thread."""
    convo = await ConversationService.create_conversation(
        user_id=req.user_id or "user_1",
        title=req.title or "New Conversation",
        default_language=req.default_language or "hi"
    )
    return convo

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(user_id: str = Query("user_1")):
    """List all conversations for the active user."""
    convos = await ConversationService.list_conversations(user_id=user_id)
    return convos

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(conversation_id: str):
    """Retrieve full message history for a specific conversation."""
    convo = await ConversationService.get_conversation(conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and its messages."""
    deleted = await ConversationService.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "success", "message": "Conversation deleted successfully"}

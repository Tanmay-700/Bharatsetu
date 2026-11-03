from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, desc
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.models.models import Conversation, Message
from app.core.logger import logger

class ConversationService:
    """Manages conversations and chat history in SQLite."""

    @staticmethod
    async def create_conversation(
        user_id: str = "user_1",
        title: str = "New Conversation",
        default_language: str = "hi"
    ) -> Conversation:
        async with AsyncSessionLocal() as session:
            convo = Conversation(
                user_id=user_id,
                title=title,
                default_language=default_language
            )
            session.add(convo)
            await session.commit()
            await session.refresh(convo)
            logger.info(f"Created new conversation: {convo.id}")
            return convo

    @staticmethod
    async def get_conversation(conversation_id: str) -> Optional[Conversation]:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Conversation)
                .where(Conversation.id == conversation_id)
                .options(selectinload(Conversation.messages))
            )
            res = await session.execute(stmt)
            return res.scalar_one_or_none()

    @staticmethod
    async def list_conversations(user_id: str = "user_1") -> List[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(desc(Conversation.updated_at))
                .options(selectinload(Conversation.messages))
            )
            res = await session.execute(stmt)
            convos = res.scalars().all()
            return [
                {
                    "id": c.id,
                    "user_id": c.user_id,
                    "title": c.title,
                    "default_language": c.default_language,
                    "created_at": c.created_at,
                    "updated_at": c.updated_at,
                    "message_count": len(c.messages)
                }
                for c in convos
            ]

    @staticmethod
    async def delete_conversation(conversation_id: str) -> bool:
        async with AsyncSessionLocal() as session:
            stmt = delete(Conversation).where(Conversation.id == conversation_id)
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0

    @staticmethod
    async def update_title_if_default(conversation_id: str, first_question: str) -> None:
        """Sets a human-readable title based on the first question if currently 'New Conversation'."""
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(Conversation).where(Conversation.id == conversation_id))
            convo = res.scalar_one_or_none()
            if convo and (convo.title == "New Conversation" or not convo.title):
                # Take first 40 chars of question
                title = first_question.strip().split("\n")[0][:40]
                convo.title = title if len(first_question) <= 40 else f"{title}..."
                convo.updated_at = datetime.now(timezone.utc)
                await session.commit()

    @staticmethod
    async def add_message(
        conversation_id: str,
        role: str,
        content: str,
        original_question: Optional[str] = None,
        rewritten_question: Optional[str] = None,
        answer_language: Optional[str] = None,
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        async with AsyncSessionLocal() as session:
            msg = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                original_question=original_question,
                rewritten_question=rewritten_question,
                answer_language=answer_language,
                sources=sources,
                timestamp=datetime.now(timezone.utc)
            )
            session.add(msg)
            
            # Touch conversation updated_at
            res = await session.execute(select(Conversation).where(Conversation.id == conversation_id))
            convo = res.scalar_one_or_none()
            if convo:
                convo.updated_at = datetime.now(timezone.utc)

            await session.commit()
            await session.refresh(msg)
            return msg

    @staticmethod
    async def get_recent_messages(conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(desc(Message.timestamp))
                .limit(limit)
            )
            res = await session.execute(stmt)
            messages = list(reversed(res.scalars().all()))
            return [
                {"role": m.role, "content": m.content}
                for m in messages
            ]

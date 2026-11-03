import pytest
from app.core.database import init_db
from app.services.chat.conversation_service import ConversationService
from app.services.chat.query_rewriter import QueryRewriter

@pytest.mark.asyncio
async def test_conversation_memory_lifecycle():
    await init_db()
    
    # 1. Create conversation
    convo = await ConversationService.create_conversation(
        user_id="test_user",
        title="Physics Discussion",
        default_language="hi"
    )
    assert convo.id is not None
    assert convo.title == "Physics Discussion"

    # 2. Add user message
    msg1 = await ConversationService.add_message(
        conversation_id=convo.id,
        role="user",
        content="What is electric current?"
    )
    assert msg1.content == "What is electric current?"

    # 3. Add assistant message
    msg2 = await ConversationService.add_message(
        conversation_id=convo.id,
        role="assistant",
        content="Electric current is the flow of electric charge."
    )
    assert msg2.role == "assistant"

    # 4. Check history retrieval
    history = await ConversationService.get_recent_messages(convo.id, limit=5)
    assert len(history) == 2
    assert history[0]["content"] == "What is electric current?"
    assert history[1]["content"] == "Electric current is the flow of electric charge."

    # 5. Clean up
    deleted = await ConversationService.delete_conversation(convo.id)
    assert deleted is True

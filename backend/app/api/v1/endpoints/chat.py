import json
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.logger import logger
from app.schemas.schemas import ChatRequest
from app.services.chat.conversation_service import ConversationService
from app.services.chat.query_rewriter import query_rewriter
from app.services.chat.context_manager import context_manager
from app.services.routing.jev_router import jev_router
from app.services.retrieval.embeddings import embedding_service
from app.services.retrieval.vector_store import vector_store
from app.services.retrieval.reranker import reranker_service
from app.services.generation.prompts import prompt_factory
from app.services.generation.llm import llm_service

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("")
async def stream_chat(req: ChatRequest):
    """
    Main conversational RAG endpoint with multi-turn memory, Jev routing,
    cross-lingual retrieval, and SSE streaming generation.
    """
    convo = await ConversationService.get_conversation(req.conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation ID not found")

    target_lang = req.answer_language or convo.default_language or "hi"

    # 1. Update title if needed
    await ConversationService.update_title_if_default(req.conversation_id, req.question)

    # 2. Save user message
    await ConversationService.add_message(
        conversation_id=req.conversation_id,
        role="user",
        content=req.question,
        original_question=req.question,
        answer_language=target_lang
    )

    # 3. Retrieve recent history for coreference resolution
    history = await ConversationService.get_recent_messages(req.conversation_id, limit=8)

    # Exclude the message we just added from history for the query rewriter
    prior_history = history[:-1] if len(history) > 1 else []

    # 4. Resolve conversational references
    rewritten_query = await query_rewriter.rewrite_if_needed(req.question, prior_history)

    # 5. Jev Domain Routing
    routing_result = await jev_router.route(rewritten_query)
    routed_domains = routing_result.get("domains", [])

    # 6. Dense Multilingual Embedding
    query_vector = embedding_service.embed_query(rewritten_query)

    # 7. Vector DB Retrieval
    candidates = vector_store.search(
        query_embedding=query_vector,
        top_k=settings.TOP_K_RETRIEVAL,
        domain_filter=routed_domains if routed_domains else None
    )

    # 8. Cross-Lingual Reranking
    best_chunks = reranker_service.rerank(
        query=rewritten_query,
        candidates=candidates,
        top_n=settings.TOP_N_RERANK
    )

    # Prepare sources for client citations
    sources = []
    for c in best_chunks:
        meta = c.get("metadata", {})
        sources.append({
            "chunk_id": c.get("chunk_id"),
            "document_name": meta.get("document_name", "Document"),
            "domain": meta.get("domain", "General"),
            "section": meta.get("section", "Section"),
            "page_number": meta.get("page_number", 1),
            "score": c.get("rerank_score", c.get("score", 0.0)),
            "content_preview": c.get("content", "")[:250] + "..."
        })

    # 9. Prompt Assembly
    primary_domain = routed_domains[0] if routed_domains else None
    system_prompt = prompt_factory.get_system_prompt(answer_language=target_lang, domain=primary_domain)
    
    formatted_evidence = context_manager.format_evidence(best_chunks)
    formatted_history = context_manager.format_chat_history(prior_history, max_turns=6)
    
    user_prompt = prompt_factory.build_user_prompt(
        question=req.question,
        formatted_evidence=formatted_evidence,
        formatted_history=formatted_history,
        answer_language=target_lang
    )

    # 10. Streaming generator
    async def event_generator() -> AsyncGenerator[str, None]:
        full_answer = []

        # Yield metadata event (rewritten query, Jev domains, and sources)
        init_event = {
            "type": "metadata",
            "original_question": req.question,
            "rewritten_query": rewritten_query,
            "routed_domains": routed_domains,
            "sources": sources,
            "answer_language": target_lang
        }
        yield f"data: {json.dumps(init_event)}\n\n"

        # Stream token chunks from Gemini
        async for token in llm_service.stream_generation(system_prompt, user_prompt):
            full_answer.append(token)
            chunk_event = {
                "type": "token",
                "content": token
            }
            yield f"data: {json.dumps(chunk_event)}\n\n"

        complete_text = "".join(full_answer)

        # Save assistant answer to chat history
        await ConversationService.add_message(
            conversation_id=req.conversation_id,
            role="assistant",
            content=complete_text,
            rewritten_question=rewritten_query,
            answer_language=target_lang,
            sources=sources
        )

        done_event = {
            "type": "done",
            "status": "completed"
        }
        yield f"data: {json.dumps(done_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

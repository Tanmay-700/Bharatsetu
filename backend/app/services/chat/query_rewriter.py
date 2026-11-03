from typing import List, Dict
from app.core.config import settings
from app.core.logger import logger

class QueryRewriter:
    """
    Resolves pronouns, coreferences, and conversational ellipsis in multi-turn dialogues.
    Turns questions like "What is its SI unit?" into "What is the SI unit of electric current?".
    """

    @classmethod
    async def rewrite_if_needed(
        cls,
        current_question: str,
        chat_history: List[Dict[str, str]]
    ) -> str:
        """
        Rewrites the current question into a self-contained query based on chat history.
        """
        if not chat_history:
            return current_question

        if not settings.GEMINI_API_KEY:
            return current_question

        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            # Format the last 4 turns for context
            history_text = "\n".join([
                f"{m['role'].capitalize()}: {m['content']}"
                for m in chat_history[-4:]
            ])

            prompt = f"""You are a query rewriting assistant for a retrieval system.
Given the recent conversation history and the user's latest question, determine if the question contains pronouns or references to previous context (like 'it', 'its', 'this policy', 'those rules', 'how many days', 'what about that?').

If it contains references, rewrite the question to be completely self-contained so that a vector search engine can retrieve the right documents without needing the previous chat.
If the question is already self-contained, return the question unchanged.

Do NOT answer the question. Only output the rewritten question in the exact same language as the user asked it.

Conversation History:
{history_text}

Latest User Question: "{current_question}"

Rewritten Query:"""

            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )

            rewritten = response.text.strip().strip('"').strip("'")
            if rewritten and len(rewritten) > 3:
                logger.info(f"Query rewriter: '{current_question}' -> '{rewritten}'")
                return rewritten
            return current_question

        except Exception as e:
            logger.warning(f"Query rewriter encountered error: {e}. Using original question.")
            return current_question

query_rewriter = QueryRewriter()

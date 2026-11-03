import asyncio
from typing import AsyncGenerator, Optional, List
from app.core.config import settings
from app.core.logger import logger

# Ordered list of models to try (primary first, then fallbacks)
FALLBACK_MODELS: List[str] = [
    "gemini-3.5-flash-lite",      # Fast, abundant free quota
    settings.GEMINI_MODEL,
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]
# Deduplicate while preserving order
FALLBACK_MODELS = list(dict.fromkeys(FALLBACK_MODELS))


class LLMService:
    """Handles communication with Google Gemini Free API for text generation and streaming."""

    @classmethod
    async def stream_generation(
        cls,
        system_prompt: str,
        user_prompt: str
    ) -> AsyncGenerator[str, None]:
        """
        Yields text tokens asynchronously for real-time SSE streaming.
        Includes automatic retry with backoff and multi-model failover.
        """
        if not settings.GEMINI_API_KEY:
            yield "\n[Notice: GEMINI_API_KEY is not configured in backend/.env. Please configure it to enable live Gemini answers.]\n\n"
            yield "Here is a preview based on the retrieved evidence:\n"
            yield "Based on the retrieved documents, the relevant evidence has been located and citations are attached below."
            return

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        gen_config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2048
        )

        last_error = ""

        for model_name in FALLBACK_MODELS:
            # Try streaming (up to 3 attempts per model with increasing backoff)
            for attempt in range(1, 4):
                try:
                    response = await client.aio.models.generate_content_stream(
                        model=model_name,
                        contents=full_prompt,
                        config=gen_config
                    )

                    has_tokens = False
                    async for chunk in response:
                        if chunk.text:
                            has_tokens = True
                            yield chunk.text

                    if has_tokens:
                        return  # Success!

                except Exception as e:
                    err_str = str(e)
                    last_error = err_str
                    is_transient = "503" in err_str or "UNAVAILABLE" in err_str
                    is_not_found = "404" in err_str or "NOT_FOUND" in err_str
                    is_exhausted = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str

                    if is_not_found or is_exhausted:
                        logger.info(f"Model {model_name} unavailable or quota reached. Trying next model...")
                        break  # Skip immediately to next model

                    if is_transient and attempt < 3:
                        wait_time = 2 * attempt  # 2s, 4s
                        logger.info(f"503 on {model_name} (attempt {attempt}). Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"Streaming failed on {model_name} attempt {attempt}: {err_str[:120]}")
                        break

            # Try non-streaming fallback for this model
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                if res.text:
                    yield res.text
                    return  # Success!
            except Exception as e2:
                err_str2 = str(e2)
                last_error = err_str2
                is_not_found = "404" in err_str2 or "NOT_FOUND" in err_str2
                if is_not_found:
                    continue  # Try next model
                logger.warning(f"Non-streaming fallback failed on {model_name}: {err_str2[:120]}")
                await asyncio.sleep(2)

        # All models exhausted
        yield "\n[All Gemini models are temporarily experiencing high demand. Please wait 10-15 seconds and resend your message.]"

    @classmethod
    async def generate_text(
        cls,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Non-streaming generation for summaries and translations with multi-model failover.
        """
        if not settings.GEMINI_API_KEY:
            return "Gemini API key is not configured."

        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        contents = prompt
        if system_instruction:
            contents = f"{system_instruction}\n\n{prompt}"

        for model_name in FALLBACK_MODELS:
            for attempt in range(1, 3):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents
                    )
                    return response.text.strip()
                except Exception as e:
                    err_str = str(e)
                    if "404" in err_str or "NOT_FOUND" in err_str:
                        break  # Try next model
                    if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < 2:
                        await asyncio.sleep(2)
                        continue
                    logger.error(f"Gemini API error on {model_name}: {err_str[:120]}")
                    break

        return "Error: All Gemini models are temporarily unavailable. Please try again in a few seconds."

llm_service = LLMService()

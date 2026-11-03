"""Translation package: dedicated passage translation using Gemini"""
from typing import Dict
from app.core.config import settings
from app.core.logger import logger
from app.services.generation.llm import llm_service

class TranslationService:
    """Dedicated passage and chunk translation service."""

    @staticmethod
    async def translate_text(text: str, source_lang: str, target_lang: str) -> Dict[str, str]:
        target_name = settings.SUPPORTED_LANGUAGES.get(target_lang, target_lang)
        source_name = settings.SUPPORTED_LANGUAGES.get(source_lang, "Original Language")

        prompt = f"""Translate the following text accurately and faithfully from {source_name} into {target_name}.
Preserve all factual meaning, technical terms, and clause/section numbers.
Do NOT add extra explanations or commentary. Return ONLY the translated text.

Text to translate:
\"\"\"{text}\"\"\"
"""
        translated = await llm_service.generate_text(prompt=prompt)
        return {
            "original_text": text,
            "translated_text": translated,
            "source_language": source_lang,
            "target_language": target_lang
        }

translation_service = TranslationService()

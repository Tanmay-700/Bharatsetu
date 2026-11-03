import json
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logger import logger
from app.services.retrieval.vector_store import vector_store

class JevRouter:
    """
    Jev Dynamic Domain Router.
    Analyzes student/user questions across any language and routes them
    to the relevant knowledge domain(s) without blindly discarding documents.
    """

    @classmethod
    async def route(
        cls,
        question: str,
        available_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Classifies the incoming question into one or more active domains.
        Returns:
            {"domains": List[str], "confidence": float, "explanation": str}
        """
        if available_domains is None:
            available_domains = vector_store.get_all_domains()

        # If 0 or 1 domain exists, no routing needed
        if not available_domains:
            return {"domains": [], "confidence": 1.0, "explanation": "No domains registered yet."}
        if len(available_domains) == 1:
            return {"domains": available_domains, "confidence": 1.0, "explanation": "Single active domain."}

        # If Gemini API key is not configured, fall back to searching all domains safely
        if not settings.GEMINI_API_KEY:
            logger.info("Gemini API key not configured; Jev falling back to all domains.")
            return {
                "domains": available_domains,
                "confidence": 0.5,
                "explanation": "Fallback: all domains queried (no API key configured)."
            }

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            prompt = f"""You are Jev, an intelligent domain router for a multilingual knowledge base.
Your job is to examine the user query (which may be in English, Hindi, Odia, Tamil, Kannada, Marathi, Punjabi, Gujarati, etc.)
and determine which of the available domains it belongs to.

Available Domains: {json.dumps(available_domains)}

User Query: "{question}"

Instructions:
1. Identify the semantic subject or topic of the question.
2. Select 1 to 2 most relevant domains from the Available Domains list.
3. If the question spans multiple domains (e.g. Physical Chemistry or IT HR policy), select all relevant ones.
4. If you are uncertain or the question is too broad, include all plausible domains.
5. Return ONLY a valid JSON object matching this schema:
{{
  "selected_domains": ["Domain1", ...],
  "confidence": 0.95,
  "explanation": "Brief reason for choice"
}}
"""

            response = None
            for model_name in ["gemini-3.5-flash-lite", settings.GEMINI_MODEL, "gemini-3.8-flash", "gemini-3.6-flash"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.0
                        )
                    )
                    if response and response.text:
                        break
                except Exception as me:
                    logger.info(f"Jev router model {model_name} failed: {me}. Trying next model...")

            if not response or not response.text:
                return {"domains": available_domains, "confidence": 0.5, "explanation": "Fallback to all domains."}

            result_text = response.text.strip()
            data = json.loads(result_text)
            
            selected = data.get("selected_domains", [])
            # Filter to ensure only valid available domains are kept
            valid_selected = [d for d in selected if d in available_domains]
            if not valid_selected:
                valid_selected = available_domains # Safe fallback

            logger.info(f"Jev routed query '{question[:30]}...' -> {valid_selected}")
            return {
                "domains": valid_selected,
                "confidence": float(data.get("confidence", 0.9)),
                "explanation": data.get("explanation", "Domain routed by Jev")
            }

        except Exception as e:
            logger.warning(f"Jev routing encountered an error: {e}. Falling back to all domains.")
            return {
                "domains": available_domains,
                "confidence": 0.5,
                "explanation": f"Fallback to all domains due to router error: {str(e)}"
            }

jev_router = JevRouter()

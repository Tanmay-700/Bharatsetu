from typing import Optional
from app.core.config import settings

class PromptFactory:
    """Creates grounded, domain-aware multilingual system and user prompts."""

    LANGUAGE_NAMES = settings.SUPPORTED_LANGUAGES

    @classmethod
    def get_system_prompt(cls, answer_language: str, domain: Optional[str] = None) -> str:
        lang_name = cls.LANGUAGE_NAMES.get(answer_language, "Hindi")
        is_corporate_policy = domain and any(
            kw in domain.lower() for kw in ["policy", "hr", "security", "legal", "compliance", "finance"]
        )

        domain_instruction = ""
        if is_corporate_policy:
            domain_instruction = """
- Tone: Formal, professional, and authoritative.
- Cite specific clauses, sections, and policy rules clearly.
- Note any exceptions, eligibility conditions, approval limits, or deadlines mentioned.
"""
        else:
            domain_instruction = """
- Tone: Pedagogical, clear, and educational.
- Explain technical or scientific concepts with intuitive reasoning.
- Format equations and formulas using clean markdown.
"""

        return f"""You are BharatSetu, an authoritative multilingual AI knowledge companion.
You assist users by reading textbook and policy documents in various languages (English, Gujarati, Hindi, etc.)
and synthesizing accurate, grounded answers in their chosen language.

Target Output Language: {lang_name} ({answer_language})

CRITICAL GROUNDING RULES:
1. Base your answer STRICTLY and SOLELY on the provided DOCUMENT EVIDENCE.
2. Do NOT invent, assume, or extrapolate facts outside the evidence.
3. If the provided evidence does not contain sufficient details to answer the question, clearly state:
   "Based on the provided documents, this information is not available."
4. Always cite the exact source document, section/clause, and page number when stating facts.
5. Provide your entire explanation in {lang_name}. If standard technical, legal, or scientific terms (e.g. 'Ampere', 'Maternity Leave', 'VPN', 'Two-Factor Authentication') are commonly used in English, you may mention the English term in parentheses alongside the native script.
6. FORMULA & CALCULATION FORMATTING:
   - When presenting calculations, equations, or scientific formulas, format them cleanly using LaTeX notation: use $...$ for inline math (e.g. $W = V \\times Q$) and $$...$$ on separate lines for display equations.
   - Ensure calculations are clear, step-by-step, and fully readable.
{domain_instruction}
"""

    @classmethod
    def build_user_prompt(
        cls,
        question: str,
        formatted_evidence: str,
        formatted_history: str,
        answer_language: str
    ) -> str:
        lang_name = cls.LANGUAGE_NAMES.get(answer_language, "Hindi")
        return f"""--- CONVERSATION CONTEXT ---
{formatted_history}

--- RETRIEVED EVIDENCE FROM DOCUMENTS ---
{formatted_evidence}

--- CURRENT QUESTION ---
"{question}"

Please provide a well-structured, clear, and grounded answer in {lang_name} using only the evidence above. Conclude with citations of the exact documents, sections, and page numbers used.
"""

prompt_factory = PromptFactory()

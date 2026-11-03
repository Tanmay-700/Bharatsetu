from typing import List, Dict, Any
from app.core.config import settings
from app.core.logger import logger

class ContextManager:
    """Manages chat context sliding windows, token boundaries, and evidence formatting."""

    @staticmethod
    def format_evidence(evidence_chunks: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved and reranked chunks into structured citation blocks for the LLM.
        """
        if not evidence_chunks:
            return "No relevant textbook or policy documents were retrieved."

        formatted_blocks = []
        for idx, chunk in enumerate(evidence_chunks, start=1):
            meta = chunk.get("metadata", {})
            doc_name = meta.get("document_name", "Unknown Document")
            domain = meta.get("domain", "General")
            section = meta.get("section", "Section N/A")
            page = meta.get("page_number", "N/A")
            content = chunk.get("content", "").strip()

            block = (
                f"--- EVIDENCE [{idx}] ---\n"
                f"Document: {doc_name}\n"
                f"Domain: {domain}\n"
                f"Section/Clause: {section}\n"
                f"Page: {page}\n"
                f"Content:\n{content}"
            )
            formatted_blocks.append(block)

        return "\n\n".join(formatted_blocks)

    @staticmethod
    def format_chat_history(messages: List[Dict[str, str]], max_turns: int = 6) -> str:
        """Formats the sliding window of recent conversation turns."""
        if not messages:
            return "No previous conversation."

        recent = messages[-max_turns:]
        formatted = []
        for m in recent:
            role = "Student/User" if m["role"] == "user" else "BharatSetu Assistant"
            formatted.append(f"{role}: {m['content']}")

        return "\n".join(formatted)

context_manager = ContextManager()

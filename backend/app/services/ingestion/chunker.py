import re
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logger import logger
from app.services.ingestion.parser import PageData

class DocumentChunker:
    """Performs semantic, section-aware chunking on extracted PDF pages."""

    # Common section/clause header patterns (for policies, legal docs, and textbooks)
    SECTION_PATTERNS = [
        re.compile(r"^(Clause|Section|Article|Chapter|Part)\s+[\d\.\w]+.*$", re.IGNORECASE),
        re.compile(r"^\d+(\.\d+)*\s+[A-Z][\w\s]+$"), # e.g. "4.2 Leave Entitlements"
        re.compile(r"^[A-Z\s]{4,40}$"), # e.g. "CODE OF CONDUCT"
    ]

    @classmethod
    def _is_section_header(cls, line: str) -> bool:
        line_clean = line.strip()
        if len(line_clean) < 3 or len(line_clean) > 100:
            return False
        for pattern in cls.SECTION_PATTERNS:
            if pattern.match(line_clean):
                return True
        return False

    @classmethod
    def chunk_document(
        cls,
        pages: List[PageData],
        document_id: str,
        document_name: str,
        domain: str,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Chunks extracted pages into semantic chunks with metadata.
        Target: ~300-500 words per chunk with overlap.
        """
        chunks: List[Dict[str, Any]] = []
        current_section = "General Overview"

        for page in pages:
            page_text = page.text
            if not page_text.strip():
                continue

            lines = page_text.splitlines()
            paragraphs: List[str] = []
            current_para = []

            for line in lines:
                clean_line = line.strip()
                if not clean_line:
                    if current_para:
                        paragraphs.append(" ".join(current_para))
                        current_para = []
                    continue

                if cls._is_section_header(clean_line):
                    current_section = clean_line
                    if current_para:
                        paragraphs.append(" ".join(current_para))
                        current_para = []
                    paragraphs.append(clean_line)
                else:
                    current_para.append(clean_line)

            if current_para:
                paragraphs.append(" ".join(current_para))

            # Group paragraphs into chunks of target size (~350 words)
            chunk_text = ""
            chunk_idx = 1
            words_in_chunk = 0

            for para in paragraphs:
                para_words = len(para.split())
                
                # If adding this paragraph exceeds target chunk size and chunk is not empty
                if words_in_chunk + para_words > settings.CHUNK_SIZE and chunk_text:
                    chunk_id = f"{document_id}_p{page.page_number}_c{chunk_idx}"
                    chunks.append({
                        "id": chunk_id,
                        "document_id": document_id,
                        "document_name": document_name,
                        "domain": domain,
                        "section": current_section,
                        "page_number": page.page_number,
                        "content": chunk_text.strip(),
                        "token_count": len(chunk_text.split()),
                        "language": language
                    })
                    chunk_idx += 1
                    
                    # Create overlap: take last ~50 words of previous chunk
                    prev_words = chunk_text.split()
                    overlap = " ".join(prev_words[-settings.CHUNK_OVERLAP:]) if len(prev_words) >= settings.CHUNK_OVERLAP else ""
                    chunk_text = (overlap + " " + para).strip() if overlap else para
                    words_in_chunk = len(chunk_text.split())
                else:
                    if chunk_text:
                        chunk_text += "\n" + para
                    else:
                        chunk_text = para
                    words_in_chunk += para_words

            # Add any remaining text on the page
            if chunk_text.strip():
                chunk_id = f"{document_id}_p{page.page_number}_c{chunk_idx}"
                chunks.append({
                    "id": chunk_id,
                    "document_id": document_id,
                    "document_name": document_name,
                    "domain": domain,
                    "section": current_section,
                    "page_number": page.page_number,
                    "content": chunk_text.strip(),
                    "token_count": len(chunk_text.split()),
                    "language": language
                })

        logger.info(f"Chunked document '{document_name}' into {len(chunks)} chunks across {len(pages)} pages.")
        return chunks

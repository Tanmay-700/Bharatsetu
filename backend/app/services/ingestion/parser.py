from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from app.core.logger import logger

@dataclass
class PageData:
    page_number: int
    text: str

class PDFParser:
    """Extracts text and metadata from PDF files using pdfplumber and pypdf."""

    @staticmethod
    def parse_pdf(file_path: Path) -> List[PageData]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        pages: List[PageData] = []
        logger.info(f"Starting extraction for PDF: {file_path.name}")

        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    page_num = idx + 1
                    text = page.extract_text() or ""
                    
                    # If page text is very sparse, try extracting words
                    if not text.strip():
                        words = page.extract_words()
                        if words:
                            text = " ".join([w["text"] for w in words])
                    
                    # Clean up excessive whitespace
                    cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
                    pages.append(PageData(page_number=page_num, text=cleaned_text))
            
            logger.info(f"Successfully extracted {len(pages)} pages using pdfplumber.")
            return pages
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed or had warnings: {e}. Falling back to pypdf.")

        # Fallback to pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            pages = []
            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                text = page.extract_text() or ""
                cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
                pages.append(PageData(page_number=page_num, text=cleaned_text))
            logger.info(f"Successfully extracted {len(pages)} pages using pypdf fallback.")
            return pages
        except Exception as e:
            logger.error(f"Both pdfplumber and pypdf failed to parse PDF: {e}")
            raise e

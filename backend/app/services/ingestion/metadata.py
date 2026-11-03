import hashlib
from pathlib import Path
from typing import Optional
from app.core.config import settings

class MetadataExtractor:
    """Utilities for document hashing, language detection, and metadata extraction."""

    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        """Compute SHA256 hash of a file for idempotency detection."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def infer_language_from_text(sample_text: str) -> str:
        """Heuristic language detection based on Unicode script ranges."""
        for char in sample_text[:1000]:
            code = ord(char)
            # Devanagari (Hindi / Marathi)
            if 0x0900 <= code <= 0x097F:
                return "hi"
            # Gujarati
            if 0x0A80 <= code <= 0x0AFF:
                return "gu"
            # Tamil
            if 0x0B80 <= code <= 0x0BFF:
                return "ta"
            # Odia
            if 0x0B00 <= code <= 0x0B7F:
                return "od"
            # Kannada
            if 0x0C80 <= code <= 0x0CFF:
                return "kn"
            # Gurmukhi (Punjabi)
            if 0x0A00 <= code <= 0x0A7F:
                return "pa"

        return "en"

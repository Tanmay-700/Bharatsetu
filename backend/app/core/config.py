import os
from pathlib import Path
from typing import Dict, List

# Manually load .env from backend/ or root/ to guarantee keys are loaded
BASE_DIR = Path(__file__).resolve().parent.parent.parent
for env_candidate in [BASE_DIR / ".env", BASE_DIR.parent / ".env", Path(".env")]:
    if env_candidate.exists():
        try:
            with open(env_candidate, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'").strip('"')
                    if k and (k not in os.environ or not os.environ[k]):
                        if k == "CHROMA_PERSIST_DIRECTORY":
                            v = str((BASE_DIR / "data" / "vectordb").resolve())
                        os.environ[k] = v
        except Exception:
            pass

try:
    from pydantic_settings import BaseSettings
    class ConfigBase(BaseSettings):
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            extra = "ignore"
except ImportError:
    from pydantic import BaseModel
    class ConfigBase(BaseModel):
        pass

class Settings(ConfigBase):
    PROJECT_NAME: str = "BharatSetu"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Google Gemini API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    # Multilingual Local Models
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
    RERANKER_MODEL_NAME: str = os.getenv("RERANKER_MODEL_NAME", "BAAI/bge-reranker-v2-m3")

    # Data directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    CHROMA_PERSIST_DIRECTORY: Path = BASE_DIR / "data" / "vectordb"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR / 'bharatsetu.db'}"

    # Chunking & Retrieval Parameters
    CHUNK_SIZE: int = 200
    CHUNK_OVERLAP: int = 40
    MAX_BATCH_SIZE: int = 32
    TOP_K_RETRIEVAL: int = 30
    TOP_N_RERANK: int = 8

    # Default User
    DEFAULT_USER_ID: str = "user_1"

    # Supported Languages (8 Indic Languages + English)
    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "en": "English",
        "hi": "Hindi",
        "od": "Odia",
        "ta": "Tamil",
        "kn": "Kannada",
        "mr": "Marathi",
        "pa": "Punjabi",
        "gu": "Gujarati"
    }

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)

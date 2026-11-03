import os
from typing import List
from app.core.config import settings
from app.core.logger import logger


class EmbeddingService:
    """
    Multilingual dense embedding service.
    Priority: 1) Local bge-m3 (if sentence-transformers installed)
              2) Gemini text-embedding-004 API (free, uses same API key)
              3) Hash fallback (last resort)
    """
    _instance = None
    _model = None
    _mode = None  # "local", "gemini", "fallback"
    _gemini_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._mode is not None:
            return

        # Try 1: Local sentence-transformers (bge-m3)
        try:
            import torch
            num_cores = os.cpu_count() or 4
            torch.set_num_threads(min(num_cores, 12))
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local embedding model: {settings.EMBEDDING_MODEL_NAME} on CPU...")
            try:
                self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device="cpu", model_kwargs={"local_files_only": True})
            except Exception:
                self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device="cpu")
            self._mode = "local"
            logger.info(f"Local embedding model loaded successfully on CPU with {torch.get_num_threads()} threads.")
            return
        except Exception as e:
            logger.info(f"Local sentence-transformers not available: {e}")

        # Try 2: Gemini Embedding API (free, same API key)
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                # Quick test to verify the API works
                test_result = self._gemini_client.models.embed_content(
                    model="gemini-embedding-001",
                    contents="test"
                )
                if test_result and test_result.embeddings:
                    self._mode = "gemini"
                    logger.info("Using Gemini text-embedding-004 API for embeddings (free tier).")
                    return
            except Exception as e:
                logger.warning(f"Gemini embedding API test failed: {e}")

        # Fallback: deterministic hash vectors
        self._mode = "fallback"
        logger.warning("No embedding engine available. Using hash-based fallback (search quality will be poor).")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates dense embeddings for a batch of text chunks."""
        self._load_model()
        if not texts:
            return []

        if self._mode == "local":
            embeddings = self._model.encode(
                texts,
                batch_size=settings.MAX_BATCH_SIZE,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            return embeddings.tolist()

        if self._mode == "gemini":
            return self._embed_via_gemini(texts)

        # Fallback: hash-based
        return self._hash_embed(texts)

    def _embed_via_gemini(self, texts: List[str]) -> List[List[float]]:
        """Batch embed using Gemini's free text-embedding-004 model."""
        all_embeddings = []
        batch_size = 20  # Gemini supports up to ~100 texts per call, but keep batches small

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Filter out empty strings (API rejects them)
            processed_batch = [t if t.strip() else "empty" for t in batch]

            try:
                result = self._gemini_client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=processed_batch
                )
                if result and result.embeddings:
                    for emb in result.embeddings:
                        all_embeddings.append(list(emb.values))
                else:
                    # If somehow no embeddings returned, use hash for this batch
                    all_embeddings.extend(self._hash_embed(batch))
            except Exception as e:
                logger.warning(f"Gemini embedding batch failed: {e}. Using hash fallback for this batch.")
                all_embeddings.extend(self._hash_embed(batch))

        return all_embeddings

    def _hash_embed(self, texts: List[str]) -> List[List[float]]:
        """Deterministic hash-based fallback (3072 dims to match gemini-embedding-001)."""
        import hashlib
        vectors = []
        for t in texts:
            h = int(hashlib.sha256(t.encode()).hexdigest(), 16)
            vec = [((h >> (i % 64)) & 1) * 0.1 - 0.05 for i in range(3072)]
            vectors.append(vec)
        return vectors

    def embed_query(self, query: str) -> List[float]:
        """Generates a dense embedding for a single user query."""
        results = self.embed_documents([query])
        return results[0] if results else []


embedding_service = EmbeddingService()

import os
import torch
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logger import logger

class RerankerService:
    """
    Cross-lingual neural reranker powered by BAAI/bge-reranker-v2-m3.
    Rescores candidate chunks based on deep query-document cross-attention.
    """
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RerankerService, cls).__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            if settings.RERANKER_MODEL_NAME.lower() in ["none", "fallback", "cosine", ""]:
                self._model = "fallback"
                logger.info("Using fast vector score sorting for reranking.")
                return

            logger.info(f"Loading reranker model: {settings.RERANKER_MODEL_NAME} on CPU...")
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(settings.RERANKER_MODEL_NAME, device="cpu")
                logger.info("Reranker model loaded successfully on CPU.")
            except Exception as e:
                logger.warning(f"Could not load HuggingFace reranker '{settings.RERANKER_MODEL_NAME}': {e}. Using vector score sorting.")
                self._model = "fallback"

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Reranks retrieved candidate chunks using deep cross-attention.
        """
        if not candidates:
            return []

        if len(candidates) <= top_n and self._model == "fallback":
            return candidates

        self._load_model()

        if self._model == "fallback":
            # Sort by vector similarity score
            sorted_candidates = sorted(candidates, key=lambda x: x.get("score", 0.0), reverse=True)
            return sorted_candidates[:top_n]

        try:
            pairs = [[query, cand["content"]] for cand in candidates]
            scores = self._model.predict(pairs)

            for cand, score in zip(candidates, scores):
                cand["rerank_score"] = float(score)

            sorted_candidates = sorted(candidates, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
            return sorted_candidates[:top_n]
        except Exception as e:
            logger.warning(f"Cross-encoder reranking encountered error: {e}. Falling back to vector score.")
            return sorted(candidates, key=lambda x: x.get("score", 0.0), reverse=True)[:top_n]

reranker_service = RerankerService()

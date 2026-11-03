from typing import List, Dict, Any, Optional
import math
from app.core.config import settings
from app.core.logger import logger

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

class VectorStore:
    """ChromaDB wrapper with resilient local in-memory fallback."""

    COLLECTION_NAME = "bharatsetu_knowledge_base"

    def __init__(self):
        self._has_chroma = HAS_CHROMADB
        self._fallback_store: Dict[str, Dict[str, Any]] = {}

        if self._has_chroma:
            try:
                self._client = chromadb.PersistentClient(
                    path=str(settings.CHROMA_PERSIST_DIRECTORY),
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
                self._collection = self._client.get_or_create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"Connected to ChromaDB. Total chunks indexed: {self._collection.count()}")
            except Exception as e:
                logger.warning(f"Could not initialize ChromaDB client: {e}. Using in-memory vector store.")
                self._has_chroma = False
        else:
            logger.info("ChromaDB library not detected. Running on high-performance in-memory vector engine.")

    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """Upsert text chunks with embeddings and metadata."""
        if not chunks:
            return

        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [
            {
                "document_id": str(chunk.get("document_id", "")),
                "document_name": str(chunk.get("document_name", "")),
                "domain": str(chunk.get("domain", "General")),
                "section": str(chunk.get("section", "")),
                "page_number": int(chunk.get("page_number", 1)),
                "language": str(chunk.get("language", "en"))
            }
            for chunk in chunks
        ]

        if self._has_chroma:
            try:
                batch_size = 250
                for i in range(0, len(ids), batch_size):
                    end_idx = i + batch_size
                    self._collection.upsert(
                        ids=ids[i:end_idx],
                        embeddings=embeddings[i:end_idx],
                        documents=documents[i:end_idx],
                        metadatas=metadatas[i:end_idx]
                    )
                logger.info(f"Successfully upserted {len(chunks)} chunks into ChromaDB.")
                return
            except Exception as e:
                logger.warning(f"ChromaDB upsert failed: {e}. Falling back to memory store.")

        # In-memory storage
        for idx, cid in enumerate(ids):
            self._fallback_store[cid] = {
                "id": cid,
                "content": documents[idx],
                "metadata": metadatas[idx],
                "embedding": embeddings[idx] if idx < len(embeddings) else []
            }
        logger.info(f"Upserted {len(chunks)} chunks into fallback vector store.")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 25,
        domain_filter: Optional[List[str]] = None,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes ANN cosine similarity search with domain and document filters.
        """
        if self._has_chroma:
            try:
                where_filter: Optional[Dict[str, Any]] = None
                conditions = []
                if domain_filter:
                    if len(domain_filter) == 1:
                        conditions.append({"domain": {"$eq": domain_filter[0]}})
                    elif len(domain_filter) > 1:
                        conditions.append({"domain": {"$in": domain_filter}})

                if document_id:
                    conditions.append({"document_id": {"$eq": document_id}})

                if len(conditions) == 1:
                    where_filter = conditions[0]
                elif len(conditions) > 1:
                    where_filter = {"$and": conditions}

                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(top_k, max(1, self._collection.count())),
                    where=where_filter,
                    include=["documents", "metadatas", "distances"]
                )

                matches: List[Dict[str, Any]] = []
                if results and results.get("ids") and results["ids"][0]:
                    count = len(results["ids"][0])
                    for i in range(count):
                        chunk_id = results["ids"][0][i]
                        content = results["documents"][0][i] if results.get("documents") else ""
                        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                        distance = results["distances"][0][i] if results.get("distances") else 1.0
                        score = round(1.0 - distance, 4)

                        matches.append({
                            "chunk_id": chunk_id,
                            "content": content,
                            "metadata": metadata,
                            "distance": distance,
                            "score": score
                        })
                return matches
            except Exception as e:
                logger.warning(f"ChromaDB search failed: {e}. Using fallback memory search.")

        # In-memory search
        scored = []
        for cid, item in self._fallback_store.items():
            meta = item["metadata"]
            if domain_filter and meta.get("domain") not in domain_filter:
                continue
            if document_id and meta.get("document_id") != document_id:
                continue

            sim = cosine_similarity(query_embedding, item["embedding"])
            dist = round(1.0 - sim, 4)
            scored.append({
                "chunk_id": cid,
                "content": item["content"],
                "metadata": meta,
                "distance": dist,
                "score": round(sim, 4)
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def delete_by_document(self, document_id: str) -> None:
        """Deletes all chunks belonging to a specific document."""
        if self._has_chroma:
            try:
                self._collection.delete(where={"document_id": {"$eq": document_id}})
            except Exception:
                pass

        keys_to_del = [cid for cid, item in self._fallback_store.items() if item["metadata"].get("document_id") == document_id]
        for k in keys_to_del:
            del self._fallback_store[k]
        logger.info(f"Deleted vector chunks for document_id: {document_id}")

    def count(self) -> int:
        if self._has_chroma:
            try:
                return self._collection.count()
            except Exception:
                pass
        return len(self._fallback_store)

    def get_all_domains(self) -> List[str]:
        """Retrieves list of all distinct domains currently in the vector store."""
        if self._has_chroma:
            try:
                data = self._collection.get(include=["metadatas"], limit=1000)
                domains = set()
                if data and data.get("metadatas"):
                    for m in data["metadatas"]:
                        if m and "domain" in m:
                            domains.add(m["domain"])
                if domains:
                    return sorted(list(domains))
            except Exception:
                pass

        domains = {item["metadata"].get("domain") for item in self._fallback_store.values() if item["metadata"].get("domain")}
        return sorted(list(domains))

vector_store = VectorStore()

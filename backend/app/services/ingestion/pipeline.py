from pathlib import Path
from typing import Dict, Any
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.logger import logger
from app.models.models import Document, Chunk
from app.services.ingestion.parser import PDFParser
from app.services.ingestion.chunker import DocumentChunker
from app.services.retrieval.embeddings import embedding_service
from app.services.retrieval.vector_store import vector_store

class IngestionPipeline:
    """Orchestrates end-to-end PDF processing, semantic chunking, embedding, and vector indexing."""

    @staticmethod
    async def process_document_background(
        document_id: str,
        file_path: Path,
        filename: str,
        domain: str,
        document_type: str,
        language: str = "en"
    ) -> None:
        """
        Background worker function executed after file upload.
        Updates SQLite and ChromaDB.
        """
        async with AsyncSessionLocal() as session:
            try:
                # 1. Fetch document from DB
                res = await session.execute(select(Document).where(Document.id == document_id))
                doc = res.scalar_one_or_none()
                if not doc:
                    logger.error(f"Document {document_id} not found in database for ingestion.")
                    return

                logger.info(f"Processing document {filename} ({document_id}) in domain '{domain}'...")

                # 2. Extract pages from PDF
                pages = PDFParser.parse_pdf(file_path)
                doc.total_pages = len(pages)
                await session.commit()

                # 3. Semantic chunking
                chunks_data = DocumentChunker.chunk_document(
                    pages=pages,
                    document_id=document_id,
                    document_name=filename,
                    domain=domain,
                    language=language
                )

                if not chunks_data:
                    doc.status = "failed"
                    doc.error_message = "No readable text could be extracted from PDF."
                    await session.commit()
                    return

                # 4. Generate embeddings via bge-m3
                chunk_texts = [c["content"] for c in chunks_data]
                logger.info(f"Embedding {len(chunk_texts)} chunks for '{filename}' on CPU...")
                embeddings = embedding_service.embed_documents(chunk_texts)

                # 5. Upsert to ChromaDB
                vector_store.upsert_chunks(chunks_data, embeddings)

                # 6. Save chunk metadata to SQLite
                for c in chunks_data:
                    chunk_obj = Chunk(
                        id=c["id"],
                        document_id=document_id,
                        domain=domain,
                        section=c.get("section"),
                        page_number=c.get("page_number", 1),
                        content=c["content"],
                        token_count=c.get("token_count", 0)
                    )
                    session.add(chunk_obj)

                # 7. Update document status to completed
                doc.total_chunks = len(chunks_data)
                doc.status = "completed"
                await session.commit()
                logger.info(f"Ingestion completed successfully for '{filename}'. Total chunks: {len(chunks_data)}")

            except Exception as e:
                logger.error(f"Error during document ingestion pipeline: {e}")
                await session.rollback()
                try:
                    res = await session.execute(select(Document).where(Document.id == document_id))
                    doc = res.scalar_one_or_none()
                    if doc:
                        doc.status = "failed"
                        doc.error_message = str(e)
                        await session.commit()
                except Exception as db_err:
                    logger.error(f"Failed to update document failure status: {db_err}")

import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy import select, delete

from app.core.config import settings
from app.core.logger import logger
from app.core.database import AsyncSessionLocal
from app.models.models import Document
from app.schemas.schemas import DocumentResponse
from app.services.ingestion.metadata import MetadataExtractor
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.retrieval.vector_store import vector_store

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    domain: str = Form("General"),
    document_type: str = Form("Policy"),
    language: str = Form("en")
):
    """
    Upload an educational or corporate PDF for asynchronous ingestion.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = settings.UPLOAD_DIR / file.filename

    # Save uploaded file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_hash = MetadataExtractor.compute_file_hash(file_path)

    async with AsyncSessionLocal() as session:
        # Check if already uploaded
        existing = await session.execute(select(Document).where(Document.file_hash == file_hash))
        existing_doc = existing.scalar_one_or_none()
        if existing_doc and existing_doc.status == "completed":
            logger.info(f"File {file.filename} with hash {file_hash} already exists. Skipping duplicate.")
            return existing_doc

        doc = Document(
            filename=file.filename,
            file_path=str(file_path),
            domain=domain.strip(),
            document_type=document_type.strip(),
            language=language.strip(),
            status="processing",
            file_hash=file_hash
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        doc_id = doc.id

    # Launch ingestion pipeline in the background
    background_tasks.add_task(
        IngestionPipeline.process_document_background,
        document_id=doc_id,
        file_path=file_path,
        filename=file.filename,
        domain=domain.strip(),
        document_type=document_type.strip(),
        language=language.strip()
    )

    return doc

@router.get("", response_model=List[DocumentResponse])
async def list_documents():
    """List all indexed documents and their statuses."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Document).order_by(Document.uploaded_at.desc()))
        docs = res.scalars().all()
        return docs

@router.get("/domains", response_model=List[str])
async def list_active_domains():
    """List all unique domains currently indexed in the knowledge base."""
    return vector_store.get_all_domains()

@router.get("/{document_id}/status")
async def get_document_status(document_id: str):
    """Check processing status of a specific document."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Document).where(Document.id == document_id))
        doc = res.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return {
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status,
            "total_pages": doc.total_pages,
            "total_chunks": doc.total_chunks,
            "error_message": doc.error_message
        }

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from SQLite and ChromaDB."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Document).where(Document.id == document_id))
        doc = res.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete physical file if exists
        try:
            p = Path(doc.file_path)
            if p.exists():
                p.unlink()
        except Exception as e:
            logger.warning(f"Could not delete physical file: {e}")

        # Delete from ChromaDB
        vector_store.delete_by_document(document_id)

        # Delete from SQLite
        await session.execute(delete(Document).where(Document.id == document_id))
        await session.commit()

    return {"status": "success", "message": f"Document {document_id} deleted successfully"}

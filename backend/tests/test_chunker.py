import pytest
from app.services.ingestion.parser import PageData
from app.services.ingestion.chunker import DocumentChunker

def test_chunker_basic():
    pages = [
        PageData(page_number=1, text="Section 1: Company Leave Policy\nEmployees are entitled to 20 days of paid annual leave."),
        PageData(page_number=2, text="Clause 2.1: Sick Leave\nSick leave of up to 10 days is permitted with medical certificates.")
    ]

    chunks = DocumentChunker.chunk_document(
        pages=pages,
        document_id="doc_test_1",
        document_name="LeavePolicy.pdf",
        domain="HR Policies",
        language="en"
    )

    assert len(chunks) >= 2
    assert chunks[0]["domain"] == "HR Policies"
    assert chunks[0]["document_id"] == "doc_test_1"
    assert "Section 1" in chunks[0]["section"] or "General" in chunks[0]["section"]
    assert chunks[1]["page_number"] == 2

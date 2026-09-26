import pytest
from apexforge.ingestion.document_loader import DocumentLoader
from apexforge.models.data_models import DocumentType, ProcessingStatus


def test_document_loader_sha3_hash():
    loader = DocumentLoader()
    doc = loader.load_from_text("sample.txt", "ApexForge Financial Document", DocumentType.TXT)
    assert doc.document_id.startswith("DOC-")
    assert len(doc.sha3_256_hash) == 64
    assert doc.processing_status == ProcessingStatus.PROCESSED
    assert "ApexForge" in doc.extracted_text


def test_csv_extraction():
    loader = DocumentLoader()
    csv_txt = "Sender,Receiver,Amount,Date\nShell Alpha,Vanguard,45000.00,2026-03-01\n"
    doc = loader.load_from_text("test.csv", csv_txt, DocumentType.CSV)
    assert doc.document_type == DocumentType.CSV
    assert "Shell Alpha" in doc.extracted_text

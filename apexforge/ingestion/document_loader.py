"""
Layer 1 — Document Ingestion Module
Ingests heterogeneous financial evidence files (PDF, Image, CSV, TXT, Email, Chat)
and produces normalized internal document representations with SHA3-256 provenance hashing.
"""

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Union, Dict, Any, List

from apexforge.models.data_models import (
    NormalizedDocument,
    DocumentType,
    ProcessingStatus,
)


class DocumentLoader:
    def __init__(self):
        pass

    @staticmethod
    def compute_sha3_256(content: bytes) -> str:
        """Computes SHA3-256 hash of raw document bytes for tamper-evident provenance."""
        return hashlib.sha3_256(content).hexdigest()

    def detect_document_type(self, filepath: Union[str, Path], raw_bytes: bytes) -> DocumentType:
        ext = Path(filepath).suffix.lower()
        if ext in [".pdf"]:
            return DocumentType.PDF
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return DocumentType.IMAGE
        elif ext in [".csv"]:
            return DocumentType.CSV
        elif ext in [".eml", ".email"]:
            return DocumentType.EMAIL
        elif ext in [".txt", ".log", ".md"]:
            # Check if text looks like email or chat
            text_snippet = raw_bytes[:1000].decode("utf-8", errors="ignore").lower()
            if "from:" in text_snippet and "to:" in text_snippet and "subject:" in text_snippet:
                return DocumentType.EMAIL
            elif "slack" in text_snippet or "chat" in text_snippet or "teams" in text_snippet or "whatsapp" in text_snippet:
                return DocumentType.CHAT
            return DocumentType.TXT
        elif ext in [".json"]:
            return DocumentType.CHAT
        else:
            return DocumentType.TXT

    def extract_raw_text(self, filepath: Union[str, Path], raw_bytes: bytes, doc_type: DocumentType) -> str:
        """Extracts text based on document type."""
        try:
            if doc_type in [DocumentType.TXT, DocumentType.EMAIL, DocumentType.CHAT]:
                return raw_bytes.decode("utf-8", errors="ignore")
            elif doc_type == DocumentType.CSV:
                # Format CSV for clean NLP extraction
                import pandas as pd
                import io
                df = pd.read_csv(io.BytesIO(raw_bytes))
                return df.to_string(index=False)
            elif doc_type == DocumentType.PDF:
                try:
                    import pypdf
                    reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
                    text_pages = []
                    for idx, page in enumerate(reader.pages):
                        page_txt = page.extract_text() or ""
                        text_pages.append(f"--- Page {idx + 1} ---\n{page_txt}")
                    return "\n".join(text_pages)
                except Exception:
                    # Fallback to plain text decoding
                    return raw_bytes.decode("utf-8", errors="ignore")
            elif doc_type == DocumentType.IMAGE:
                # OCR extraction or mock text payload if image contains embedded text string
                return self._extract_image_text(raw_bytes)
            else:
                return raw_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            return f"[ERROR Extracting Text from {filepath}: {str(e)}]"

    def _extract_image_text(self, raw_bytes: bytes) -> str:
        """Attempts OCR via pytesseract, with graceful fallback."""
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(raw_bytes))
            try:
                import pytesseract
                return pytesseract.image_to_string(img)
            except Exception:
                return f"[IMAGE DOCUMENT: {img.size[0]}x{img.size[1]} {img.format} - OCR Engine Standby]"
        except Exception as e:
            return f"[IMAGE ERROR: {str(e)}]"

    def load_document(
        self, filepath: Union[str, Path], document_id: str = None, override_text: str = None
    ) -> NormalizedDocument:
        path = Path(filepath)
        filename = path.name

        if path.exists():
            with open(path, "rb") as f:
                raw_bytes = f.read()
        else:
            raw_bytes = (override_text or "").encode("utf-8")

        sha3_hash = self.compute_sha3_256(raw_bytes)
        doc_type = self.detect_document_type(filepath, raw_bytes)

        if override_text is not None:
            text = override_text
        else:
            text = self.extract_raw_text(filepath, raw_bytes, doc_type)

        if not document_id:
            document_id = f"DOC-{sha3_hash[:8].upper()}"

        metadata = {
            "file_size_bytes": len(raw_bytes),
            "file_extension": path.suffix,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Extract extra email/chat/csv metadata headers if present
        if doc_type == DocumentType.EMAIL:
            lines = text.splitlines()
            for line in lines[:10]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    metadata[f"email_{k.strip().lower()}"] = v.strip()

        return NormalizedDocument(
            document_id=document_id,
            filename=filename,
            document_type=doc_type,
            source=str(path),
            ingestion_timestamp=datetime.now(timezone.utc).isoformat(),
            sha3_256_hash=sha3_hash,
            processing_status=ProcessingStatus.PROCESSED,
            extracted_text=text,
            metadata=metadata,
        )

    def load_from_text(self, filename: str, content: str, doc_type: DocumentType, document_id: str = None) -> NormalizedDocument:
        raw_bytes = content.encode("utf-8")
        sha3_hash = self.compute_sha3_256(raw_bytes)
        if not document_id:
            document_id = f"DOC-{sha3_hash[:8].upper()}"
        return NormalizedDocument(
            document_id=document_id,
            filename=filename,
            document_type=doc_type,
            source="text_input",
            ingestion_timestamp=datetime.now(timezone.utc).isoformat(),
            sha3_256_hash=sha3_hash,
            processing_status=ProcessingStatus.PROCESSED,
            extracted_text=content,
            metadata={"file_size_bytes": len(raw_bytes), "source_type": "direct_text"},
        )

"""
Layer 1 — Document Ingestion Module
Ingests heterogeneous financial evidence files (PDF, Images, CSV, Excel XLSX, Word DOCX, TXT, Email, JSON, Chat, etc.)
and produces normalized internal document representations with SHA3-256 provenance hashing.
"""

import hashlib
import io
import json
import os
import re
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
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif", ".webp"]:
            return DocumentType.IMAGE
        elif ext in [".csv", ".xlsx", ".xls", ".ods"]:
            return DocumentType.CSV
        elif ext in [".eml", ".email"]:
            return DocumentType.EMAIL
        elif ext in [".txt", ".log", ".md", ".rtf", ".docx", ".doc", ".html", ".xml"]:
            text_snippet = raw_bytes[:1000].decode("utf-8", errors="ignore").lower()
            if "from:" in text_snippet and "to:" in text_snippet and "subject:" in text_snippet:
                return DocumentType.EMAIL
            elif any(k in text_snippet for k in ["slack", "chat", "teams", "whatsapp", "conversation"]):
                return DocumentType.CHAT
            return DocumentType.TXT
        elif ext in [".json"]:
            return DocumentType.CHAT
        else:
            return DocumentType.TXT

    def extract_raw_text(self, filepath: Union[str, Path], raw_bytes: bytes, doc_type: DocumentType) -> str:
        """Extracts plain text across all supported file extensions."""
        ext = Path(filepath).suffix.lower()
        
        try:
            # 1. Word Documents (.docx)
            if ext in [".docx"]:
                try:
                    import docx
                    doc = docx.Document(io.BytesIO(raw_bytes))
                    fullText = []
                    for para in doc.paragraphs:
                        if para.text.strip():
                            fullText.append(para.text)
                    for table in doc.tables:
                        for row in table.rows:
                            fullText.append(" | ".join([cell.text.strip() for cell in row.cells]))
                    return "\n".join(fullText)
                except Exception as e:
                    print(f"[Docx extract fallback]: {e}")

            # 2. Excel Spreadsheets (.xlsx, .xls)
            if ext in [".xlsx", ".xls"]:
                try:
                    import pandas as pd
                    excel_file = pd.ExcelFile(io.BytesIO(raw_bytes))
                    sheets_text = []
                    for sheet_name in excel_file.sheet_names:
                        df = pd.read_excel(excel_file, sheet_name=sheet_name)
                        sheets_text.append(f"--- Sheet: {sheet_name} ---\n" + df.to_string(index=False))
                    return "\n".join(sheets_text)
                except Exception as e:
                    print(f"[Excel extract fallback]: {e}")

            # 3. CSV Tabular Files
            if doc_type == DocumentType.CSV or ext == ".csv":
                try:
                    import pandas as pd
                    df = pd.read_csv(io.BytesIO(raw_bytes))
                    return df.to_string(index=False)
                except Exception:
                    return raw_bytes.decode("utf-8", errors="ignore")

            # 4. JSON Files
            if ext == ".json":
                try:
                    parsed = json.loads(raw_bytes.decode("utf-8", errors="ignore"))
                    return json.dumps(parsed, indent=2)
                except Exception:
                    return raw_bytes.decode("utf-8", errors="ignore")

            # 5. PDF Files
            if doc_type == DocumentType.PDF:
                try:
                    import pypdf
                    reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
                    text_pages = []
                    for idx, page in enumerate(reader.pages):
                        page_txt = page.extract_text() or ""
                        text_pages.append(f"--- Page {idx + 1} ---\n{page_txt}")
                    return "\n".join(text_pages)
                except Exception:
                    return raw_bytes.decode("utf-8", errors="ignore")

            # 6. Images (PNG/JPG/BMP)
            if doc_type == DocumentType.IMAGE:
                return self._extract_image_text(raw_bytes, filepath)

            # 7. Plain Text, EML, Markdown, Log Files
            return raw_bytes.decode("utf-8", errors="ignore")

        except Exception as e:
            # Universal Fallback for raw binary or unknown files
            printable_text = re.sub(r"[^\x20-\x7E\n\r\t]", " ", raw_bytes.decode("latin1", errors="ignore"))
            return f"[EXTRACTED DATA FROM {Path(filepath).name}]\n" + printable_text[:5000]

    def _extract_image_text(self, raw_bytes: bytes, filepath: Union[str, Path]) -> str:
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(raw_bytes))
            try:
                import pytesseract
                txt = pytesseract.image_to_string(img)
                if txt.strip():
                    return txt
            except Exception:
                pass
            return f"[IMAGE DOCUMENT: {Path(filepath).name} ({img.size[0]}x{img.size[1]} {img.format})] - Forensic metadata ingested."
        except Exception as e:
            return f"[IMAGE INGESTION NOTE: {str(e)}]"

    def load_document(
        self, filepath: Union[str, Path], document_id: str = None, override_bytes: bytes = None, override_text: str = None
    ) -> NormalizedDocument:
        path = Path(filepath)
        filename = path.name

        if override_bytes is not None:
            raw_bytes = override_bytes
        elif path.exists():
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

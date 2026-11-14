"""Document service: extract text from uploaded files using pure Python."""
from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone
from typing import Any

from models.document_models import DocumentData, DocumentAnalysis
from utils.logging_config import get_logger
from utils.file_validation import get_extension

logger = get_logger()


class DocumentService:
    """Handle document uploads and text extraction."""

    def __init__(self, config: Any = None):
        from utils.config import get_config
        self.config = config or get_config()

    def process_upload(self, filename: str, content: bytes) -> DocumentData:
        """
        Process an uploaded file: extract text and return a DocumentData object.
        Actual AI analysis is performed separately by BedrockService.
        """
        ext = get_extension(filename)
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"

        text = self._extract_text(filename, content, ext)

        doc = DocumentData(
            id=doc_id,
            filename=filename,
            file_type=ext,
            size_bytes=len(content),
            content=text,
            uploaded_at=datetime.now(timezone.utc).isoformat(),
            page_count=self._estimate_pages(text, ext),
        )
        logger.info(f"Processed document: {filename} ({doc.size_mb} MB, {len(text)} chars)")
        return doc

    def _extract_text(self, filename: str, content: bytes, ext: str) -> str:
        """Dispatch to the appropriate extractor."""
        extractors = {
            "pdf": self._extract_pdf,
            "docx": self._extract_docx,
            "xlsx": self._extract_xlsx,
            "csv": self._extract_csv,
            "txt": self._extract_txt,
            "md": self._extract_txt,
            "pptx": self._extract_pptx,
            "png": self._extract_image,
            "jpg": self._extract_image,
            "jpeg": self._extract_image,
        }
        extractor = extractors.get(ext, self._extract_txt)
        try:
            return extractor(content)
        except Exception as e:
            logger.warning(f"Text extraction failed for {filename}: {e}")
            return f"[Text extraction failed for {filename}: {str(e)[:200]}]"

    def _extract_pdf(self, content: bytes) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(f"--- Page {i+1} ---\n{text}")
            return "\n\n".join(pages)
        except ImportError:
            return "[pypdf not installed — PDF text extraction unavailable]"

    def _extract_docx(self, content: bytes) -> str:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            # Also extract tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)
            return "\n\n".join(paragraphs)
        except ImportError:
            return "[python-docx not installed — DOCX text extraction unavailable]"

    def _extract_xlsx(self, content: bytes) -> str:
        try:
            import pandas as pd
            excel = pd.ExcelFile(io.BytesIO(content))
            sheets_text = []
            for sheet_name in excel.sheet_names[:10]:  # Max 10 sheets
                df = pd.read_excel(excel, sheet_name=sheet_name, nrows=500)
                sheets_text.append(f"=== Sheet: {sheet_name} ===\n{df.to_string(index=False)}")
            return "\n\n".join(sheets_text)
        except ImportError:
            return "[pandas/openpyxl not installed — XLSX extraction unavailable]"

    def _extract_csv(self, content: bytes) -> str:
        try:
            import pandas as pd
            df = pd.read_csv(io.BytesIO(content), nrows=1000)
            return f"Columns: {', '.join(df.columns.tolist())}\n\n{df.to_string(index=False)}"
        except Exception as e:
            # Fallback: raw decode
            return content.decode("utf-8", errors="replace")

    def _extract_txt(self, content: bytes) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1", errors="replace")

    def _extract_pptx(self, content: bytes) -> str:
        try:
            from pptx import Presentation
            prs = Presentation(io.BytesIO(content))
            slides_text = []
            for i, slide in enumerate(prs.slides):
                texts = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        texts.append(shape.text)
                if texts:
                    slides_text.append(f"--- Slide {i+1} ---\n" + "\n".join(texts))
            return "\n\n".join(slides_text)
        except ImportError:
            return "[python-pptx not installed — PPTX extraction unavailable]"

    def _extract_image(self, content: bytes) -> str:
        try:
            from PIL import Image
            import io as _io
            img = Image.open(_io.BytesIO(content))
            return f"[Image file: {img.format} {img.size[0]}x{img.size[1]} pixels. OCR not enabled in Phase 1.]"
        except ImportError:
            return "[Image file — install Pillow for image info]"

    def _estimate_pages(self, text: str, ext: str) -> int:
        if ext in ("png", "jpg", "jpeg"):
            return 1
        words = len(text.split())
        return max(1, words // 400)  # ~400 words per page

    def search_content(self, documents: list[DocumentData], query: str) -> list[dict]:
        """Simple keyword search across document contents."""
        results = []
        q_lower = query.lower()
        for doc in documents:
            if q_lower in doc.content.lower():
                # Find context around match
                idx = doc.content.lower().find(q_lower)
                start = max(0, idx - 100)
                end = min(len(doc.content), idx + 200)
                snippet = doc.content[start:end]
                results.append({
                    "doc_id": doc.id,
                    "filename": doc.filename,
                    "snippet": snippet,
                    "relevance": 0.8,
                })
        return results

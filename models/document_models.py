"""Pydantic models for uploaded documents and their AI analysis."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class DocumentAnalysis(BaseModel):
    summary: str = ""
    key_topics: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    sentiment: str = "neutral"
    document_type: str = "General"  # Contract | Report | Invoice | Proposal | Email | General
    risk_flags: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    word_count: int = 0
    reading_time_minutes: int = 0
    confidence_score: float = 0.85
    language: str = "English"
    key_dates: list[str] = Field(default_factory=list)
    financial_figures: list[str] = Field(default_factory=list)


class DocumentData(BaseModel):
    id: str
    filename: str
    file_type: str  # pdf | docx | xlsx | csv | txt | pptx | png | jpg
    size_bytes: int = 0
    content: str = ""  # Extracted text
    page_count: Optional[int] = None
    uploaded_at: str = ""
    analysis: Optional[DocumentAnalysis] = None
    qa_history: list[dict] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source_path: Optional[str] = None

    @property
    def size_mb(self) -> float:
        return round(self.size_bytes / (1024 * 1024), 2)

    @property
    def is_analyzed(self) -> bool:
        return self.analysis is not None

    @property
    def short_summary(self) -> str:
        if self.analysis and self.analysis.summary:
            text = self.analysis.summary
            return text[:200] + "..." if len(text) > 200 else text
        return "Not yet analyzed"

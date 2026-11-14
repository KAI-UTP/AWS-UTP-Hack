"""Pydantic models for emails and their AI analysis."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class Person(BaseModel):
    name: str
    email: str
    role: Optional[str] = None
    company: Optional[str] = None


class Deadline(BaseModel):
    text: str
    date: Optional[str] = None
    urgency: str = "medium"  # immediate | high | medium | low


class MeetingDetails(BaseModel):
    title: str
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    timezone: str = "EST"
    location: Optional[str] = None
    attendees: list[str] = Field(default_factory=list)
    agenda: list[str] = Field(default_factory=list)
    requires_confirmation: bool = True
    conflict: bool = False


class Attachment(BaseModel):
    name: str
    size: int = 0
    type: str = ""


class EmailAnalysis(BaseModel):
    category: str = "General"
    priority: str = "Medium"  # Critical | High | Medium | Low
    sentiment: str = "neutral"
    summary: str = ""
    action_items: list[str] = Field(default_factory=list)
    deadline: Optional[Deadline] = None
    meeting_detected: Optional[MeetingDetails] = None
    key_entities: list[str] = Field(default_factory=list)
    requires_response: bool = False
    estimated_time_to_handle: int = 10  # minutes
    confidence_score: float = 0.85
    risk_level: str = "Low"  # Critical | High | Medium | Low
    tags: list[str] = Field(default_factory=list)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        allowed = {"Critical", "High", "Medium", "Low"}
        return v if v in allowed else "Medium"

    @field_validator("confidence_score")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class EmailData(BaseModel):
    id: str
    subject: str
    sender: str
    sender_name: str = ""
    recipients: list[str] = Field(default_factory=list)
    date: str = ""
    body: str = ""
    snippet: str = ""
    has_attachments: bool = False
    attachments: list[Attachment] = Field(default_factory=list)
    thread_id: str = ""
    labels: list[str] = Field(default_factory=list)
    analysis: Optional[EmailAnalysis] = None

    @property
    def priority(self) -> str:
        return self.analysis.priority if self.analysis else "Medium"

    @property
    def category(self) -> str:
        return self.analysis.category if self.analysis else "General"

    @property
    def is_unread(self) -> bool:
        return "UNREAD" in self.labels

    @property
    def is_important(self) -> bool:
        return "IMPORTANT" in self.labels

    @classmethod
    def from_dict(cls, data: dict) -> "EmailData":
        """Create from raw dict, parsing nested analysis."""
        if "analysis" in data and isinstance(data["analysis"], dict):
            analysis_data = data["analysis"]
            # Parse deadline
            if "deadline" in analysis_data and isinstance(analysis_data["deadline"], dict):
                analysis_data["deadline"] = Deadline(**analysis_data["deadline"])
            # Parse meeting_detected
            if (
                "meeting_detected" in analysis_data
                and isinstance(analysis_data["meeting_detected"], dict)
            ):
                analysis_data["meeting_detected"] = MeetingDetails(
                    **analysis_data["meeting_detected"]
                )
            data["analysis"] = EmailAnalysis(**analysis_data)
        # Parse attachments
        if "attachments" in data and isinstance(data["attachments"], list):
            data["attachments"] = [
                Attachment(**a) if isinstance(a, dict) else a
                for a in data["attachments"]
            ]
        return cls(**data)

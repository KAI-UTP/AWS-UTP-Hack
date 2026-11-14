"""Pydantic models for calendar events."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    id: str
    title: str
    start: str
    end: str
    timezone: str = "America/New_York"
    location: Optional[str] = None
    description: str = ""
    organizer: str = ""
    attendees: list[str] = Field(default_factory=list)
    status: str = "confirmed"  # confirmed | pending_confirmation | cancelled
    type: str = "Meeting"
    priority: str = "Medium"
    source: str = "calendar"  # calendar | email
    conflict: bool = False
    conflict_with: list[str] = Field(default_factory=list)
    recurring: bool = False
    recurrence: Optional[str] = None
    video_link: Optional[str] = None
    from_email: Optional[str] = None

    @property
    def is_pending(self) -> bool:
        return self.status == "pending_confirmation"

    @property
    def attendee_count(self) -> int:
        return len(self.attendees)

    @classmethod
    def from_dict(cls, data: dict) -> "CalendarEvent":
        return cls(**data)


class MeetingDetected(BaseModel):
    """A meeting extracted from email content."""
    email_id: str
    email_subject: str
    title: str
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    timezone: str = "EST"
    location: Optional[str] = None
    attendees: list[str] = Field(default_factory=list)
    agenda: list[str] = Field(default_factory=list)
    requires_confirmation: bool = True
    added_to_calendar: bool = False
    confidence: float = 0.9

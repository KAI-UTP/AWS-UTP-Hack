"""Pydantic models for user and settings."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class NotificationPreferences(BaseModel):
    email_alerts: bool = True
    task_reminders: bool = True
    meeting_alerts: bool = True
    daily_brief: bool = True
    critical_only: bool = False


class DisplayPreferences(BaseModel):
    theme: str = "dark"  # dark | light
    items_per_page: int = 20
    default_view: str = "dashboard"
    show_confidence_scores: bool = True
    compact_mode: bool = False


class Settings(BaseModel):
    notification_preferences: NotificationPreferences = Field(
        default_factory=NotificationPreferences
    )
    display_preferences: DisplayPreferences = Field(
        default_factory=DisplayPreferences
    )
    email_fetch_days: int = 7
    max_emails: int = 50
    auto_extract_tasks: bool = True
    auto_detect_meetings: bool = True
    mock_mode: bool = True
    bedrock_model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    language: str = "en"
    timezone: str = "America/New_York"


class User(BaseModel):
    id: str = "demo_user"
    name: str = "Demo User"
    email: str = "demo@company.com"
    role: str = "Executive"
    department: str = "Leadership"
    avatar_initials: str = "DU"
    settings: Settings = Field(default_factory=Settings)
    connected_services: list[str] = Field(default_factory=list)
    created_at: str = ""
    last_login: str = ""

    @property
    def is_admin(self) -> bool:
        return self.role in {"Admin", "SuperAdmin"}

    @property
    def display_name(self) -> str:
        return self.name or self.email.split("@")[0]

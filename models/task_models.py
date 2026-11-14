"""Pydantic models for tasks."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator

VALID_STATUSES = {"Not Started", "In Progress", "Pending", "Completed", "Cancelled"}
VALID_PRIORITIES = {"Critical", "High", "Medium", "Low"}


class SubTask(BaseModel):
    id: str
    title: str
    done: bool = False


class Task(BaseModel):
    id: str
    title: str
    description: str = ""
    status: str = "Not Started"
    priority: str = "Medium"
    category: str = "General"
    source: str = "manual"  # email | document | calendar | manual
    source_id: Optional[str] = None
    assigned_to: str = ""
    created_at: str = ""
    due_date: Optional[str] = None
    completed_at: Optional[str] = None
    estimated_hours: float = 1.0
    actual_hours: float = 0.0
    tags: list[str] = Field(default_factory=list)
    subtasks: list[SubTask] = Field(default_factory=list)
    confirmed: bool = True
    ai_extracted: bool = False
    confidence: float = 1.0
    notes: str = ""

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        return v if v in VALID_STATUSES else "Not Started"

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        return v if v in VALID_PRIORITIES else "Medium"

    @property
    def is_overdue(self) -> bool:
        if not self.due_date or self.status == "Completed":
            return False
        from utils.date_utils import is_overdue
        return is_overdue(self.due_date)

    @property
    def completion_pct(self) -> float:
        if not self.subtasks:
            return 100.0 if self.status == "Completed" else 0.0
        done = sum(1 for s in self.subtasks if s.done)
        return round(done / len(self.subtasks) * 100, 1)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        if "subtasks" in data and isinstance(data["subtasks"], list):
            data["subtasks"] = [
                SubTask(**s) if isinstance(s, dict) else s
                for s in data["subtasks"]
            ]
        return cls(**data)

"""Pydantic models for audit logging."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


class AuditRecord(BaseModel):
    id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    user_id: str = "demo_user"
    action: str  # e.g. "analyze_email", "upload_document", "confirm_task"
    resource_type: str  # email | document | task | calendar | settings
    resource_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    ip_address: str = "127.0.0.1"
    user_agent: str = ""
    duration_ms: Optional[int] = None

    @property
    def is_error(self) -> bool:
        return not self.success

    @classmethod
    def create(
        cls,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: dict | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> "AuditRecord":
        import uuid
        return cls(
            id=str(uuid.uuid4()),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            success=success,
            error_message=error_message,
        )

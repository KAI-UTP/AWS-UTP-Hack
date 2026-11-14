"""Audit logging service backed by session state (mock) or persistent store (live)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import streamlit as st

from models.audit_models import AuditRecord

AUDIT_KEY = "audit_records"


class AuditService:
    """Record and query audit events."""

    def __init__(self, config: Any = None):
        from utils.config import get_config
        self.config = config or get_config()
        self._ensure_state()

    def _ensure_state(self):
        if AUDIT_KEY not in st.session_state:
            st.session_state[AUDIT_KEY] = []

    def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: dict | None = None,
        success: bool = True,
        error_message: str | None = None,
        duration_ms: int | None = None,
    ) -> AuditRecord:
        """Record an audit event."""
        self._ensure_state()
        record = AuditRecord(
            id=str(uuid.uuid4()),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
        )
        st.session_state[AUDIT_KEY].insert(0, record.model_dump())
        # Keep last 500 records
        st.session_state[AUDIT_KEY] = st.session_state[AUDIT_KEY][:500]
        return record

    def get_records(
        self,
        action_filter: str | None = None,
        resource_type_filter: str | None = None,
        success_only: bool = False,
        limit: int = 100,
    ) -> list[AuditRecord]:
        """Retrieve audit records with optional filters."""
        self._ensure_state()
        records = [AuditRecord(**r) for r in st.session_state[AUDIT_KEY]]

        if action_filter:
            records = [r for r in records if action_filter.lower() in r.action.lower()]
        if resource_type_filter:
            records = [r for r in records if r.resource_type == resource_type_filter]
        if success_only:
            records = [r for r in records if r.success]

        return records[:limit]

    def get_stats(self) -> dict:
        self._ensure_state()
        records = [AuditRecord(**r) for r in st.session_state[AUDIT_KEY]]
        actions: dict[str, int] = {}
        resources: dict[str, int] = {}
        errors = 0
        for r in records:
            actions[r.action] = actions.get(r.action, 0) + 1
            resources[r.resource_type] = resources.get(r.resource_type, 0) + 1
            if not r.success:
                errors += 1
        return {
            "total": len(records),
            "errors": errors,
            "top_actions": sorted(actions.items(), key=lambda x: x[1], reverse=True)[:5],
            "by_resource": resources,
        }

    def seed_demo_records(self):
        """Populate with realistic audit history for demo purposes."""
        if len(st.session_state.get(AUDIT_KEY, [])) == 0:
            demo_records = [
                ("analyze_email", "email", "email_001", {"priority": "Critical"}, True),
                ("analyze_email", "email", "email_002", {"priority": "High"}, True),
                ("analyze_email", "email", "email_006", {"priority": "Critical"}, True),
                ("extract_tasks", "email", "email_001", {"tasks_found": 3}, True),
                ("extract_tasks", "email", "email_014", {"tasks_found": 2}, True),
                ("detect_meetings", "email", "email_002", {"meetings_found": 1}, True),
                ("detect_meetings", "email", "email_014", {"meetings_found": 1}, True),
                ("generate_daily_brief", "brief", None, {"date": "2026-06-28"}, True),
                ("confirm_task", "task", "task_001", {"title": "Resolve server outage"}, True),
                ("confirm_task", "task", "task_002", {"title": "Approve Q3 budget"}, True),
                ("reject_task", "task", "task_007", {"reason": "Not relevant"}, True),
                ("answer_question", "knowledge", None, {"question": "What are urgent items?"}, True),
                ("answer_question", "knowledge", None, {"question": "Show upcoming meetings"}, True),
                ("upload_document", "document", "doc_abc123", {"filename": "Q3_Budget.pdf"}, True),
                ("analyze_document", "document", "doc_abc123", {"pages": 12}, True),
                ("connect_service", "gmail", None, {}, False, "OAuth credentials not configured"),
                ("connect_service", "bedrock", None, {}, False, "AWS credentials not configured"),
                ("view_page", "page", None, {"page": "dashboard"}, True),
                ("view_page", "page", None, {"page": "email_intelligence"}, True),
                ("view_page", "page", None, {"page": "daily_brief"}, True),
                ("export_brief", "brief", None, {"format": "markdown"}, True),
            ]
            import time
            base_time = datetime.now(timezone.utc).timestamp()
            for i, record_data in enumerate(demo_records):
                action, resource_type = record_data[0], record_data[1]
                resource_id = record_data[2]
                details = record_data[3]
                success = record_data[4] if len(record_data) > 4 else True
                error_msg = record_data[5] if len(record_data) > 5 else None

                # Stagger timestamps backward
                ts = datetime.fromtimestamp(base_time - (i * 300), tz=timezone.utc).isoformat()
                record = AuditRecord(
                    id=str(uuid.uuid4()),
                    timestamp=ts,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details,
                    success=success,
                    error_message=error_msg,
                    duration_ms=int(50 + (i * 17) % 400),
                )
                st.session_state[AUDIT_KEY].append(record.model_dump())

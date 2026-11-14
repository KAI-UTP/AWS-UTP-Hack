"""In-app notification service backed by Streamlit session state."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import streamlit as st


NOTIFICATION_KEY = "notifications"


class NotificationService:
    """Manage in-app notifications using st.session_state."""

    LEVELS = ("info", "success", "warning", "error", "critical")

    def __init__(self):
        self._ensure_state()

    def _ensure_state(self):
        if NOTIFICATION_KEY not in st.session_state:
            st.session_state[NOTIFICATION_KEY] = []

    def add(
        self,
        title: str,
        message: str,
        level: str = "info",
        source: str = "",
        source_id: str = "",
        action_label: str = "",
        action_page: str = "",
    ) -> str:
        """Create and store a new notification. Returns the notification ID."""
        self._ensure_state()
        notif_id = str(uuid.uuid4())
        notif = {
            "id": notif_id,
            "title": title,
            "message": message,
            "level": level if level in self.LEVELS else "info",
            "source": source,
            "source_id": source_id,
            "action_label": action_label,
            "action_page": action_page,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False,
        }
        st.session_state[NOTIFICATION_KEY].insert(0, notif)
        # Keep max 100 notifications
        st.session_state[NOTIFICATION_KEY] = st.session_state[NOTIFICATION_KEY][:100]
        return notif_id

    def info(self, title: str, message: str, **kwargs) -> str:
        return self.add(title, message, level="info", **kwargs)

    def success(self, title: str, message: str, **kwargs) -> str:
        return self.add(title, message, level="success", **kwargs)

    def warning(self, title: str, message: str, **kwargs) -> str:
        return self.add(title, message, level="warning", **kwargs)

    def error(self, title: str, message: str, **kwargs) -> str:
        return self.add(title, message, level="error", **kwargs)

    def critical(self, title: str, message: str, **kwargs) -> str:
        return self.add(title, message, level="critical", **kwargs)

    def get_notifications(self, unread_only: bool = False) -> list[dict]:
        """Alias for get_all() — returns notifications list."""
        return self.get_all(unread_only=unread_only)

    def get_all(self, unread_only: bool = False) -> list[dict]:
        self._ensure_state()
        notifs = st.session_state[NOTIFICATION_KEY]
        if unread_only:
            return [n for n in notifs if not n["read"]]
        return notifs

    def get_unread_count(self) -> int:
        return sum(1 for n in self.get_all() if not n["read"])

    def mark_read(self, notif_id: str):
        self._ensure_state()
        for n in st.session_state[NOTIFICATION_KEY]:
            if n["id"] == notif_id:
                n["read"] = True
                break

    def mark_all_read(self):
        self._ensure_state()
        for n in st.session_state[NOTIFICATION_KEY]:
            n["read"] = True

    def delete(self, notif_id: str):
        self._ensure_state()
        st.session_state[NOTIFICATION_KEY] = [
            n for n in st.session_state[NOTIFICATION_KEY] if n["id"] != notif_id
        ]

    def clear_all(self):
        st.session_state[NOTIFICATION_KEY] = []

    def seed_demo_notifications(self):
        """Add realistic demo notifications on first load."""
        if self.get_unread_count() == 0 and len(self.get_all()) == 0:
            self.critical(
                "🚨 Production Outage Detected",
                "prod-web-01 is DOWN. All customer services affected. INC-2024-0628-001 opened.",
                source="email",
                source_id="email_001",
                action_label="View Incident",
                action_page="Email Intelligence",
            )
            self.error(
                "Payment API Failure",
                "23% error rate on payment processing. ~$42K revenue impact. Dev team alerted.",
                source="email",
                source_id="email_007",
            )
            self.warning(
                "⚠️ Calendar Conflict Detected",
                "Board Meeting and All-Hands both scheduled July 1 at 9 AM EST.",
                source="calendar",
                action_label="View Calendar",
                action_page="Calendar",
            )
            self.warning(
                "Contract Deadline Today",
                "Project Nexus contract must go to legal@techpartner.com by EOD today.",
                source="email",
                source_id="email_014",
            )
            self.info(
                "10 Tasks Extracted from Emails",
                "AI automatically extracted action items from your inbox. Review and confirm.",
                source="tasks",
                action_label="Review Tasks",
                action_page="Tasks",
            )
            self.success(
                "Daily Brief Ready",
                "Your AI-generated executive brief for June 28 is ready to review.",
                action_label="View Brief",
                action_page="Daily Brief",
            )

    @staticmethod
    def level_icon(level: str) -> str:
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨",
        }
        return icons.get(level, "🔔")

    @staticmethod
    def level_color(level: str) -> str:
        colors = {
            "info": "#3b82f6",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "critical": "#dc2626",
        }
        return colors.get(level, "#6b7280")

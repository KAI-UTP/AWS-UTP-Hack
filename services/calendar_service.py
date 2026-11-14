"""Calendar service with mock-mode support."""
from __future__ import annotations

from typing import Any, Optional

from models.calendar_models import CalendarEvent, MeetingDetected
from utils.json_utils import load_json_file
from utils.logging_config import get_logger

logger = get_logger()


class CalendarService:
    """Manage calendar events. Mock mode reads from sample_calendar.json."""

    def __init__(self, config: Any = None):
        from utils.config import get_config
        self.config = config or get_config()
        self.mock_mode = self.config.MOCK_MODE
        self._events_cache: list[CalendarEvent] | None = None

    # ── Public API ────────────────────────────────────────────────────────────

    def get_events(
        self,
        view: str = "all",  # today | week | month | all
        event_type: str | None = None,
        include_conflicts: bool = False,
    ) -> list[CalendarEvent]:
        """Return calendar events with optional filters."""
        events = self._load_events()

        if view == "today":
            from utils.date_utils import is_today
            events = [e for e in events if is_today(e.start)]
        elif view == "week":
            from datetime import datetime, timezone
            from utils.date_utils import get_week_range, parse_date
            start, end = get_week_range()
            filtered = []
            for e in events:
                dt = parse_date(e.start)
                if dt:
                    if dt.tzinfo is None:
                        from datetime import timezone
                        dt = dt.replace(tzinfo=timezone.utc)
                    if start <= dt <= end:
                        filtered.append(e)
            events = filtered
        elif view == "month":
            from utils.date_utils import get_month_range, parse_date
            start, end = get_month_range()
            filtered = []
            for e in events:
                dt = parse_date(e.start)
                if dt:
                    if dt.tzinfo is None:
                        from datetime import timezone
                        dt = dt.replace(tzinfo=timezone.utc)
                    if start <= dt <= end:
                        filtered.append(e)
            events = filtered

        if event_type:
            events = [e for e in events if e.type == event_type]

        if include_conflicts:
            events = [e for e in events if e.conflict]

        return events

    def get_event_by_id(self, event_id: str) -> Optional[CalendarEvent]:
        for e in self._load_events():
            if e.id == event_id:
                return e
        return None

    def get_conflicts(self) -> list[CalendarEvent]:
        return [e for e in self._load_events() if e.conflict]

    def get_pending_confirmations(self) -> list[CalendarEvent]:
        return [e for e in self._load_events() if e.is_pending]

    def get_meetings_from_emails(self, gmail_service: Any) -> list[MeetingDetected]:
        """Extract meeting invitations detected from emails."""
        meetings = []
        emails = gmail_service.get_emails_with_meetings()
        for email in emails:
            if email.analysis and email.analysis.meeting_detected:
                m = email.analysis.meeting_detected
                meetings.append(MeetingDetected(
                    email_id=email.id,
                    email_subject=email.subject,
                    title=m.title,
                    date=m.date,
                    start_time=m.start_time,
                    end_time=m.end_time,
                    timezone=m.timezone,
                    location=m.location,
                    attendees=m.attendees,
                    agenda=m.agenda,
                    requires_confirmation=m.requires_confirmation,
                    confidence=0.9,
                ))
        return meetings

    def confirm_event(self, event_id: str) -> bool:
        """Confirm a pending event."""
        events = self._load_events()
        for e in events:
            if e.id == event_id:
                e.status = "confirmed"
                return True
        return False

    def decline_event(self, event_id: str) -> bool:
        """Decline / cancel an event."""
        events = self._load_events()
        for e in events:
            if e.id == event_id:
                e.status = "cancelled"
                return True
        return False

    def get_stats(self) -> dict:
        events = self._load_events()
        return {
            "total": len(events),
            "confirmed": sum(1 for e in events if e.status == "confirmed"),
            "pending": sum(1 for e in events if e.is_pending),
            "conflicts": len(self.get_conflicts()),
            "today": len(self.get_events(view="today")),
            "this_week": len(self.get_events(view="week")),
            "from_emails": sum(1 for e in events if e.source == "email"),
        }

    def get_event_types(self) -> list[str]:
        return sorted(set(e.type for e in self._load_events()))

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load_events(self) -> list[CalendarEvent]:
        if self._events_cache is not None:
            return self._events_cache

        raw = load_json_file(self.config.SAMPLE_CALENDAR_PATH, [])
        self._events_cache = [CalendarEvent.from_dict(e) for e in raw]
        logger.info(f"Loaded {len(self._events_cache)} calendar events")
        return self._events_cache

    def invalidate_cache(self):
        self._events_cache = None

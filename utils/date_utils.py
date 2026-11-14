"""Date parsing and formatting helpers."""
from __future__ import annotations

from datetime import datetime, date, timezone, timedelta
from typing import Optional
import re


def parse_date(value: str | None) -> Optional[datetime]:
    """Parse a date string into a datetime object."""
    if not value:
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    # Fallback: try dateparser if installed
    try:
        import dateparser
        result = dateparser.parse(value)
        return result
    except Exception:
        return None


def format_relative(dt: datetime | str | None) -> str:
    """Return human-readable relative time (e.g. '2 hours ago')."""
    if dt is None:
        return "Unknown"
    if isinstance(dt, str):
        dt = parse_date(dt)
    if dt is None:
        return "Unknown"
    # Make naive datetimes UTC-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 0:
        # Future
        seconds = abs(seconds)
        if seconds < 60:
            return f"in {seconds}s"
        if seconds < 3600:
            return f"in {seconds // 60}m"
        if seconds < 86400:
            return f"in {seconds // 3600}h"
        return f"in {seconds // 86400}d"
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        m = seconds // 60
        return f"{m} minute{'s' if m != 1 else ''} ago"
    if seconds < 86400:
        h = seconds // 3600
        return f"{h} hour{'s' if h != 1 else ''} ago"
    if seconds < 86400 * 7:
        d = seconds // 86400
        return f"{d} day{'s' if d != 1 else ''} ago"
    return dt.strftime("%b %d, %Y")


def format_date(dt: datetime | str | None, fmt: str = "%b %d, %Y") -> str:
    """Format a datetime as a readable string."""
    if dt is None:
        return ""
    if isinstance(dt, str):
        dt = parse_date(dt)
    if dt is None:
        return ""
    return dt.strftime(fmt)


def format_datetime(dt: datetime | str | None) -> str:
    """Format datetime with time component."""
    return format_date(dt, fmt="%b %d, %Y %I:%M %p")


def days_until(target: datetime | str | None) -> Optional[int]:
    """Return number of days until the target date (negative if past)."""
    if target is None:
        return None
    if isinstance(target, str):
        target = parse_date(target)
    if target is None:
        return None
    if target.tzinfo is None:
        target = target.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    return (target - now).days


def is_today(dt: datetime | str | None) -> bool:
    """Check if a datetime is today."""
    if dt is None:
        return False
    if isinstance(dt, str):
        dt = parse_date(dt)
    if dt is None:
        return False
    return dt.date() == date.today()


def is_overdue(dt: datetime | str | None) -> bool:
    """Check if a datetime is in the past."""
    if dt is None:
        return False
    if isinstance(dt, str):
        dt = parse_date(dt)
    if dt is None:
        return False
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt < datetime.now(timezone.utc)


def get_week_range(reference: datetime | None = None) -> tuple[datetime, datetime]:
    """Return (start_of_week, end_of_week) for the given date."""
    if reference is None:
        reference = datetime.now(timezone.utc)
    start = reference - timedelta(days=reference.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start, end


def get_month_range(reference: datetime | None = None) -> tuple[datetime, datetime]:
    """Return (first_day, last_day) of the month for the given date."""
    if reference is None:
        reference = datetime.now(timezone.utc)
    first = reference.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Last day: first day of next month minus 1 second
    if reference.month == 12:
        last = reference.replace(year=reference.year + 1, month=1, day=1)
    else:
        last = reference.replace(month=reference.month + 1, day=1)
    last = last - timedelta(seconds=1)
    return first, last

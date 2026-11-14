"""Calendar event card component."""
from __future__ import annotations

import streamlit as st

from models.calendar_models import CalendarEvent
from utils.date_utils import format_date, format_datetime


TYPE_COLORS = {
    "Board Meeting": "#dc2626",
    "All-Hands": "#f97316",
    "Kick-off": "#10b981",
    "Project Review": "#6366f1",
    "Standup": "#64748b",
    "1:1": "#06b6d4",
    "Security Review": "#8b5cf6",
    "Finance Meeting": "#f59e0b",
    "Demo": "#ec4899",
    "Client Call": "#f97316",
    "Post-Incident Review": "#dc2626",
    "Learning": "#22c55e",
    "Meeting": "#3b82f6",
}

STATUS_COLORS = {
    "confirmed": "#22c55e",
    "pending_confirmation": "#f59e0b",
    "cancelled": "#6b7280",
}


def render_calendar_card(event: CalendarEvent, show_actions: bool = True):
    """Render a calendar event card."""
    type_color = TYPE_COLORS.get(event.type, "#6366f1")
    status_color = STATUS_COLORS.get(event.status, "#64748b")
    conflict_banner = ""
    if event.conflict:
        conflict_banner = (
            '<div style="background:rgba(220,38,38,0.12); border:1px solid rgba(220,38,38,0.4); border-radius:4px; '
            'padding:4px 8px; font-size:0.72rem; color:#dc2626; margin-bottom:6px;">'
            '&#9888; Calendar Conflict Detected</div>'
        )

    source_badge = ""
    if event.source == "email":
        source_badge = (
            '<span style="background:rgba(99,102,241,0.12); color:#818cf8; border:1px solid rgba(99,102,241,0.3); '
            'border-radius:4px; padding:1px 6px; font-size:0.65rem; margin-left:4px;">From Email</span>'
        )

    pending_badge = ""
    if event.is_pending:
        pending_badge = (
            '<span style="background:rgba(245,158,11,0.12); color:#f59e0b; border:1px solid rgba(245,158,11,0.3); '
            'border-radius:4px; padding:1px 6px; font-size:0.65rem; margin-left:4px;">Awaiting Confirmation</span>'
        )

    # Format time
    try:
        start_str = event.start.split("T")[1][:5] if "T" in event.start else event.start
        end_str = event.end.split("T")[1][:5] if "T" in event.end else event.end
        date_str = format_date(event.start.split("T")[0])
        time_str = f"{start_str} – {end_str} {event.timezone}"
    except Exception:
        date_str = event.start
        time_str = event.end

    location_span = f'<span>&#128205; {event.location}</span>' if event.location else ''
    desc_div = (
        f'<div style="font-size:0.73rem; color:#64748b; margin-top:6px;">{event.description[:120]}...</div>'
        if event.description else ''
    )
    st.html(
        f"""
        <div style="
            background:#1e293b;
            border:1px solid #334155;
            border-left:4px solid {type_color};
            border-radius:8px;
            padding:12px 14px;
            margin-bottom:8px;
        ">
            {conflict_banner}
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:4px;">
                <div style="font-size:0.85rem; font-weight:600; color:#f1f5f9;">
                    {event.title}{source_badge}{pending_badge}
                </div>
                <span style="background:rgba(0,0,0,0.3); color:{type_color}; border:1px solid {type_color};
                    border-radius:4px; padding:1px 8px; font-size:0.68rem;">{event.type}</span>
            </div>
            <div style="font-size:0.75rem; color:#94a3b8; margin-top:6px; display:flex; gap:12px; flex-wrap:wrap;">
                <span>&#128197; {date_str}</span>
                <span>&#128336; {time_str}</span>
                {location_span}
                <span>&#128101; {event.attendee_count} attendees</span>
                <span style="color:{status_color};">&#9679; {event.status.replace("_"," ").title()}</span>
            </div>
            {desc_div}
        </div>
        """
    )

    if show_actions and event.is_pending:
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("✅ Confirm", key=f"cal_confirm_{event.id}", use_container_width=True):
                event.status = "confirmed"
                st.success("Event confirmed!")
                st.rerun()
        with col2:
            if st.button("❌ Decline", key=f"cal_decline_{event.id}", use_container_width=True):
                event.status = "cancelled"
                st.warning("Event declined")
                st.rerun()

"""Calendar page — events, meeting detection, conflict resolution."""
from __future__ import annotations

import streamlit as st

from components.calendar_card import render_calendar_card
from models.calendar_models import CalendarEvent


def render():
    st.html("## 📅 Calendar Intelligence")
    st.markdown("*Manage events and meetings detected from your emails*")

    calendar = st.session_state.get("calendar_service")
    gmail = st.session_state.get("gmail_service")

    if not calendar:
        st.error("Calendar service not initialised.")
        return

    # ── Stats Row ─────────────────────────────────────────────────────────────
    stats = calendar.get_stats()
    s_cols = st.columns(5)
    stat_items = [
        ("📅", "Total Events", stats["total"], "#6366f1"),
        ("✅", "Confirmed", stats["confirmed"], "#22c55e"),
        ("⏳", "Pending", stats["pending"], "#f59e0b"),
        ("⚠️", "Conflicts", stats["conflicts"], "#dc2626"),
        ("📧", "From Emails", stats["from_emails"], "#8b5cf6"),
    ]
    for col, (icon, label, val, color) in zip(s_cols, stat_items):
        with col:
            st.markdown(
                f'<div style="background:#1e293b; border:1px solid #334155; border-left:3px solid {color}; '
                f'border-radius:6px; padding:8px; text-align:center;">'
                f'<div style="font-size:0.9rem;">{icon}</div>'
                f'<div style="font-size:1.2rem; font-weight:700; color:#f1f5f9;">{val}</div>'
                f'<div style="font-size:0.65rem; color:#64748b;">{label}</div></div>')

    # Conflict banner
    conflicts = calendar.get_conflicts()
    if conflicts:
        st.html("")
        st.error(
            f"⚠️ **{len(conflicts)} Calendar Conflict(s) Detected!** "
            "Please review and resolve before the affected dates."
        )

    st.markdown("---")

    # ── View Tabs ─────────────────────────────────────────────────────────────
    tab_all, tab_pending, tab_conflicts, tab_meetings, tab_add = st.tabs([
        "📅 All Events",
        "⏳ Pending Confirmation",
        "⚠️ Conflicts",
        "📧 From Emails",
        "➕ Add Event",
    ])

    with tab_all:
        view_selector = st.radio(
            "View", ["All", "Today", "This Week", "This Month"],
            horizontal=True, key="cal_view"
        )
        view_map = {"All": "all", "Today": "today", "This Week": "week", "This Month": "month"}
        events = calendar.get_events(view=view_map.get(view_selector, "all"))

        if not events:
            st.info(f"No events for the selected view: {view_selector}")
        else:
            st.markdown(f"**{len(events)} event(s)**")
            for event in events:
                render_calendar_card(event, show_actions=True)

    with tab_pending:
        pending_events = calendar.get_pending_confirmations()
        if not pending_events:
            st.success("✅ No pending calendar confirmations!")
        else:
            st.markdown(f"**{len(pending_events)} event(s) awaiting your confirmation:**")
            for event in pending_events:
                render_calendar_card(event, show_actions=True)

    with tab_conflicts:
        if not conflicts:
            st.success("✅ No calendar conflicts detected!")
        else:
            st.warning(f"**{len(conflicts)} conflicts to resolve:**")
            for event in conflicts:
                render_calendar_card(event, show_actions=False)
                # Conflict resolution options
                conflict_ids = event.conflict_with
                if conflict_ids:
                    st.markdown(
                        f"**Conflicts with:** {', '.join(conflict_ids)}"
                    )
                    res_col1, res_col2, res_col3 = st.columns([1, 1, 2])
                    with res_col1:
                        if st.button("Keep This Event", key=f"keep_{event.id}", use_container_width=True):
                            st.success(f"Keeping: {event.title}")
                    with res_col2:
                        if st.button("Decline This", key=f"decline_{event.id}", use_container_width=True):
                            event.status = "cancelled"
                            st.warning(f"Declined: {event.title}")
                            st.rerun()
                    with res_col3:
                        st.info(f"Tip: Board Meeting takes priority per company policy")
                st.markdown("---")

    with tab_meetings:
        if gmail:
            detected_meetings = calendar.get_meetings_from_emails(gmail)
            if not detected_meetings:
                st.info("No meeting invitations detected in recent emails.")
            else:
                st.markdown(f"**{len(detected_meetings)} meeting(s) detected from emails:**")
                for meeting in detected_meetings:
                    _render_detected_meeting(meeting, calendar)
        else:
            st.info("Connect Gmail to detect meetings from emails.")

    with tab_add:
        _render_add_event_form(calendar)


def _render_detected_meeting(meeting, calendar):
    """Render a meeting detected from email with add-to-calendar option."""
    conf_color = "#22c55e" if not meeting.requires_confirmation else "#f59e0b"

    st.markdown(
        f"""
        <div style="background:#1e293b; border:1px solid #334155; border-left:4px solid #6366f1;
                    border-radius:8px; padding:12px 16px; margin-bottom:10px;">
            <div style="font-size:0.85rem; font-weight:600; color:#f1f5f9; margin-bottom:4px;">
                📅 {meeting.title}
            </div>
            <div style="font-size:0.75rem; color:#94a3b8;">
                From email: <em style="color:#818cf8;">"{meeting.email_subject[:60]}..."</em>
            </div>
            <div style="font-size:0.75rem; color:#64748b; margin-top:6px; display:flex; gap:12px; flex-wrap:wrap;">
                {f'<span>📅 {meeting.date}</span>' if meeting.date else ''}
                {f'<span>🕐 {meeting.start_time} – {meeting.end_time} {meeting.timezone}</span>' if meeting.start_time else ''}
                {f'<span>📍 {meeting.location}</span>' if meeting.location else ''}
                <span>👥 {len(meeting.attendees)} attendees</span>
                <span style="color:{conf_color};">{'Requires Confirmation' if meeting.requires_confirmation else 'Auto-Confirmed'}</span>
            </div>
            {f'<div style="font-size:0.72rem; color:#64748b; margin-top:4px;">Agenda: {" · ".join(meeting.agenda[:3])}</div>' if meeting.agenda else ''}
        </div>
        """)

    if not meeting.added_to_calendar:
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📅 Add to Calendar", key=f"add_meet_{meeting.email_id}", use_container_width=True):
                meeting.added_to_calendar = True
                st.success(f"Added '{meeting.title}' to calendar!")
                st.rerun()


def _render_add_event_form(calendar):
    """Manual event creation form."""
    import uuid
    from datetime import datetime, timezone, date, time

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Event Title *", key="new_event_title")
        event_date = st.date_input("Date *", key="new_event_date")
        start_time = st.time_input("Start Time", value=time(9, 0), key="new_event_start")
        end_time = st.time_input("End Time", value=time(10, 0), key="new_event_end")
    with col2:
        location = st.text_input("Location", key="new_event_location")
        event_type = st.selectbox("Type", ["Meeting", "1:1", "All-Hands", "Standup", "Demo", "Other"], key="new_event_type")
        description = st.text_area("Description", key="new_event_desc", height=80)
        attendees_raw = st.text_input("Attendees (comma-separated emails)", key="new_event_attendees")

    if st.button("📅 Create Event", type="primary") and title:
        event = CalendarEvent(
            id=f"cal_{uuid.uuid4().hex[:8]}",
            title=title,
            start=f"{event_date}T{start_time}",
            end=f"{event_date}T{end_time}",
            location=location,
            description=description,
            type=event_type,
            status="confirmed",
            attendees=[a.strip() for a in attendees_raw.split(",") if a.strip()],
            source="manual",
        )
        # Add to cache
        if calendar._events_cache is None:
            calendar._events_cache = []
        calendar._events_cache.insert(0, event)
        st.success(f"✅ Event '{title}' created!")
        st.rerun()

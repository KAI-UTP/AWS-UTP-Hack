"""Home dashboard page."""
from __future__ import annotations

import streamlit as st

from components.metric_card import metric_card
from components.email_card import render_email_card
from components.task_card import render_task_card
from components.calendar_card import render_calendar_card
from components.charts import (
    email_volume_chart,
    category_distribution_chart,
    priority_distribution_chart,
    task_status_chart,
    time_saved_gauge,
)
from models.task_models import Task


def render():
    st.html("## 🏠 Executive Dashboard")
    st.markdown("*Real-time overview of your enterprise intelligence*")

    gmail = st.session_state.get("gmail_service")
    calendar = st.session_state.get("calendar_service")
    tasks_raw = st.session_state.get("tasks", [])

    if not gmail:
        st.error("Services not initialised. Please refresh the page.")
        return

    # ── Metrics Row 1 ─────────────────────────────────────────────────────────
    stats = gmail.get_stats()
    cal_stats = calendar.get_stats() if calendar else {}

    tasks = [Task.from_dict(t) if isinstance(t, dict) else t for t in tasks_raw]
    task_status_counts: dict[str, int] = {}
    for t in tasks:
        task_status_counts[t.status] = task_status_counts.get(t.status, 0) + 1

    overdue_count = sum(1 for t in tasks if t.is_overdue)
    unconfirmed_ai = sum(1 for t in tasks if t.ai_extracted and not t.confirmed)

    cols = st.columns(4)
    with cols[0]:
        metric_card("Emails Analysed", stats["total"], icon="📧", color="#6366f1",
                    subtitle=f"{stats['unread']} unread")
    with cols[1]:
        metric_card("Critical Alerts", stats["critical"], icon="🚨", color="#dc2626",
                    subtitle=f"{stats['requiring_response']} need reply",
                    delta_color="negative" if stats["critical"] > 0 else "normal")
    with cols[2]:
        metric_card("Active Tasks", len([t for t in tasks if t.status not in ("Completed", "Cancelled")]),
                    icon="✅", color="#10b981",
                    subtitle=f"{overdue_count} overdue",
                    delta_color="negative" if overdue_count > 0 else "positive")
    with cols[3]:
        metric_card("Calendar Events", cal_stats.get("total", 0), icon="📅", color="#f59e0b",
                    subtitle=f"{cal_stats.get('conflicts', 0)} conflicts")

    st.markdown("<br>")

    cols2 = st.columns(4)
    with cols2[0]:
        metric_card("Meetings Detected", stats.get("with_meetings", 0), icon="🤝", color="#8b5cf6",
                    subtitle="from email scan")
    with cols2[1]:
        metric_card("Deadlines Tracked", stats.get("with_deadlines", 0), icon="⏰", color="#f97316",
                    subtitle="action required")
    with cols2[2]:
        metric_card("AI Tasks Extracted", unconfirmed_ai, icon="🤖", color="#06b6d4",
                    subtitle="pending confirmation")
    with cols2[3]:
        metric_card("Hours Saved Today", "3.5h", icon="⚡", color="#22c55e",
                    subtitle="vs manual processing")

    st.html("---")

    # ── Charts Row ────────────────────────────────────────────────────────────
    chart_col1, chart_col2, chart_col3 = st.columns([2, 1.5, 1.5])

    with chart_col1:
        # Mock 7-day email volume
        import datetime
        dates = [(datetime.date.today() - datetime.timedelta(days=i)).strftime("%b %d")
                 for i in range(6, -1, -1)]
        counts = [3, 7, 5, 9, 4, 11, 15]
        st.plotly_chart(email_volume_chart(dates, counts), use_container_width=True)

    with chart_col2:
        cats = stats.get("categories", {})
        if cats:
            st.plotly_chart(category_distribution_chart(cats), use_container_width=True)

    with chart_col3:
        prios = stats.get("priorities", {})
        if prios:
            st.plotly_chart(priority_distribution_chart(prios), use_container_width=True)

    st.markdown("---")

    # ── Bottom 3-column layout ────────────────────────────────────────────────
    bottom_col1, bottom_col2, bottom_col3 = st.columns(3)

    with bottom_col1:
        st.markdown("### 📧 Recent Critical Emails")
        critical_emails = [e for e in gmail.get_emails() if e.priority in ("Critical", "High")][:3]
        if critical_emails:
            for email in critical_emails:
                render_email_card(email)
        else:
            st.info("No critical emails. You're all caught up! 🎉")

        if st.button("View All Emails →", key="home_view_emails"):
            st.session_state["current_page"] = "email_intelligence"
            st.rerun()

    with bottom_col2:
        st.markdown("### ✅ Upcoming Tasks")
        pending_tasks = [t for t in tasks if t.status not in ("Completed", "Cancelled")][:4]
        if pending_tasks:
            for task in pending_tasks:
                render_task_card(task, compact=True, show_actions=False)
        else:
            st.info("All tasks complete! Great work.")

        if st.button("View All Tasks →", key="home_view_tasks"):
            st.session_state["current_page"] = "tasks"
            st.rerun()

    with bottom_col3:
        st.markdown("### 📅 Upcoming Calendar")
        cal_events = calendar.get_events() if calendar else []
        # Show next 4 events
        for event in cal_events[:4]:
            render_calendar_card(event, show_actions=False)

        if cal_events:
            conflicts = [e for e in cal_events if e.conflict]
            if conflicts:
                st.warning(f"⚠️ {len(conflicts)} calendar conflict(s) detected!")

        if st.button("View Calendar →", key="home_view_calendar"):
            st.session_state["current_page"] = "calendar"
            st.rerun()

    st.markdown("---")

    # ── System Status Bar ─────────────────────────────────────────────────────
    st.markdown("### 🖥️ System Status")
    status_cols = st.columns(5)
    services = [
        ("Gmail API", "🟡 Demo", "#f59e0b"),
        ("AWS Bedrock", "🟡 Demo", "#f59e0b"),
        ("Knowledge Base", "🟡 Demo", "#f59e0b"),
        ("Calendar API", "🟡 Demo", "#f59e0b"),
        ("AI Processing", "🟢 Active", "#22c55e"),
    ]
    for col, (name, status, color) in zip(status_cols, services):
        with col:
            st.markdown(
                f'<div style="background:#1e293b; border:1px solid #334155; border-radius:6px; '
                f'padding:8px; text-align:center;">'
                f'<div style="font-size:0.7rem; color:#94a3b8;">{name}</div>'
                f'<div style="color:{color}; font-size:0.8rem; font-weight:600;">{status}</div>'
                f'</div>')

"""Notifications page."""
from __future__ import annotations

import streamlit as st

from services.notification_service import NotificationService


def render():
    st.html("## 🔔 Notifications")
    st.markdown("*In-app alerts and system notifications*")

    svc = NotificationService()

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 1, 1, 1])
    with ctrl_col1:
        filter_level = st.selectbox(
            "Filter by level",
            ["All", "critical", "error", "warning", "success", "info"],
            key="notif_filter",
        )
    with ctrl_col2:
        unread_only = st.checkbox("Unread only", key="notif_unread")
    with ctrl_col3:
        st.markdown("<br>")
        if st.button("✅ Mark All Read", use_container_width=True):
            svc.mark_all_read()
            st.rerun()
    with ctrl_col4:
        st.html("<br>")
        if st.button("🗑️ Clear All", use_container_width=True):
            svc.clear_all()
            st.rerun()

    # ── Stats ─────────────────────────────────────────────────────────────────
    all_notifs = svc.get_all()
    unread_count = svc.get_unread_count()

    stat_cols = st.columns(4)
    level_counts = {}
    for n in all_notifs:
        lvl = n.get("level", "info")
        level_counts[lvl] = level_counts.get(lvl, 0) + 1

    with stat_cols[0]:
        st.metric("Total", len(all_notifs))
    with stat_cols[1]:
        st.metric("Unread", unread_count)
    with stat_cols[2]:
        st.metric("Critical/Error", level_counts.get("critical", 0) + level_counts.get("error", 0))
    with stat_cols[3]:
        st.metric("Warnings", level_counts.get("warning", 0))

    st.html("---")

    # ── Notification list ─────────────────────────────────────────────────────
    notifs = svc.get_all(unread_only=unread_only)

    if filter_level != "All":
        notifs = [n for n in notifs if n.get("level") == filter_level]

    if not notifs:
        st.markdown(
            """
            <div style="text-align:center; padding:60px 20px; color:#64748b;">
                <div style="font-size:3rem; margin-bottom:16px;">🔔</div>
                <div style="font-size:1rem; font-weight:600; margin-bottom:8px;">No notifications</div>
                <div style="font-size:0.85rem;">You're all caught up!</div>
            </div>
            """)
        return

    for notif in notifs:
        _render_notification(notif, svc)


def _render_notification(notif: dict, svc: NotificationService):
    """Render a single notification card."""
    level = notif.get("level", "info")
    color = svc.level_color(level)
    icon = svc.level_icon(level)
    is_read = notif.get("read", False)
    opacity = "0.6" if is_read else "1.0"

    from utils.date_utils import format_relative
    ts = format_relative(notif.get("timestamp"))

    st.html(f"""
        <div style="
            background:#1e293b;
            border:1px solid #334155;
            border-left:4px solid {color};
            border-radius:8px;
            padding:12px 16px;
            margin-bottom:8px;
            opacity:{opacity};
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;">
                <div style="flex:1; min-width:0;">
                    <div style="font-size:0.85rem; font-weight:600; color:#f1f5f9; margin-bottom:4px;">
                        {icon} {notif.get('title','')}
                    </div>
                    <div style="font-size:0.78rem; color:#94a3b8;">
                        {notif.get('message','')}
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px; min-width:80px;">
                    <span style="font-size:0.65rem; color:#475569;">{ts}</span>
                    {"" if is_read else f'<span style="background:{color}20; color:{color}; border-radius:4px; padding:1px 6px; font-size:0.65rem; font-weight:600;">NEW</span>'}
                </div>
            </div>
        </div>
        """)

    notif_id = notif.get("id", "")
    action_col1, action_col2, action_col3 = st.columns([1, 1, 5])
    with action_col1:
        if not is_read and st.button("Mark Read", key=f"read_{notif_id}", use_container_width=True):
            svc.mark_read(notif_id)
            st.rerun()
    with action_col2:
        if st.button("Delete", key=f"del_{notif_id}", use_container_width=True):
            svc.delete(notif_id)
            st.rerun()

    action_page = notif.get("action_page")
    action_label = notif.get("action_label")
    if action_page and action_label:
        with action_col3:
            if st.button(f"→ {action_label}", key=f"act_{notif_id}"):
                page_map = {
                    "Email Intelligence": "email_intelligence",
                    "Tasks": "tasks",
                    "Calendar": "calendar",
                    "Daily Brief": "daily_brief",
                }
                target = page_map.get(action_page, "home")
                svc.mark_read(notif_id)
                st.session_state["current_page"] = target
                st.rerun()

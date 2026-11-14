"""Sidebar navigation component."""
from __future__ import annotations

import streamlit as st


NAV_PAGES = [
    ("🏠", "Dashboard", "home"),
    ("📋", "Daily Brief", "daily_brief"),
    ("📧", "Email Intelligence", "email_intelligence"),
    ("📄", "Document Intelligence", "document_intelligence"),
    ("💬", "Knowledge Assistant", "knowledge_assistant"),
    ("✅", "Tasks", "tasks"),
    ("📅", "Calendar", "calendar"),
    ("🔗", "Knowledge Connections", "knowledge_connections"),
    ("📊", "Analytics", "analytics"),
    ("🔌", "Data Sources", "data_sources"),
    ("🔔", "Notifications", "notifications"),
    ("🛡️", "Audit History", "audit_history"),
    ("⚙️", "Settings", "settings"),
    ("🖥️", "System Status", "system_status"),
]


def render_navigation():
    """Render the sidebar with navigation and status info."""
    with st.sidebar:
        # Logo / brand
        st.html(
            """
            <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
                <div style="font-size:2.5rem;">&#129504;</div>
                <div style="font-size:1.1rem; font-weight:700; color:#6366f1; letter-spacing:0.5px;">
                    Enterprise Intelligence Hub
                </div>
                <div style="font-size:0.7rem; color:#64748b; margin-top:2px;">
                    Powered by AWS Bedrock &amp; Claude AI
                </div>
            </div>
            """
        )

        st.divider()

        # Unread notification badge
        notif_count = 0
        if "notifications" in st.session_state:
            notif_count = sum(
                1 for n in st.session_state["notifications"] if not n.get("read", False)
            )

        # Navigation links
        current_page = st.session_state.get("current_page", "home")

        for icon, label, page_key in NAV_PAGES:
            badge = f" 🔴{notif_count}" if page_key == "notifications" and notif_count > 0 else ""
            display_label = f"{icon} {label}{badge}"

            is_active = current_page == page_key
            button_type = "primary" if is_active else "secondary"

            if st.button(
                display_label,
                key=f"nav_{page_key}",
                use_container_width=True,
                type=button_type,
            ):
                st.session_state["current_page"] = page_key
                st.rerun()

        st.divider()

        # Quick stats
        _render_quick_stats()

        # Mode indicator
        mock_mode = st.session_state.get("config_mock_mode", True)
        if mock_mode:
            st.html(
                """
                <div style="background:#fef3c7; border:1px solid #f59e0b; border-radius:6px;
                            padding:8px 10px; font-size:0.75rem; color:#92400e; text-align:center;">
                    &#128993; <strong>Demo Mode</strong><br/>Using Sample Data
                </div>
                """
            )
        else:
            st.html(
                """
                <div style="background:#d1fae5; border:1px solid #22c55e; border-radius:6px;
                            padding:8px 10px; font-size:0.75rem; color:#065f46; text-align:center;">
                    &#129002; <strong>Live Mode</strong><br/>Connected to AWS &amp; Gmail
                </div>
                """
            )

        st.html(
            "<div style='font-size:0.65rem; color:#475569; text-align:center; margin-top:8px;'>"
            "v1.0.0 &middot; AWS Hackathon 2026</div>"
        )


def _render_quick_stats():
    """Render compact quick-stats in sidebar."""
    emails = st.session_state.get("email_stats", {})
    tasks = st.session_state.get("task_stats", {})

    critical = emails.get("critical", 0)
    pending_tasks = tasks.get("not_started", 0) + tasks.get("in_progress", 0)

    cols = st.columns(2)
    with cols[0]:
        st.metric("📧 Emails", emails.get("total", 0), delta=None)
    with cols[1]:
        st.metric("⚡ Critical", critical, delta=None)

    cols2 = st.columns(2)
    with cols2[0]:
        st.metric("✅ Tasks", pending_tasks, delta=None)
    with cols2[1]:
        overdue = tasks.get("overdue", 0)
        st.metric("🔴 Overdue", overdue, delta=None)

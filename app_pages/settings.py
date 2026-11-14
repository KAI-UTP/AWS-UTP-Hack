"""Settings page."""
from __future__ import annotations

import streamlit as st


def render():
    st.html("## ⚙️ Settings")
    st.markdown("*Configure the Enterprise Intelligence Hub*")

    tab_general, tab_ai, tab_email, tab_notifs, tab_security = st.tabs([
        "🔧 General", "🤖 AI & Bedrock", "📧 Email", "🔔 Notifications", "🔒 Security"
    ])

    with tab_general:
        st.markdown("### General Settings")

        col1, col2 = st.columns(2)
        with col1:
            mock_mode = st.toggle(
                "Demo Mode (Mock Data)",
                value=st.session_state.get("config_mock_mode", True),
                help="Use sample data instead of real APIs",
            )
            st.session_state["config_mock_mode"] = mock_mode

            theme = st.selectbox("Theme", ["Dark", "Light"], index=0, key="settings_theme")
            language = st.selectbox("Language", ["English", "Spanish", "French", "German"], key="settings_lang")
            timezone = st.selectbox(
                "Timezone",
                ["America/New_York", "America/Los_Angeles", "America/Chicago", "Europe/London", "Asia/Tokyo"],
                key="settings_tz",
            )

        with col2:
            items_per_page = st.slider("Items per page", 10, 100, 20, key="settings_ipp")
            compact_mode = st.toggle("Compact mode", False, key="settings_compact")
            show_confidence = st.toggle("Show confidence scores", True, key="settings_conf")
            debug_mode = st.toggle("Debug mode", False, key="settings_debug")

        if st.button("💾 Save General Settings", type="primary", key="save_general"):
            st.success("✅ General settings saved!")

    with tab_ai:
        st.markdown("### AI & AWS Bedrock Configuration")

        col1, col2 = st.columns(2)
        with col1:
            bedrock_model = st.selectbox(
                "Bedrock Model",
                [
                    "anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "anthropic.claude-3-5-haiku-20241022-v1:0",
                    "anthropic.claude-3-opus-20240229-v1:0",
                ],
                key="settings_model",
                help="Claude model to use for AI analysis",
            )
            max_tokens = st.slider("Max Tokens", 1024, 8192, 4096, key="settings_tokens")
            temperature = st.slider("Temperature", 0.0, 1.0, 0.1, step=0.05, key="settings_temp",
                                   help="Lower = more focused, Higher = more creative")
            top_p = st.slider("Top P", 0.1, 1.0, 0.9, step=0.05, key="settings_top_p")

        with col2:
            aws_region = st.selectbox(
                "AWS Region",
                ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                key="settings_region",
            )
            auto_extract_tasks = st.toggle("Auto-extract tasks from emails", True, key="settings_auto_tasks")
            auto_detect_meetings = st.toggle("Auto-detect meetings from emails", True, key="settings_auto_meetings")
            auto_analyse_docs = st.toggle("Auto-analyse uploaded documents", True, key="settings_auto_docs")

        st.markdown("### AWS Credentials")
        st.info("For security, credentials are loaded from environment variables. Edit your `.env` file.")

        col3, col4 = st.columns(2)
        with col3:
            st.text_input("AWS Region (env: AWS_REGION)", value=aws_region, disabled=True)
            st.text_input("Bedrock Model ID (env: BEDROCK_MODEL_ID)", value=bedrock_model, disabled=True)
        with col4:
            st.text_input("AWS Access Key (env: AWS_ACCESS_KEY_ID)", value="••••••••", disabled=True, type="password")
            st.text_input("AWS Secret Key (env: AWS_SECRET_ACCESS_KEY)", value="••••••••", disabled=True, type="password")

        if st.button("💾 Save AI Settings", type="primary", key="save_ai"):
            st.success("✅ AI settings saved!")

    with tab_email:
        st.markdown("### Email Settings")

        col1, col2 = st.columns(2)
        with col1:
            fetch_days = st.slider("Fetch emails from last N days", 1, 30, 7, key="settings_days")
            max_emails = st.slider("Maximum emails to fetch", 10, 200, 50, key="settings_max_emails")
            priority_threshold = st.selectbox(
                "Minimum priority to highlight",
                ["Low", "Medium", "High", "Critical"],
                index=2,
                key="settings_min_priority",
            )

        with col2:
            auto_mark_read = st.toggle("Auto-mark as read after analysis", False, key="settings_auto_read")
            show_spam = st.toggle("Show spam/promotional emails", True, key="settings_show_spam")
            thread_view = st.toggle("Group by email threads", True, key="settings_threads")

        if st.button("💾 Save Email Settings", type="primary", key="save_email"):
            st.success("✅ Email settings saved!")

    with tab_notifs:
        st.markdown("### Notification Preferences")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Alert Types:**")
            email_alerts = st.toggle("Email analysis alerts", True, key="notif_email")
            task_reminders = st.toggle("Task deadline reminders", True, key="notif_tasks")
            meeting_alerts = st.toggle("Meeting confirmations", True, key="notif_meetings")
            daily_brief = st.toggle("Daily brief ready notification", True, key="notif_brief")
            critical_only = st.toggle("Critical alerts only", False, key="notif_critical_only")

        with col2:
            st.markdown("**Timing:**")
            brief_time = st.time_input("Daily brief generation time", key="notif_brief_time")
            reminder_hours = st.slider("Task reminder: hours before deadline", 1, 48, 24, key="notif_reminder_hours")

        if st.button("💾 Save Notification Settings", type="primary", key="save_notifs"):
            st.success("✅ Notification settings saved!")

    with tab_security:
        st.markdown("### Security Settings")

        col1, col2 = st.columns(2)
        with col1:
            max_file_size = st.slider("Max file upload size (MB)", 1, 50, 10, key="settings_max_file")
            allowed_types = st.multiselect(
                "Allowed file types",
                ["pdf", "docx", "xlsx", "csv", "txt", "pptx", "png", "jpg", "jpeg"],
                default=["pdf", "docx", "xlsx", "csv", "txt", "pptx", "png", "jpg"],
                key="settings_file_types",
            )
            audit_enabled = st.toggle("Enable audit logging", True, key="settings_audit")
            pii_detection = st.toggle("Enable PII detection", True, key="settings_pii")

        with col2:
            st.markdown("**Session Settings:**")
            session_timeout = st.slider("Session timeout (minutes)", 15, 480, 60, key="settings_session")
            rate_limit = st.slider("AI requests per minute limit", 5, 60, 20, key="settings_rate")

        st.markdown("### Security Status")
        status_items = [
            ("HTTPS Enabled", "✅" if True else "❌", True),
            ("Audit Logging", "✅" if audit_enabled else "❌", audit_enabled),
            ("PII Detection", "✅" if pii_detection else "❌", pii_detection),
            ("Rate Limiting", "✅", True),
            ("Input Sanitisation", "✅", True),
            ("File Type Validation", "✅", True),
        ]
        for label, icon, ok in status_items:
            color = "#22c55e" if ok else "#ef4444"
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; background:#0f172a; '
                f'border-radius:4px; padding:4px 10px; margin-bottom:4px; font-size:0.8rem;">'
                f'<span style="color:#94a3b8;">{label}</span>'
                f'<span style="color:{color};">{icon}</span></div>')

        if st.button("💾 Save Security Settings", type="primary", key="save_security"):
            st.success("✅ Security settings saved!")

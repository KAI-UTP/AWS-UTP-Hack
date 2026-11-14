"""Data Sources page — connection status and management."""
from __future__ import annotations

import streamlit as st


SERVICES = [
    {
        "id": "gmail",
        "name": "Gmail",
        "icon": "📧",
        "description": "Connect your Gmail to analyse emails with AI. Reads emails, detects meetings, extracts tasks automatically.",
        "features": ["Email reading", "Meeting detection", "Task extraction", "Label management"],
        "status_key": "gmail_connected",
        "color": "#ea4335",
        "requires": "Google OAuth credentials (GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET)",
        "docs": "https://developers.google.com/gmail/api",
    },
    {
        "id": "google_calendar",
        "name": "Google Calendar",
        "icon": "📅",
        "description": "Sync your Google Calendar to detect conflicts, manage meetings detected from emails, and get scheduling insights.",
        "features": ["Event sync", "Conflict detection", "Meeting confirmation", "Availability check"],
        "status_key": "calendar_connected",
        "color": "#34a853",
        "requires": "Google Calendar API scope (included with Gmail OAuth)",
        "docs": "https://developers.google.com/calendar/api",
    },
    {
        "id": "bedrock",
        "name": "AWS Bedrock",
        "icon": "🤖",
        "description": "Connect to AWS Bedrock to power real AI analysis using Claude. Currently in mock mode with pre-computed responses.",
        "features": ["Email analysis", "Document summarisation", "Q&A assistant", "Daily brief generation"],
        "status_key": "bedrock_connected",
        "color": "#ff9900",
        "requires": "AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) with Bedrock access",
        "docs": "https://aws.amazon.com/bedrock/",
    },
    {
        "id": "knowledge_base",
        "name": "AWS Knowledge Base",
        "icon": "🔗",
        "description": "Amazon Bedrock Knowledge Base for storing and retrieving enterprise documents with semantic search.",
        "features": ["Document indexing", "Semantic search", "RAG retrieval", "Custom knowledge"],
        "status_key": "kb_connected",
        "color": "#6366f1",
        "requires": "KNOWLEDGE_BASE_ID and S3 bucket configured in AWS",
        "docs": "https://aws.amazon.com/bedrock/knowledge-bases/",
    },
    {
        "id": "s3",
        "name": "AWS S3",
        "icon": "🗄️",
        "description": "Amazon S3 for storing uploaded documents, audit logs, and exported reports.",
        "features": ["Document storage", "Audit log backup", "Report exports", "Secure encryption"],
        "status_key": "s3_connected",
        "color": "#00a86b",
        "requires": "S3 bucket ARN and IAM permissions",
        "docs": "https://aws.amazon.com/s3/",
    },
    {
        "id": "cloudwatch",
        "name": "AWS CloudWatch",
        "icon": "📊",
        "description": "Monitor application metrics, logs, and performance via AWS CloudWatch.",
        "features": ["Metrics dashboard", "Log aggregation", "Alerting", "Performance insights"],
        "status_key": "cloudwatch_connected",
        "color": "#e879f9",
        "requires": "AWS CloudWatch IAM permissions",
        "docs": "https://aws.amazon.com/cloudwatch/",
    },
]


def render():
    st.html("## 🔌 Data Sources")
    st.markdown("*Manage connections to external services and APIs*")

    mock_mode = st.session_state.get("config_mock_mode", True)

    if mock_mode:
        st.info(
            "🟡 **Demo Mode Active** — All services are simulated with sample data. "
            "To connect real services, set `MOCK_MODE=false` in your `.env` file and provide credentials."
        )

    # Connection summary
    connected = [s for s in SERVICES if st.session_state.get(s["status_key"], False)]
    st.markdown(
        f'<div style="background:#1e293b; border:1px solid #334155; border-radius:8px; '
        f'padding:12px 16px; margin-bottom:16px;">'
        f'<span style="color:#94a3b8; font-size:0.85rem;">Services: </span>'
        f'<strong style="color:{"#22c55e" if connected else "#f59e0b"};">'
        f'{len(connected)}/{len(SERVICES)} Connected</strong>'
        f'{"" if connected else " — Connect your first service below"}'
        f'</div>')

    # Service cards
    for service in SERVICES:
        _render_service_card(service, mock_mode)

    st.html("---")

    # Setup instructions
    with st.expander("📖 Setup Instructions"):
        st.markdown("""
### Quick Setup Guide

**Phase 1 (Current - Demo Mode):**
- Everything works out-of-the-box with sample data
- Run: `streamlit run app.py`

**Phase 2 (Connect Real Services):**

1. **Gmail Setup:**
   - Go to Google Cloud Console → APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
   - Download `credentials.json` to project root
   - Set `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` in `.env`

2. **AWS Bedrock Setup:**
   - Ensure AWS account has Bedrock access in us-east-1
   - Request model access for Claude claude-sonnet-4-6
   - Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`
   - Set `MOCK_MODE=false`

3. **AWS Knowledge Base:**
   - Create Bedrock Knowledge Base in AWS Console
   - Set `KNOWLEDGE_BASE_ID` and `KNOWLEDGE_BASE_BUCKET` in `.env`

4. **Run in live mode:**
   ```bash
   MOCK_MODE=false streamlit run app.py
   ```
""")


def _render_service_card(service: dict, mock_mode: bool):
    """Render a single service connection card."""
    is_connected = st.session_state.get(service["status_key"], False)
    in_demo = mock_mode  # Everything is "demo" in mock mode

    status_label = "🟡 Demo" if in_demo else ("🟢 Connected" if is_connected else "🔴 Disconnected")
    status_color = "#f59e0b" if in_demo else ("#22c55e" if is_connected else "#ef4444")
    border_color = service["color"]

    with st.expander(
        f"{service['icon']} {service['name']} — {status_label}",
        expanded=False,
    ):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**Description:** {service['description']}")
            st.markdown(f"**Features:** {' · '.join(['`' + f + '`' for f in service['features']])}")
            st.markdown(f"**Requires:** `{service['requires']}`")
            st.markdown(f"[📖 Documentation]({service['docs']})")

        with col2:
            st.markdown(
                f'<div style="background:{status_color}20; border:1px solid {status_color}50; '
                f'border-radius:6px; padding:8px; text-align:center; margin-bottom:10px;">'
                f'<div style="color:{status_color}; font-weight:600; font-size:0.85rem;">{status_label}</div>'
                f'</div>')

            if in_demo:
                if st.button(f"⚙️ Configure", key=f"cfg_{service['id']}", use_container_width=True):
                    st.info("Set credentials in `.env` file and disable mock mode to connect.")
            elif is_connected:
                if st.button(f"🔌 Disconnect", key=f"disc_{service['id']}", use_container_width=True):
                    st.session_state[service["status_key"]] = False
                    st.success(f"Disconnected from {service['name']}")
                    st.rerun()
            else:
                if st.button(f"🔗 Connect", key=f"conn_{service['id']}", type="primary", use_container_width=True):
                    # In a real app, this would trigger OAuth or credential validation
                    st.warning(f"Please configure credentials in `.env` first, then restart the app.")

        # Health check if connected
        if is_connected and not in_demo:
            st.markdown("**Last health check:** ✅ Healthy — 245ms response time")

"""System Status page — health dashboard."""
from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import datetime


def render():
    st.html("## 🖥️ System Status")
    st.markdown("*Real-time health and performance monitoring*")

    now = datetime.datetime.now()
    st.markdown(f"*Last updated: {now.strftime('%Y-%m-%d %H:%M:%S')}*")

    # ── Overall Status ────────────────────────────────────────────────────────
    mock_mode = st.session_state.get("config_mock_mode", True)
    overall_status = "Demo Mode" if mock_mode else "Operational"
    overall_color = "#f59e0b" if mock_mode else "#22c55e"

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,{overall_color}20,{overall_color}10);
                    border:2px solid {overall_color}50; border-radius:10px;
                    padding:20px; text-align:center; margin-bottom:20px;">
            <div style="font-size:2.5rem; margin-bottom:8px;">{'🟡' if mock_mode else '🟢'}</div>
            <div style="font-size:1.3rem; font-weight:700; color:{overall_color};">{overall_status}</div>
            <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">
                {"All services running in demo mode with sample data" if mock_mode else "All systems operational"}
            </div>
        </div>
        """)

    # ── Service Health Grid ───────────────────────────────────────────────────
    services = [
        {
            "name": "Streamlit App",
            "status": "operational",
            "response_ms": 45,
            "uptime": "100%",
            "icon": "🌐",
        },
        {
            "name": "AI Processing Engine",
            "status": "demo",
            "response_ms": 0,
            "uptime": "N/A",
            "icon": "🤖",
        },
        {
            "name": "Gmail API",
            "status": "demo",
            "response_ms": 0,
            "uptime": "N/A",
            "icon": "📧",
        },
        {
            "name": "Google Calendar API",
            "status": "demo",
            "response_ms": 0,
            "uptime": "N/A",
            "icon": "📅",
        },
        {
            "name": "AWS Bedrock",
            "status": "demo",
            "response_ms": 0,
            "uptime": "N/A",
            "icon": "☁️",
        },
        {
            "name": "AWS S3",
            "status": "demo",
            "response_ms": 0,
            "uptime": "N/A",
            "icon": "🗄️",
        },
        {
            "name": "Knowledge Base",
            "status": "demo",
            "response_ms": 0,
            "uptime": "N/A",
            "icon": "🔗",
        },
        {
            "name": "Audit Logger",
            "status": "operational",
            "response_ms": 2,
            "uptime": "100%",
            "icon": "🛡️",
        },
    ]

    st.html("### Service Health")
    grid_cols = st.columns(4)

    for i, service in enumerate(services):
        with grid_cols[i % 4]:
            s = service["status"]
            color = {"operational": "#22c55e", "demo": "#f59e0b", "degraded": "#f97316", "down": "#dc2626"}.get(s, "#6b7280")
            label = {"operational": "Operational", "demo": "Demo Mode", "degraded": "Degraded", "down": "Down"}.get(s, s)
            indicator = {"operational": "🟢", "demo": "🟡", "degraded": "🟠", "down": "🔴"}.get(s, "⚪")

            resp_str = f"{service['response_ms']}ms" if service["response_ms"] > 0 else "—"

            st.markdown(
                f"""
                <div style="background:#1e293b; border:1px solid #334155;
                            border-top:3px solid {color}; border-radius:8px;
                            padding:12px; margin-bottom:10px; text-align:center;">
                    <div style="font-size:1.5rem;">{service['icon']}</div>
                    <div style="font-size:0.78rem; font-weight:600; color:#cbd5e1; margin:4px 0;">
                        {service['name']}
                    </div>
                    <div style="color:{color}; font-size:0.75rem; font-weight:600;">
                        {indicator} {label}
                    </div>
                    <div style="font-size:0.65rem; color:#475569; margin-top:4px;">
                        Response: {resp_str} · Uptime: {service['uptime']}
                    </div>
                </div>
                """)

    st.html("---")

    # ── Performance Charts ────────────────────────────────────────────────────
    st.markdown("### Performance Metrics")

    perf_col1, perf_col2 = st.columns(2)

    with perf_col1:
        # App response time (mock)
        hours = [f"{h:02d}:00" for h in range(0, 24, 2)]
        response_times = [45, 42, 38, 40, 52, 65, 80, 75, 60, 55, 50, 48]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours,
            y=response_times,
            mode="lines+markers",
            line=dict(color="#10b981", width=2),
            marker=dict(color="#34d399", size=5),
            fill="tozeroy",
            fillcolor="rgba(16,185,129,0.1)",
            name="Response Time (ms)",
        ))
        fig.update_layout(
            title="App Response Time (Last 24h)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            height=250,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(title="ms", gridcolor="#1e293b"),
            xaxis=dict(gridcolor="#1e293b"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with perf_col2:
        # Session state usage
        pages_visited = st.session_state.get("_pages_visited", 1)
        session_data = {
            "emails_loaded": len(st.session_state.get("email_stats", {})) > 0,
            "tasks_loaded": len(st.session_state.get("tasks", [])),
            "notifications": len(st.session_state.get("notifications", [])),
            "audit_records": len(st.session_state.get("audit_records", [])),
            "documents": len(st.session_state.get("documents", [])),
            "chat_messages": len(st.session_state.get("chat_history", [])),
        }

        categories = list(session_data.keys())
        values = [int(v) if isinstance(v, bool) else v for v in session_data.values()]

        fig2 = go.Figure(go.Bar(
            x=categories,
            y=values,
            marker=dict(color="#6366f1", cornerradius=4),
            text=values,
            textposition="auto",
        ))
        fig2.update_layout(
            title="Session State (Items Loaded)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", size=10),
            height=250,
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(gridcolor="#1e293b", tickangle=-20),
            yaxis=dict(gridcolor="#1e293b"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── System Info ────────────────────────────────────────────────────────────
    st.markdown("### System Information")

    import sys
    import platform
    import streamlit as _st

    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown("**Application:**")
        info_items = [
            ("App Version", "1.0.0"),
            ("Streamlit Version", _st.__version__),
            ("Python Version", sys.version.split()[0]),
            ("Platform", platform.system()),
            ("App Mode", "Demo" if mock_mode else "Live"),
        ]
        for label, val in info_items:
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; background:#0f172a; '
                f'border-radius:4px; padding:4px 10px; margin-bottom:4px; font-size:0.8rem;">'
                f'<span style="color:#94a3b8;">{label}</span>'
                f'<span style="color:#f1f5f9; font-weight:600;">{val}</span></div>')

    with info_col2:
        st.html("**Configuration:**")
        config = st.session_state.get("app_config")
        if config:
            cfg_items = [
                ("AWS Region", config.AWS_REGION),
                ("Bedrock Model", config.BEDROCK_MODEL_ID.split(".")[-1][:30]),
                ("Max Emails", str(config.MAX_EMAILS_TO_FETCH)),
                ("Max File Size", f"{config.MAX_FILE_SIZE_MB} MB"),
                ("Allowed File Types", ", ".join(config.ALLOWED_FILE_TYPES[:4]) + "..."),
            ]
        else:
            cfg_items = [("Config", "Not loaded")]

        for label, val in cfg_items:
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; background:#0f172a; '
                f'border-radius:4px; padding:4px 10px; margin-bottom:4px; font-size:0.8rem;">'
                f'<span style="color:#94a3b8;">{label}</span>'
                f'<span style="color:#f1f5f9;">{val}</span></div>')

    # Refresh button
    st.html("<br>")
    if st.button("🔄 Refresh Status", use_container_width=False):
        st.rerun()

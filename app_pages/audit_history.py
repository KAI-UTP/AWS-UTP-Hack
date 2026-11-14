"""Audit History page."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from services.audit_service import AuditService
from models.audit_models import AuditRecord


def render():
    st.html("## 🛡️ Audit History")
    st.markdown("*Complete audit trail of all AI actions and system events*")

    audit = st.session_state.get("audit_service")
    if not audit:
        audit = AuditService()
        st.session_state["audit_service"] = audit

    audit.seed_demo_records()

    # ── Stats ─────────────────────────────────────────────────────────────────
    stats = audit.get_stats()
    s_cols = st.columns(4)
    with s_cols[0]:
        st.metric("Total Events", stats["total"])
    with s_cols[1]:
        st.metric("Errors", stats["errors"])
    with s_cols[2]:
        top_action = stats["top_actions"][0][0] if stats["top_actions"] else "—"
        st.metric("Top Action", top_action)
    with s_cols[3]:
        resource_types = len(stats["by_resource"])
        st.metric("Resource Types", resource_types)

    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────────────────────
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.5, 1.5, 1])

    with f_col1:
        action_search = st.text_input("🔍 Search actions", placeholder="analyze_email, upload...", key="audit_search")
    with f_col2:
        resource_filter = st.selectbox(
            "Resource Type",
            ["All", "email", "document", "task", "calendar", "knowledge", "brief", "page", "gmail", "bedrock"],
            key="audit_resource",
        )
    with f_col3:
        success_filter = st.selectbox("Status", ["All", "Success Only", "Errors Only"], key="audit_status")
    with f_col4:
        st.markdown("<br>")
        limit = st.selectbox("Show", [50, 100, 200], key="audit_limit")

    # ── Load records ──────────────────────────────────────────────────────────
    records = audit.get_records(
        action_filter=action_search if action_search else None,
        resource_type_filter=resource_filter if resource_filter != "All" else None,
        success_only=success_filter == "Success Only",
        limit=int(limit),
    )

    if success_filter == "Errors Only":
        records = [r for r in records if not r.success]

    if not records:
        st.info("No audit records match the current filters.")
        return

    # ── Table ─────────────────────────────────────────────────────────────────
    st.markdown(f"**{len(records)} record(s)**")

    rows = []
    for r in records:
        from utils.date_utils import format_relative
        rows.append({
            "Time": r.timestamp[:19].replace("T", " "),
            "Action": r.action,
            "Resource Type": r.resource_type,
            "Resource ID": (r.resource_id or "")[:20],
            "Status": "✅ Success" if r.success else "❌ Error",
            "Duration": f"{r.duration_ms}ms" if r.duration_ms else "—",
            "User": r.user_id,
            "Details": str(r.details)[:60] if r.details else "—",
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Duration": st.column_config.TextColumn("Duration", width="small"),
        },
    )

    # Export
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Export Audit Log CSV",
        csv,
        "audit_history.csv",
        "text/csv",
    )

    # ── Action frequency chart ─────────────────────────────────────────────────
    if stats["top_actions"]:
        st.markdown("---")
        st.markdown("### Top Actions")

        import plotly.graph_objects as go

        top = stats["top_actions"][:8]
        actions = [t[0] for t in top]
        counts = [t[1] for t in top]

        fig = go.Figure(go.Bar(
            y=actions,
            x=counts,
            orientation="h",
            marker=dict(color="#6366f1", cornerradius=4),
            text=counts,
            textposition="auto",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            height=300,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(gridcolor="#1e293b"),
        )
        st.plotly_chart(fig, use_container_width=True)

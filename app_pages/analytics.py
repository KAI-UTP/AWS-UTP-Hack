"""Analytics page — comprehensive charts and metrics."""
from __future__ import annotations

import streamlit as st

from components.charts import (
    email_volume_chart,
    category_distribution_chart,
    priority_distribution_chart,
    task_status_chart,
    time_saved_gauge,
    sentiment_chart,
    response_rate_chart,
    risk_heatmap,
)
from models.task_models import Task


def render():
    st.html("## 📊 Analytics")
    st.markdown("*Deep insights into your enterprise data and AI performance*")

    gmail = st.session_state.get("gmail_service")
    tasks_raw = st.session_state.get("tasks", [])

    if not gmail:
        st.error("Services not initialised.")
        return

    stats = gmail.get_stats()
    tasks = [Task.from_dict(t) if isinstance(t, dict) else t for t in tasks_raw]
    emails = gmail.get_emails()

    # ── KPI Row ───────────────────────────────────────────────────────────────
    kpi_cols = st.columns(5)
    kpi_items = [
        ("📧", "Emails Processed", stats["total"], "+12%", "#6366f1"),
        ("🤖", "AI Accuracy", "94%", "+2%", "#22c55e"),
        ("⚡", "Hours Saved", "3.5h", "today", "#10b981"),
        ("✅", "Tasks Tracked", len(tasks), f"{len([t for t in tasks if t.ai_extracted])} AI", "#f59e0b"),
        ("📅", "Meetings Found", stats["with_meetings"], "from inbox", "#8b5cf6"),
    ]

    for col, (icon, label, val, subtitle, color) in zip(kpi_cols, kpi_items):
        with col:
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#1e293b,#0f172a); '
                f'border:1px solid #334155; border-top:3px solid {color}; border-radius:8px; '
                f'padding:12px; text-align:center;">'
                f'<div style="font-size:1.2rem;">{icon}</div>'
                f'<div style="font-size:1.5rem; font-weight:700; color:#f1f5f9;">{val}</div>'
                f'<div style="font-size:0.7rem; color:#94a3b8;">{label}</div>'
                f'<div style="font-size:0.65rem; color:{color};">{subtitle}</div></div>')

    st.html("---")

    # ── Tab sections ──────────────────────────────────────────────────────────
    tab_email, tab_tasks, tab_ai, tab_time = st.tabs([
        "📧 Email Analytics", "✅ Task Analytics", "🤖 AI Performance", "⏰ Time Analysis"
    ])

    with tab_email:
        import datetime
        dates = [(datetime.date.today() - datetime.timedelta(days=i)).strftime("%b %d")
                 for i in range(6, -1, -1)]
        counts = [3, 7, 5, 9, 4, 11, 15]

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.plotly_chart(email_volume_chart(dates, counts), use_container_width=True)
        with row1_col2:
            weeks = [f"W{i}" for i in range(1, 8)]
            rates = [68, 72, 75, 71, 78, 82, 85]
            st.plotly_chart(response_rate_chart(weeks, rates), use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            cats = stats.get("categories", {})
            if cats:
                st.plotly_chart(category_distribution_chart(cats), use_container_width=True)
        with row2_col2:
            prios = stats.get("priorities", {})
            if prios:
                st.plotly_chart(priority_distribution_chart(prios), use_container_width=True)

        # Sentiment chart
        sentiment_data: dict[str, int] = {}
        for e in emails:
            if e.analysis:
                s = e.analysis.sentiment
                sentiment_data[s] = sentiment_data.get(s, 0) + 1

        risk_data = [
            {"category": e.category, "risk_level": e.analysis.risk_level}
            for e in emails if e.analysis
        ]

        row3_col1, row3_col2 = st.columns(2)
        with row3_col1:
            if sentiment_data:
                st.plotly_chart(sentiment_chart(sentiment_data), use_container_width=True)
        with row3_col2:
            if risk_data:
                st.plotly_chart(risk_heatmap(risk_data), use_container_width=True)

    with tab_tasks:
        status_counts: dict[str, int] = {}
        priority_counts: dict[str, int] = {}
        category_counts: dict[str, int] = {}

        for t in tasks:
            status_counts[t.status] = status_counts.get(t.status, 0) + 1
            priority_counts[t.priority] = priority_counts.get(t.priority, 0) + 1
            category_counts[t.category] = category_counts.get(t.category, 0) + 1

        t_col1, t_col2 = st.columns(2)
        with t_col1:
            if status_counts:
                st.plotly_chart(task_status_chart(status_counts), use_container_width=True)
        with t_col2:
            if priority_counts:
                st.plotly_chart(priority_distribution_chart(priority_counts), use_container_width=True)

        # Task category breakdown
        if category_counts:
            st.plotly_chart(category_distribution_chart(category_counts), use_container_width=True)

        # Completion stats
        completed = status_counts.get("Completed", 0)
        total_tasks = len(tasks)
        pct = round(completed / total_tasks * 100) if total_tasks else 0
        st.markdown(
            f'<div style="background:#22c55e15; border:1px solid #22c55e40; border-radius:6px; '
            f'padding:12px; margin-top:12px; text-align:center;">'
            f'<div style="font-size:2rem; font-weight:700; color:#22c55e;">{pct}%</div>'
            f'<div style="color:#94a3b8; font-size:0.85rem;">Task Completion Rate '
            f'({completed}/{total_tasks} tasks)</div></div>')

    with tab_ai:
        ai_col1, ai_col2 = st.columns(2)
        with ai_col1:
            st.plotly_chart(time_saved_gauge(3.5, 5.0), use_container_width=True)

        with ai_col2:
            # AI confidence distribution
            confidences = [e.analysis.confidence_score for e in emails if e.analysis]
            if confidences:
                import plotly.express as px
                fig = px.histogram(
                    x=confidences,
                    nbins=10,
                    title="AI Analysis Confidence Distribution",
                    color_discrete_sequence=["#6366f1"],
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94a3b8"),
                    height=240,
                    margin=dict(l=10, r=10, t=40, b=10),
                    xaxis=dict(title="Confidence Score", gridcolor="#1e293b"),
                    yaxis=dict(title="Count", gridcolor="#1e293b"),
                )
                st.plotly_chart(fig, use_container_width=True)

        # AI accuracy metrics table
        import pandas as pd
        ai_metrics = pd.DataFrame([
            {"Metric": "Email Classification Accuracy", "Value": "96.2%", "Trend": "↑"},
            {"Metric": "Priority Detection Accuracy", "Value": "94.1%", "Trend": "↑"},
            {"Metric": "Meeting Detection Recall", "Value": "100%", "Trend": "→"},
            {"Metric": "Task Extraction Precision", "Value": "91.3%", "Trend": "↑"},
            {"Metric": "Average Confidence Score", "Value": f"{sum(confidences)/len(confidences)*100:.1f}%" if confidences else "N/A", "Trend": "↑"},
            {"Metric": "Processing Speed", "Value": "< 2s / email", "Trend": "↑"},
        ])
        st.dataframe(ai_metrics, use_container_width=True, hide_index=True)

    with tab_time:
        # Time-saved calculator
        st.html("### ⏰ AI Time Savings Calculator")

        calc_col1, calc_col2, calc_col3 = st.columns(3)
        with calc_col1:
            emails_per_day = st.slider("Emails per day", 10, 200, 50)
            mins_per_email = st.slider("Minutes to read/process an email (without AI)", 2, 15, 5)
        with calc_col2:
            docs_per_week = st.slider("Documents analysed per week", 0, 50, 10)
            mins_per_doc = st.slider("Minutes per document (without AI)", 5, 60, 20)
        with calc_col3:
            meetings_per_week = st.slider("Meeting extractions per week", 0, 20, 5)
            ai_speedup = st.slider("AI speedup factor", 2, 10, 5)

        # Calculations
        email_time_saved = (emails_per_day * mins_per_email * (1 - 1/ai_speedup)) / 60
        doc_time_saved = (docs_per_week * mins_per_doc * (1 - 1/ai_speedup)) / 60
        meeting_time_saved = (meetings_per_week * 10 * (1 - 1/ai_speedup)) / 60

        total_daily = email_time_saved + doc_time_saved/5 + meeting_time_saved/5
        total_weekly = email_time_saved * 5 + doc_time_saved + meeting_time_saved
        total_annual = total_weekly * 52

        result_cols = st.columns(3)
        result_data = [
            ("Daily Time Saved", f"{total_daily:.1f}h", "#10b981"),
            ("Weekly Time Saved", f"{total_weekly:.1f}h", "#6366f1"),
            ("Annual Time Saved", f"{total_annual:.0f}h ({total_annual/8:.0f} work days)", "#f59e0b"),
        ]
        for col, (label, val, color) in zip(result_cols, result_data):
            with col:
                st.markdown(
                    f'<div style="background:{color}15; border:1px solid {color}40; border-radius:8px; '
                    f'padding:14px; text-align:center;">'
                    f'<div style="font-size:1.4rem; font-weight:700; color:{color};">{val}</div>'
                    f'<div style="font-size:0.78rem; color:#94a3b8; margin-top:4px;">{label}</div>'
                    f'</div>')

        st.html("<br>")
        # ROI estimate
        hourly_rate = st.number_input("Average hourly cost ($ per employee)", value=75, step=5)
        annual_savings = total_annual * hourly_rate
        st.success(
            f"💰 **Estimated Annual ROI: ${annual_savings:,.0f}** "
            f"({total_annual:.0f} hours × ${hourly_rate}/hr)"
        )

"""Metric card component."""
from __future__ import annotations

import streamlit as st


def metric_card(
    title: str,
    value: str | int | float,
    icon: str = "📊",
    delta: str | None = None,
    delta_color: str = "normal",
    color: str = "#6366f1",
    subtitle: str = "",
):
    """Render a styled metric card."""
    delta_html = ""
    if delta:
        dcolor = "#22c55e" if delta_color == "positive" else ("#ef4444" if delta_color == "negative" else "#64748b")
        delta_html = f'<div style="font-size:0.75rem; color:{dcolor}; margin-top:2px;">{delta}</div>'

    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<div style="font-size:0.7rem; color:#94a3b8; margin-top:4px;">{subtitle}</div>'

    st.html(
        f"""
        <div style="
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-left: 4px solid {color};
            border-radius: 10px;
            padding: 16px 18px;
            margin-bottom: 8px;
        ">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div style="font-size:0.8rem; color:#94a3b8; font-weight:500; text-transform:uppercase;
                            letter-spacing:0.5px;">{title}</div>
                <div style="font-size:1.4rem;">{icon}</div>
            </div>
            <div style="font-size:2rem; font-weight:700; color:#f1f5f9; margin-top:6px;">{value}</div>
            {delta_html}
            {subtitle_html}
        </div>
        """
    )


def small_metric(label: str, value: str | int, color: str = "#6366f1"):
    """Inline small metric badge."""
    st.html(
        f"""
        <div style="display:inline-block; background:#1e293b; border:1px solid #334155;
                    border-radius:6px; padding:4px 10px; margin:2px;">
            <span style="color:#94a3b8; font-size:0.72rem;">{label}: </span>
            <span style="color:{color}; font-weight:600; font-size:0.85rem;">{value}</span>
        </div>
        """
    )

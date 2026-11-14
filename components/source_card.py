"""Source citation card for Knowledge Assistant."""
from __future__ import annotations

import streamlit as st


SOURCE_ICONS = {
    "email": "📧",
    "document": "📄",
    "task": "✅",
    "calendar": "📅",
    "knowledge": "🔗",
    "Email Analysis": "📧",
    "Knowledge Base": "🔗",
}


def render_source_card(source: dict, index: int = 0):
    """Render a source citation card."""
    source_type = source.get("source_type", "knowledge")
    source_title = source.get("source_title", f"Source {index + 1}")
    content = source.get("content", "")
    relevance = source.get("relevance_score", source.get("relevance", 0.8))
    icon = SOURCE_ICONS.get(source_type, SOURCE_ICONS.get(source_title, "📎"))

    relevance_pct = int(relevance * 100)
    rel_color = "#22c55e" if relevance_pct >= 80 else "#f59e0b" if relevance_pct >= 60 else "#ef4444"

    snippet = content[:200] + "..." if content and len(content) > 200 else content

    snippet_div = (
        f'<div style="font-size:0.72rem; color:#64748b; font-style:italic;">{snippet}</div>'
        if snippet else ''
    )
    st.html(
        f"""
        <div style="
            background:#0f172a;
            border:1px solid #1e293b;
            border-left:3px solid #6366f1;
            border-radius:6px;
            padding:8px 12px;
            margin-top:4px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <div style="font-size:0.75rem; font-weight:600; color:#818cf8;">
                    {icon} {source_title}
                </div>
                <span style="font-size:0.65rem; color:{rel_color};">
                    {relevance_pct}% relevant
                </span>
            </div>
            {snippet_div}
        </div>
        """
    )

"""Email card display component."""
from __future__ import annotations

import streamlit as st

from models.email_models import EmailData
from utils.date_utils import format_relative
from utils.text_utils import truncate


PRIORITY_COLORS = {
    "Critical": "#dc2626",
    "High": "#f97316",
    "Medium": "#3b82f6",
    "Low": "#22c55e",
}

CATEGORY_COLORS = {
    "Technical": "#8b5cf6",
    "Finance": "#f59e0b",
    "HR": "#06b6d4",
    "Meeting": "#10b981",
    "Newsletter": "#64748b",
    "Spam": "#6b7280",
    "Customer": "#ec4899",
    "Project Update": "#6366f1",
    "General": "#475569",
}


def priority_badge(priority: str) -> str:
    color = PRIORITY_COLORS.get(priority, "#6b7280")
    return (
        f'<span style="background:rgba(0,0,0,0.3); color:{color}; border:1px solid {color}; '
        f'border-radius:4px; padding:2px 8px; font-size:0.7rem; font-weight:600;">'
        f'{priority}</span>'
    )


def category_badge(category: str) -> str:
    color = CATEGORY_COLORS.get(category, "#475569")
    return (
        f'<span style="background:rgba(0,0,0,0.3); color:{color}; border:1px solid {color}; '
        f'border-radius:4px; padding:2px 8px; font-size:0.7rem;">{category}</span>'
    )


def render_email_card(email: EmailData, index: int = 0):
    """Render a compact email card with key details."""
    analysis = email.analysis
    priority = analysis.priority if analysis else "Medium"
    category = analysis.category if analysis else "General"
    border_color = PRIORITY_COLORS.get(priority, "#334155")
    unread_dot = "&#128309; " if email.is_unread else ""

    # Action items section
    action_items_html = ""
    if analysis and analysis.action_items:
        items = "".join(
            f'<li style="color:#cbd5e1; font-size:0.73rem; margin-bottom:2px;">{item}</li>'
            for item in analysis.action_items[:3]
        )
        action_items_html = f'<ul style="margin:6px 0 0 0; padding-left:18px;">{items}</ul>'

    # Badges row
    badges = []
    if analysis and analysis.deadline:
        urgency = analysis.deadline.urgency
        urg_color = "#dc2626" if urgency == "immediate" else "#f97316" if urgency == "high" else "#3b82f6"
        badges.append(
            f'<span style="background:rgba(0,0,0,0.3); color:{urg_color}; border:1px solid {urg_color}; '
            f'border-radius:4px; padding:2px 8px; font-size:0.68rem;">&#9200; {analysis.deadline.text[:40]}</span>'
        )
    if analysis and analysis.meeting_detected:
        m = analysis.meeting_detected
        badges.append(
            f'<span style="background:rgba(0,0,0,0.3); color:#10b981; border:1px solid #10b981; '
            f'border-radius:4px; padding:2px 8px; font-size:0.68rem;">&#128197; {m.title[:30]}</span>'
        )
    if email.has_attachments:
        badges.append(
            '<span style="background:rgba(0,0,0,0.3); color:#6366f1; border:1px solid #6366f1; '
            'border-radius:4px; padding:2px 8px; font-size:0.68rem;">&#128206; Attachments</span>'
        )
    if analysis and analysis.requires_response:
        badges.append(
            '<span style="background:rgba(0,0,0,0.3); color:#f97316; border:1px solid #f97316; '
            'border-radius:4px; padding:2px 8px; font-size:0.68rem;">&#8617; Reply needed</span>'
        )
    badges_html = (
        f'<div style="margin-top:8px; display:flex; flex-wrap:wrap; gap:4px;">{"".join(badges)}</div>'
        if badges else ""
    )

    # Confidence
    confidence_html = ""
    if analysis:
        conf_pct = int(analysis.confidence_score * 100)
        conf_color = "#22c55e" if conf_pct >= 90 else "#f59e0b" if conf_pct >= 70 else "#ef4444"
        confidence_html = (
            f'<div style="margin-top:8px; font-size:0.68rem; color:#64748b;">'
            f'AI Confidence: <span style="color:{conf_color};">{conf_pct}%</span></div>'
        )

    summary_text = truncate(analysis.summary if analysis else email.snippet, 180)
    sender_display = email.sender_name or email.sender

    st.html(
        f"""
        <div style="
            background:#1e293b;
            border:1px solid #334155;
            border-left:4px solid {border_color};
            border-radius:8px;
            padding:14px 16px;
            margin-bottom:8px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:4px;">
                <div style="flex:1; min-width:0;">
                    <div style="font-size:0.85rem; font-weight:600; color:#f1f5f9; margin-bottom:4px;
                                white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        {unread_dot}{email.subject}
                    </div>
                    <div style="font-size:0.75rem; color:#94a3b8;">
                        From: <strong style="color:#cbd5e1;">{sender_display}</strong>
                        &nbsp;&#183;&nbsp; {format_relative(email.date)}
                    </div>
                </div>
                <div style="display:flex; gap:6px; flex-wrap:wrap; align-items:center;">
                    {priority_badge(priority)}
                    {category_badge(category)}
                </div>
            </div>
            <div style="font-size:0.78rem; color:#94a3b8; margin-top:8px; line-height:1.5;">
                {summary_text}
            </div>
            {action_items_html}
            {badges_html}
            {confidence_html}
        </div>
        """
    )

    # Detail expander (native Streamlit, outside the HTML block)
    with st.expander("View Details", expanded=False):
        render_email_detail(email)


def render_email_detail(email: EmailData):
    """Render the full email detail view."""
    analysis = email.analysis

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**From:** {email.sender_name} <{email.sender}>")
        st.markdown(f"**To:** {', '.join(email.recipients[:3])}")
        st.markdown(f"**Date:** {email.date}")
        if email.has_attachments:
            att_names = ", ".join(a.name for a in email.attachments)
            st.markdown(f"**Attachments:** 📎 {att_names}")

    with col2:
        if analysis:
            st.markdown(f"**Risk Level:** {analysis.risk_level}")
            st.markdown(f"**Est. Handle:** {analysis.estimated_time_to_handle} min")

    st.markdown("**Message Body:**")
    st.text_area("Email body", email.body, height=200, disabled=True, key=f"body_{email.id}", label_visibility="collapsed")

    if analysis:
        st.markdown("---")
        if analysis.key_entities:
            st.markdown(f"**Key Entities:** {', '.join(analysis.key_entities)}")
        if analysis.tags:
            st.markdown(f"**Tags:** {' · '.join(f'`{t}`' for t in analysis.tags)}")
        if analysis.action_items:
            st.markdown("**Full Action Items:**")
            for item in analysis.action_items:
                st.markdown(f"- {item}")

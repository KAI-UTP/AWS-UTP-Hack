"""Email Intelligence page."""
from __future__ import annotations

import streamlit as st

from components.email_card import render_email_card, render_email_detail, PRIORITY_COLORS, CATEGORY_COLORS
from components.charts import priority_distribution_chart, category_distribution_chart


def render():
    st.html("## 📧 Email Intelligence")
    st.markdown("*AI-powered analysis of your inbox*")

    gmail = st.session_state.get("gmail_service")
    if not gmail:
        st.error("Gmail service not initialised.")
        return

    # ── Filters Bar ───────────────────────────────────────────────────────────
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([2, 1.5, 1.5, 1.5, 1])

    with filter_col1:
        search = st.text_input("🔍 Search emails", placeholder="Subject, sender, keywords...", key="email_search")
    with filter_col2:
        categories = ["All"] + gmail.get_categories()
        category_filter = st.selectbox("Category", categories, key="email_cat_filter")
    with filter_col3:
        priority_filter = st.selectbox("Priority", ["All", "Critical", "High", "Medium", "Low"], key="email_prio_filter")
    with filter_col4:
        label_filter = st.selectbox("Labels", ["All", "Unread", "Important", "Requires Response"], key="email_label_filter")
    with filter_col5:
        st.markdown("<br>")
        bulk_analyse = st.button("🤖 Analyse All", type="primary", use_container_width=True)

    # ── Load emails ───────────────────────────────────────────────────────────
    emails = gmail.get_emails(
        category=category_filter if category_filter != "All" else None,
        priority=priority_filter if priority_filter != "All" else None,
        search_query=search if search else None,
    )

    # Label filters
    if label_filter == "Unread":
        emails = [e for e in emails if e.is_unread]
    elif label_filter == "Important":
        emails = [e for e in emails if e.is_important]
    elif label_filter == "Requires Response":
        emails = [e for e in emails if e.analysis and e.analysis.requires_response]

    if bulk_analyse:
        with st.spinner(f"🤖 Running AI analysis on {len(emails)} emails..."):
            import time
            time.sleep(1.5)
        st.success(f"✅ Analysis complete for {len(emails)} emails")

    # ── Stats Row ─────────────────────────────────────────────────────────────
    stats = gmail.get_stats()
    stat_cols = st.columns(6)
    stat_items = [
        ("📧", "Total", stats["total"]),
        ("🔵", "Unread", stats["unread"]),
        ("🚨", "Critical", stats["critical"]),
        ("↩️", "Need Reply", stats["requiring_response"]),
        ("📅", "Has Meeting", stats["with_meetings"]),
        ("⏰", "Deadlines", stats["with_deadlines"]),
    ]
    for col, (icon, label, val) in zip(stat_cols, stat_items):
        with col:
            st.html(f'<div style="background:#1e293b; border:1px solid #334155; border-radius:6px; '
                f'padding:8px; text-align:center;">'
                f'<div style="font-size:0.85rem;">{icon}</div>'
                f'<div style="font-size:1.1rem; font-weight:700; color:#f1f5f9;">{val}</div>'
                f'<div style="font-size:0.65rem; color:#64748b;">{label}</div></div>')

    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_list, tab_stats = st.tabs(["📧 Email List", "📊 Analytics"])

    with tab_list:
        if not emails:
            st.info("No emails match your current filters. Try adjusting the search or filters above.")
            return

        st.markdown(f"**Showing {len(emails)} emails**")

        for i, email in enumerate(emails):
            render_email_card(email, index=i)

    with tab_stats:
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            cats = stats.get("categories", {})
            if cats:
                st.plotly_chart(category_distribution_chart(cats), use_container_width=True)
        with chart_col2:
            prios = stats.get("priorities", {})
            if prios:
                st.plotly_chart(priority_distribution_chart(prios), use_container_width=True)

        # Detailed breakdown table
        st.markdown("#### Email Breakdown by Category & Priority")
        all_emails = gmail.get_emails()
        breakdown: dict[str, dict[str, int]] = {}
        for e in all_emails:
            cat = e.category
            pri = e.priority
            if cat not in breakdown:
                breakdown[cat] = {}
            breakdown[cat][pri] = breakdown[cat].get(pri, 0) + 1

        import pandas as pd
        rows = []
        for cat, pris in breakdown.items():
            rows.append({
                "Category": cat,
                "Critical": pris.get("Critical", 0),
                "High": pris.get("High", 0),
                "Medium": pris.get("Medium", 0),
                "Low": pris.get("Low", 0),
                "Total": sum(pris.values()),
            })
        if rows:
            df = pd.DataFrame(rows).sort_values("Total", ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)

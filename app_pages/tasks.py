"""Tasks page — Kanban, Table, Timeline views."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from models.task_models import Task
from components.task_card import render_task_card, PRIORITY_COLORS, STATUS_COLORS


STATUSES = ["Not Started", "In Progress", "Pending", "Completed", "Cancelled"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]


def render():
    st.html("## ✅ Task Manager")
    st.markdown("*AI-extracted and manually created action items*")

    tasks_raw = st.session_state.get("tasks", [])
    tasks = [Task.from_dict(t) if isinstance(t, dict) else t for t in tasks_raw]

    # ── Summary Stats ─────────────────────────────────────────────────────────
    stat_cols = st.columns(6)
    status_counts = {}
    for t in tasks:
        status_counts[t.status] = status_counts.get(t.status, 0) + 1

    overdue = [t for t in tasks if t.is_overdue]
    critical = [t for t in tasks if t.priority == "Critical"]
    unconfirmed = [t for t in tasks if t.ai_extracted and not t.confirmed]

    stat_items = [
        ("📋", "Total", len(tasks), "#6366f1"),
        ("🚨", "Critical", len(critical), "#dc2626"),
        ("⛔", "Overdue", len(overdue), "#ef4444"),
        ("🔄", "In Progress", status_counts.get("In Progress", 0), "#3b82f6"),
        ("✅", "Completed", status_counts.get("Completed", 0), "#22c55e"),
        ("🤖", "AI Pending", len(unconfirmed), "#f59e0b"),
    ]

    for col, (icon, label, val, color) in zip(stat_cols, stat_items):
        with col:
            st.markdown(
                f'<div style="background:#1e293b; border:1px solid #334155; border-left:3px solid {color}; '
                f'border-radius:6px; padding:8px; text-align:center;">'
                f'<div style="font-size:0.85rem;">{icon}</div>'
                f'<div style="font-size:1.2rem; font-weight:700; color:#f1f5f9;">{val}</div>'
                f'<div style="font-size:0.65rem; color:#64748b;">{label}</div></div>')

    st.html("---")

    # ── Filters ───────────────────────────────────────────────────────────────
    filt_col1, filt_col2, filt_col3, filt_col4, filt_col5 = st.columns([2, 1.5, 1.5, 1.5, 1])

    with filt_col1:
        search = st.text_input("🔍 Search tasks", placeholder="Title, description...", key="task_search")
    with filt_col2:
        status_filter = st.selectbox("Status", ["All"] + STATUSES, key="task_status")
    with filt_col3:
        priority_filter = st.selectbox("Priority", ["All"] + PRIORITIES, key="task_priority")
    with filt_col4:
        source_filter = st.selectbox("Source", ["All", "email", "manual", "document"], key="task_source")
    with filt_col5:
        st.markdown("<br>")
        show_ai = st.checkbox("AI only", key="task_ai_only")

    # Apply filters
    filtered = tasks
    if search:
        q = search.lower()
        filtered = [t for t in filtered if q in t.title.lower() or q in t.description.lower()]
    if status_filter != "All":
        filtered = [t for t in filtered if t.status == status_filter]
    if priority_filter != "All":
        filtered = [t for t in filtered if t.priority == priority_filter]
    if source_filter != "All":
        filtered = [t for t in filtered if t.source == source_filter]
    if show_ai:
        filtered = [t for t in filtered if t.ai_extracted]

    # ── View Tabs ─────────────────────────────────────────────────────────────
    tab_kanban, tab_table, tab_timeline = st.tabs(["🗂️ Kanban", "📋 Table", "📅 Timeline"])

    with tab_kanban:
        _render_kanban(filtered)

    with tab_table:
        _render_table(filtered)

    with tab_timeline:
        _render_timeline(filtered)

    # ── Add Task ──────────────────────────────────────────────────────────────
    st.html("---")
    with st.expander("➕ Add New Task"):
        _render_add_task_form()


def _render_kanban(tasks: list[Task]):
    """Render Kanban board with columns for each status."""
    active_statuses = ["Not Started", "In Progress", "Pending", "Completed"]
    cols = st.columns(len(active_statuses))

    for col, status in zip(cols, active_statuses):
        with col:
            color = STATUS_COLORS.get(status, "#6b7280")
            status_tasks = [t for t in tasks if t.status == status]

            st.markdown(
                f'<div style="background:{color}20; border:1px solid {color}50; border-radius:6px; '
                f'padding:6px 10px; margin-bottom:10px; text-align:center;">'
                f'<span style="color:{color}; font-weight:600; font-size:0.8rem;">'
                f'{status} ({len(status_tasks)})</span></div>')

            if not status_tasks:
                st.html('<div style="text-align:center; color:#475569; font-size:0.75rem; padding:20px 0;">Empty</div>')
                continue

            for task in status_tasks:
                render_task_card(task, compact=True, show_actions=True)


def _render_table(tasks: list[Task]):
    """Render tasks as a sortable dataframe."""
    if not tasks:
        st.info("No tasks match current filters.")
        return

    rows = []
    for t in tasks:
        days = None
        if t.due_date:
            from utils.date_utils import days_until
            days = days_until(t.due_date)
        due_str = f"{days}d" if days is not None else "—"
        if days is not None and days < 0:
            due_str = f"⛔ {abs(days)}d overdue"
        elif days == 0:
            due_str = "🔴 Today"

        rows.append({
            "Title": t.title[:60],
            "Status": t.status,
            "Priority": t.priority,
            "Category": t.category,
            "Due": due_str,
            "Assigned": t.assigned_to.split("@")[0] if t.assigned_to else "—",
            "Source": t.source,
            "AI": "🤖" if t.ai_extracted else "👤",
            "Confirmed": "✅" if t.confirmed else "⏳",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)

    # Export
    csv = df.to_csv(index=False)
    st.download_button("📥 Export CSV", csv, "tasks.csv", "text/csv")


def _render_timeline(tasks: list[Task]):
    """Render tasks on a simple timeline by due date."""
    dated_tasks = [t for t in tasks if t.due_date]
    dated_tasks.sort(key=lambda t: t.due_date or "")

    if not dated_tasks:
        st.info("No tasks with due dates in the current filter.")
        return

    import plotly.figure_factory as ff
    import plotly.graph_objects as go
    from utils.date_utils import parse_date
    import datetime

    # Build Gantt data
    gantt_data = []
    today = datetime.date.today()
    for t in dated_tasks[:15]:  # Limit for readability
        try:
            due_dt = parse_date(t.due_date)
            if not due_dt:
                continue
            created_dt = parse_date(t.created_at) if t.created_at else datetime.datetime.combine(today, datetime.time())
            if not created_dt:
                created_dt = datetime.datetime.combine(today, datetime.time())

            gantt_data.append({
                "Task": f"[{t.priority[:1]}] {t.title[:35]}",
                "Start": created_dt.strftime("%Y-%m-%d"),
                "Finish": due_dt.strftime("%Y-%m-%d"),
                "Resource": t.status,
            })
        except Exception:
            continue

    if not gantt_data:
        st.info("Could not parse task dates for timeline.")
        return

    colors = {
        "Not Started": "#64748b",
        "In Progress": "#3b82f6",
        "Pending": "#f59e0b",
        "Completed": "#22c55e",
        "Cancelled": "#6b7280",
    }

    try:
        fig = ff.create_gantt(
            gantt_data,
            colors=colors,
            index_col="Resource",
            show_colorbar=True,
            group_tasks=True,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            height=max(300, len(gantt_data) * 30 + 100),
            margin=dict(l=5, r=5, t=30, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        # Fallback: simple bar chart
        st.info("Timeline chart requires plotly-gantt. Showing table view instead.")
        _render_table(dated_tasks)


def _render_add_task_form():
    """Form to manually add a task."""
    import uuid
    from datetime import date

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Task Title *", key="new_task_title")
        description = st.text_area("Description", key="new_task_desc", height=80)
        category = st.selectbox("Category", ["General", "Technical", "Finance", "HR", "Customer", "Legal", "Project", "Administrative", "Security"], key="new_task_cat")
    with col2:
        priority = st.selectbox("Priority", PRIORITIES, index=2, key="new_task_priority")
        status = st.selectbox("Status", STATUSES, key="new_task_status")
        due_date = st.date_input("Due Date", value=None, key="new_task_due")
        assigned = st.text_input("Assign To (email)", key="new_task_assign")

    if st.button("➕ Add Task", type="primary") and title:
        from datetime import datetime, timezone
        new_task = Task(
            id=f"task_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            status=status,
            priority=priority,
            category=category,
            source="manual",
            assigned_to=assigned,
            created_at=datetime.now(timezone.utc).isoformat(),
            due_date=str(due_date) if due_date else None,
            confirmed=True,
            ai_extracted=False,
        )
        if "tasks" not in st.session_state:
            st.session_state["tasks"] = []
        st.session_state["tasks"].insert(0, new_task.model_dump())
        st.success(f"✅ Task '{title}' added!")
        st.rerun()

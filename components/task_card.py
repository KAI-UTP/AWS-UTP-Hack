"""Task card display component."""
from __future__ import annotations

import streamlit as st

from models.task_models import Task
from utils.date_utils import format_date, days_until


PRIORITY_COLORS = {
    "Critical": "#dc2626",
    "High": "#f97316",
    "Medium": "#3b82f6",
    "Low": "#22c55e",
}

STATUS_COLORS = {
    "Not Started": "#64748b",
    "In Progress": "#3b82f6",
    "Pending": "#f59e0b",
    "Completed": "#22c55e",
    "Cancelled": "#6b7280",
}


def render_task_card(task: Task, compact: bool = False, show_actions: bool = True):
    """Render a task card."""
    prio_color = PRIORITY_COLORS.get(task.priority, "#6b7280")
    status_color = STATUS_COLORS.get(task.status, "#6b7280")

    overdue = task.is_overdue
    border_color = "#dc2626" if overdue else prio_color

    days = days_until(task.due_date) if task.due_date else None
    due_text = ""
    if days is not None:
        if days < 0:
            due_text = f"⛔ {abs(days)}d overdue"
        elif days == 0:
            due_text = "🔴 Due today"
        elif days == 1:
            due_text = "🟡 Due tomorrow"
        else:
            due_text = f"📅 Due in {days}d ({format_date(task.due_date)})"

    ai_badge = ""
    if task.ai_extracted and not task.confirmed:
        ai_badge = (
            '<span style="background:#6366f120; color:#818cf8; border:1px solid #6366f150; '
            'border-radius:4px; padding:1px 6px; font-size:0.65rem;">🤖 AI — Unconfirmed</span> '
        )

    completion_bar = ""
    if task.subtasks:
        pct = int(task.completion_pct)
        bar_color = "#22c55e" if pct == 100 else "#3b82f6"
        completion_bar = (
            f'<div style="margin-top:6px;">'
            f'<div style="font-size:0.68rem; color:#94a3b8; margin-bottom:2px;">Progress: {pct}%</div>'
            f'<div style="background:#334155; border-radius:3px; height:4px;">'
            f'<div style="background:{bar_color}; width:{pct}%; border-radius:3px; height:4px;"></div>'
            f'</div></div>'
        )

    desc_html = (
        f'<div style="font-size:0.73rem; color:#94a3b8; margin-top:4px;">{task.description[:120]}...</div>'
        if not compact and task.description else ''
    )
    due_span = f'<span>{due_text}</span>' if due_text else ''
    assigned_span = (
        f'<span>👤 {task.assigned_to.split("@")[0]}</span>' if task.assigned_to else ''
    )
    st.html(
        f"""
        <div style="
            background:#1e293b;
            border:1px solid #334155;
            border-left:4px solid {border_color};
            border-radius:8px;
            padding:12px 14px;
            margin-bottom:6px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:4px;">
                <div style="font-size:0.83rem; font-weight:600; color:#f1f5f9; flex:1;">
                    {ai_badge}{task.title}
                </div>
                <div style="display:flex; gap:4px;">
                    <span style="background:rgba(0,0,0,0.25); color:{prio_color}; border:1px solid {prio_color};
                        border-radius:4px; padding:1px 7px; font-size:0.68rem;">{task.priority}</span>
                    <span style="background:rgba(0,0,0,0.25); color:{status_color}; border:1px solid {status_color};
                        border-radius:4px; padding:1px 7px; font-size:0.68rem;">{task.status}</span>
                </div>
            </div>
            {desc_html}
            <div style="display:flex; gap:12px; margin-top:6px; flex-wrap:wrap; font-size:0.72rem; color:#64748b;">
                <span>📁 {task.category}</span>
                {due_span}
                <span>⏱️ {task.estimated_hours}h est.</span>
                {assigned_span}
            </div>
            {completion_bar}
        </div>
        """
    )

    if show_actions and not compact:
        _render_task_actions(task)


def _render_task_actions(task: Task):
    """Render confirm/reject/complete buttons for a task."""
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

    tasks_list = st.session_state.get("tasks", [])

    with col1:
        if task.status != "Completed" and st.button(
            "✅ Complete", key=f"complete_{task.id}", use_container_width=True
        ):
            _update_task_status(task.id, "Completed")
            st.success("Task marked complete!")
            st.rerun()

    with col2:
        if not task.confirmed and st.button(
            "👍 Confirm", key=f"confirm_{task.id}", use_container_width=True
        ):
            _confirm_task(task.id)
            st.success("Task confirmed!")
            st.rerun()

    with col3:
        if st.button("🗑️ Remove", key=f"remove_{task.id}", use_container_width=True):
            _remove_task(task.id)
            st.rerun()


def _update_task_status(task_id: str, status: str):
    tasks = st.session_state.get("tasks", [])
    for t in tasks:
        if isinstance(t, dict) and t.get("id") == task_id:
            t["status"] = status
        elif hasattr(t, "id") and t.id == task_id:
            t.status = status


def _confirm_task(task_id: str):
    tasks = st.session_state.get("tasks", [])
    for t in tasks:
        if isinstance(t, dict) and t.get("id") == task_id:
            t["confirmed"] = True
        elif hasattr(t, "id") and t.id == task_id:
            t.confirmed = True


def _remove_task(task_id: str):
    tasks = st.session_state.get("tasks", [])
    st.session_state["tasks"] = [
        t for t in tasks
        if not (isinstance(t, dict) and t.get("id") == task_id)
        and not (hasattr(t, "id") and t.id == task_id)
    ]

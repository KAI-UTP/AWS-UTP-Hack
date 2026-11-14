"""All Plotly chart functions for the analytics pages."""
from __future__ import annotations

from typing import Any
import plotly.graph_objects as go
import plotly.express as px


DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Inter, sans-serif"),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(
        bgcolor="rgba(30,41,59,0.8)",
        bordercolor="#334155",
        borderwidth=1,
    ),
    xaxis=dict(gridcolor="#1e293b", linecolor="#334155"),
    yaxis=dict(gridcolor="#1e293b", linecolor="#334155"),
)

PRIORITY_COLORS = {
    "Critical": "#dc2626",
    "High": "#f97316",
    "Medium": "#3b82f6",
    "Low": "#22c55e",
}

CATEGORY_COLORS_LIST = [
    "#6366f1", "#10b981", "#f59e0b", "#3b82f6",
    "#ec4899", "#8b5cf6", "#06b6d4", "#dc2626",
]


def email_volume_chart(dates: list[str], counts: list[int]) -> go.Figure:
    """Line chart of email volume over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=counts,
        mode="lines+markers",
        line=dict(color="#6366f1", width=2.5),
        marker=dict(color="#818cf8", size=6),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.12)",
        name="Emails",
    ))
    fig.update_layout(
        title="Email Volume (Last 7 Days)",
        **DARK_LAYOUT,
        height=280,
    )
    return fig


def category_distribution_chart(categories: dict[str, int]) -> go.Figure:
    """Donut chart of email categories."""
    labels = list(categories.keys())
    values = list(categories.values())
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=CATEGORY_COLORS_LIST[:len(labels)]),
        textinfo="label+percent",
        textfont=dict(size=10, color="#cbd5e1"),
        hovertemplate="<b>%{label}</b><br>%{value} emails<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        title="Email Categories",
        **DARK_LAYOUT,
        height=300,
        showlegend=False,
    )
    return fig


def priority_distribution_chart(priorities: dict[str, int]) -> go.Figure:
    """Horizontal bar chart of email priorities."""
    order = ["Critical", "High", "Medium", "Low"]
    labels = [p for p in order if p in priorities]
    values = [priorities[p] for p in labels]
    colors = [PRIORITY_COLORS[p] for p in labels]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=colors),
        text=values,
        textposition="auto",
        hovertemplate="<b>%{y}</b>: %{x} emails<extra></extra>",
    ))
    fig.update_layout(
        title="Priority Distribution",
        **DARK_LAYOUT,
        height=220,
    )
    return fig


def task_status_chart(status_counts: dict[str, int]) -> go.Figure:
    """Bar chart for task statuses."""
    status_colors = {
        "Not Started": "#64748b",
        "In Progress": "#3b82f6",
        "Pending": "#f59e0b",
        "Completed": "#22c55e",
        "Cancelled": "#6b7280",
    }
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    colors = [status_colors.get(s, "#6366f1") for s in labels]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker=dict(color=colors, cornerradius=6),
        text=values,
        textposition="auto",
        hovertemplate="<b>%{x}</b>: %{y} tasks<extra></extra>",
    ))
    fig.update_layout(
        title="Tasks by Status",
        **DARK_LAYOUT,
        height=260,
    )
    return fig


def time_saved_gauge(hours_saved: float, target_hours: float = 5.0) -> go.Figure:
    """Gauge chart for time saved by AI."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=hours_saved,
        title={"text": "Hours Saved by AI Today", "font": {"color": "#94a3b8", "size": 13}},
        number={"suffix": "h", "font": {"color": "#f1f5f9", "size": 36}},
        delta={"reference": target_hours, "suffix": "h target", "font": {"size": 13}},
        gauge={
            "axis": {"range": [0, target_hours * 1.5], "tickcolor": "#64748b"},
            "bar": {"color": "#6366f1"},
            "bgcolor": "#1e293b",
            "borderwidth": 0,
            "steps": [
                {"range": [0, target_hours * 0.5], "color": "rgba(220,38,38,0.12)"},
                {"range": [target_hours * 0.5, target_hours], "color": "rgba(245,158,11,0.12)"},
                {"range": [target_hours, target_hours * 1.5], "color": "rgba(34,197,94,0.12)"},
            ],
            "threshold": {
                "line": {"color": "#22c55e", "width": 2},
                "thickness": 0.75,
                "value": target_hours,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        height=240,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    return fig


def sentiment_chart(sentiments: dict[str, int]) -> go.Figure:
    """Pie chart of email sentiments."""
    colors = {
        "urgent": "#dc2626",
        "concerned": "#f97316",
        "formal": "#3b82f6",
        "professional": "#6366f1",
        "informational": "#64748b",
        "positive": "#22c55e",
        "suspicious": "#8b5cf6",
        "neutral": "#475569",
    }
    labels = list(sentiments.keys())
    values = list(sentiments.values())
    marker_colors = [colors.get(l, "#6366f1") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=marker_colors),
        hole=0.45,
        textinfo="label+percent",
        textfont=dict(size=10, color="#cbd5e1"),
    ))
    fig.update_layout(
        title="Email Sentiment",
        **DARK_LAYOUT,
        height=280,
        showlegend=False,
    )
    return fig


def calendar_timeline(events: list[dict]) -> go.Figure:
    """Gantt-style timeline of calendar events."""
    if not events:
        fig = go.Figure()
        fig.update_layout(title="No Events", **DARK_LAYOUT, height=200)
        return fig

    colors = [CATEGORY_COLORS_LIST[i % len(CATEGORY_COLORS_LIST)] for i in range(len(events))]

    fig = go.Figure()
    for i, ev in enumerate(events):
        fig.add_trace(go.Bar(
            x=[1],
            y=[ev.get("title", f"Event {i}")[:30]],
            orientation="h",
            marker=dict(color=colors[i], cornerradius=4),
            showlegend=False,
            hovertemplate=f"<b>{ev.get('title','')}</b><br>{ev.get('start','')}<extra></extra>",
        ))
    fig.update_layout(
        title="Upcoming Events",
        **DARK_LAYOUT,
        height=max(200, len(events) * 35 + 60),
        barmode="stack",
    )
    return fig


def response_rate_chart(weeks: list[str], rates: list[float]) -> go.Figure:
    """Line chart of response rates over weeks."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weeks,
        y=rates,
        mode="lines+markers",
        line=dict(color="#10b981", width=2.5),
        marker=dict(color="#34d399", size=7),
        fill="tozeroy",
        fillcolor="rgba(16,185,129,0.12)",
        name="Response Rate %",
    ))
    fig.update_layout(
        title="Email Response Rate (%)",
        **{k: v for k, v in DARK_LAYOUT.items() if k != "yaxis"},
        height=240,
        yaxis=dict(range=[0, 100], gridcolor="#1e293b"),
    )
    return fig


def risk_heatmap(risk_data: list[dict]) -> go.Figure:
    """Heatmap of risk levels across categories."""
    categories = list(set(d["category"] for d in risk_data))
    risk_levels = ["Low", "Medium", "High", "Critical"]
    z = [[0] * len(categories) for _ in risk_levels]

    for d in risk_data:
        cat_idx = categories.index(d["category"]) if d["category"] in categories else 0
        rl = d.get("risk_level", "Low")
        rl_idx = risk_levels.index(rl) if rl in risk_levels else 0
        z[rl_idx][cat_idx] += 1

    fig = go.Figure(go.Heatmap(
        z=z,
        x=categories,
        y=risk_levels,
        colorscale=[[0, "#1e293b"], [0.33, "#f59e0b"], [0.66, "#f97316"], [1, "#dc2626"]],
        text=[[str(v) for v in row] for row in z],
        texttemplate="%{text}",
        hovertemplate="Category: %{x}<br>Risk: %{y}<br>Count: %{z}<extra></extra>",
        showscale=False,
    ))
    fig.update_layout(
        title="Risk Level by Email Category",
        **DARK_LAYOUT,
        height=260,
    )
    return fig

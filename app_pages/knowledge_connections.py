"""Knowledge Connections page — graph visualisation of entity relationships."""
from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import random
import math


def _build_mock_graph():
    """Build a realistic mock knowledge graph from session state data."""
    G = nx.Graph()

    # Node types and colours
    node_configs = {
        "email": "#6366f1",
        "task": "#10b981",
        "person": "#f59e0b",
        "topic": "#8b5cf6",
        "company": "#ec4899",
        "calendar": "#06b6d4",
        "document": "#f97316",
    }

    # People
    people = [
        ("Sarah Johnson", "person", "Project Lead"),
        ("Michael Chen", "person", "Project Manager"),
        ("David Walsh", "person", "Acme Corp CTO"),
        ("Alex Rivera", "person", "TechPartner"),
        ("Jennifer Park", "person", "PM"),
        ("Finance Dept", "person", "Finance"),
        ("HR Team", "person", "HR"),
        ("Dev Team", "person", "Engineering"),
    ]

    # Topics
    topics = [
        ("AWS Hackathon", "topic", "Project"),
        ("Production Outage", "topic", "Incident"),
        ("Q3 Budget", "topic", "Finance"),
        ("Project Nexus", "topic", "Project"),
        ("Performance Review", "topic", "HR"),
        ("Payment API", "topic", "Technical"),
        ("Contract Renewal", "topic", "Customer"),
        ("Project Phoenix", "topic", "Project"),
        ("OpenSSL CVE", "topic", "Security"),
    ]

    # Companies
    companies = [
        ("Acme Corp", "company", "$2.4M ARR"),
        ("TechPartner", "company", "Vendor"),
        ("Company", "company", "Internal"),
    ]

    # Events (calendar)
    events = [
        ("Board Meeting Jul 1", "calendar", "Critical"),
        ("Hackathon Review Jul 3", "calendar", "High"),
        ("Nexus Kick-off Jul 1", "calendar", "High"),
    ]

    # Tasks
    task_nodes = [
        ("Resolve Outage", "task", "Critical"),
        ("Approve Budget", "task", "High"),
        ("Acme Response", "task", "Critical"),
        ("Nexus Contract", "task", "High"),
    ]

    all_nodes = people + topics + companies + events + task_nodes
    for label, ntype, detail in all_nodes:
        G.add_node(label, node_type=ntype, detail=detail, color=node_configs.get(ntype, "#6b7280"))

    # Edges with relationships
    edges = [
        ("Sarah Johnson", "AWS Hackathon", "leads"),
        ("Sarah Johnson", "Hackathon Review Jul 3", "organises"),
        ("Michael Chen", "Project Phoenix", "manages"),
        ("David Walsh", "Acme Corp", "works at"),
        ("David Walsh", "Contract Renewal", "raises"),
        ("David Walsh", "Acme Response", "triggers"),
        ("Alex Rivera", "TechPartner", "works at"),
        ("Alex Rivera", "Project Nexus", "delivers"),
        ("Alex Rivera", "Nexus Contract", "involved in"),
        ("Jennifer Park", "Project Nexus", "manages"),
        ("Finance Dept", "Q3 Budget", "owns"),
        ("Finance Dept", "Approve Budget", "requests"),
        ("HR Team", "Performance Review", "owns"),
        ("Dev Team", "Production Outage", "responds to"),
        ("Dev Team", "Payment API", "maintains"),
        ("Dev Team", "Resolve Outage", "assigned"),
        ("Q3 Budget", "Approve Budget", "requires"),
        ("Production Outage", "Resolve Outage", "generates"),
        ("Payment API", "Resolve Outage", "related to"),
        ("Project Nexus", "Nexus Contract", "requires"),
        ("Project Nexus", "Nexus Kick-off Jul 1", "triggers"),
        ("Acme Corp", "Contract Renewal", "at risk"),
        ("AWS Hackathon", "Hackathon Review Jul 3", "reviewed at"),
        ("Board Meeting Jul 1", "Nexus Kick-off Jul 1", "conflicts with"),
        ("OpenSSL CVE", "Dev Team", "affects"),
        ("Q3 Budget", "Company", "allocates for"),
        ("Project Phoenix", "Michael Chen", "led by"),
    ]

    for src, dst, rel in edges:
        if src in G.nodes and dst in G.nodes:
            G.add_edge(src, dst, relationship=rel)

    return G, node_configs


def _graph_to_plotly(G: nx.Graph, node_configs: dict) -> go.Figure:
    """Convert a NetworkX graph to a Plotly figure."""
    pos = nx.spring_layout(G, k=2.5, iterations=50, seed=42)

    # Edge traces
    edge_x, edge_y, edge_text = [], [], []
    for src, dst, data in G.edges(data=True):
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        edge_text.append((mid_x, mid_y, data.get("relationship", "")))

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color="#334155"),
        hoverinfo="none",
        mode="lines",
    )

    # Node trace
    node_x, node_y, node_text, node_hover, node_colors, node_sizes = [], [], [], [], [], []
    for node, data in G.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node[:15])
        node_hover.append(
            f"<b>{node}</b><br>"
            f"Type: {data.get('node_type','')}<br>"
            f"Detail: {data.get('detail','')}<br>"
            f"Connections: {G.degree(node)}"
        )
        node_colors.append(data.get("color", "#6366f1"))
        # Size by degree (importance)
        node_sizes.append(max(15, G.degree(node) * 5 + 10))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        hoverinfo="text",
        hovertext=node_hover,
        text=node_text,
        textposition="top center",
        textfont=dict(size=9, color="#cbd5e1"),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=1.5, color="#1e293b"),
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text="Enterprise Knowledge Graph",
                font=dict(color="#94a3b8", size=14),
            ),
            showlegend=False,
            hovermode="closest",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(14,22,39,0.8)",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=10, r=10, t=40, b=10),
            height=550,
        ),
    )
    return fig


def render():
    st.html("## 🔗 Knowledge Connections")
    st.markdown("*Visualise relationships across emails, tasks, people, and topics*")

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])
    with ctrl_col1:
        node_type_filter = st.multiselect(
            "Show Node Types",
            ["email", "task", "person", "topic", "company", "calendar", "document"],
            default=["person", "task", "topic", "company", "calendar"],
            key="graph_node_types",
        )
    with ctrl_col2:
        search_node = st.text_input("🔍 Search node", placeholder="Name, topic, company...", key="graph_search")
    with ctrl_col3:
        st.markdown("<br>")
        refresh = st.button("🔄 Refresh", use_container_width=True)

    # ── Build Graph ───────────────────────────────────────────────────────────
    G, node_configs = _build_mock_graph()

    # Filter by node type
    if node_type_filter:
        nodes_to_remove = [
            n for n, d in G.nodes(data=True)
            if d.get("node_type") not in node_type_filter
        ]
        G.remove_nodes_from(nodes_to_remove)

    # Filter by search
    if search_node:
        q = search_node.lower()
        matching = [n for n in G.nodes if q in n.lower()]
        if matching:
            # Show only nodes within 2 hops of matches
            keep = set()
            for m in matching:
                keep.add(m)
                keep.update(G.neighbors(m))
            nodes_to_remove = [n for n in G.nodes if n not in keep]
            G.remove_nodes_from(nodes_to_remove)
        else:
            st.warning(f"No nodes found matching '{search_node}'")

    # ── Stats ─────────────────────────────────────────────────────────────────
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.metric("Nodes", G.number_of_nodes())
    with stat_cols[1]:
        st.metric("Connections", G.number_of_edges())
    with stat_cols[2]:
        if G.number_of_nodes() > 0:
            most_connected = max(G.nodes, key=lambda n: G.degree(n))
            st.metric("Most Connected", most_connected[:20])
        else:
            st.metric("Most Connected", "—")
    with stat_cols[3]:
        components = nx.number_connected_components(G) if G.number_of_nodes() > 0 else 0
        st.metric("Clusters", components)

    # ── Graph ─────────────────────────────────────────────────────────────────
    if G.number_of_nodes() == 0:
        st.info("No nodes to display. Try adjusting filters.")
    else:
        fig = _graph_to_plotly(G, node_configs)
        st.plotly_chart(fig, use_container_width=True)

    # ── Legend ────────────────────────────────────────────────────────────────
    st.html("#### Legend")
    legend_cols = st.columns(len(node_configs))
    type_labels = {
        "email": "Email", "task": "Task", "person": "Person",
        "topic": "Topic", "company": "Company", "calendar": "Calendar", "document": "Document"
    }
    for col, (ntype, color) in zip(legend_cols, node_configs.items()):
        with col:
            st.markdown(
                f'<div style="display:flex; align-items:center; gap:6px;">'
                f'<div style="width:14px; height:14px; border-radius:50%; background:{color};"></div>'
                f'<span style="font-size:0.75rem; color:#94a3b8;">{type_labels.get(ntype, ntype)}</span>'
                f'</div>')

    # ── Connection Explorer ───────────────────────────────────────────────────
    st.html("---")
    st.markdown("### 🔍 Connection Explorer")
    selected_node = st.selectbox(
        "Select a node to explore its connections",
        [""] + sorted(G.nodes()),
        key="explore_node",
    )

    if selected_node and selected_node in G.nodes:
        node_data = G.nodes[selected_node]
        neighbors = list(G.neighbors(selected_node))

        col1, col2 = st.columns([1, 2])
        with col1:
            color = node_data.get("color", "#6366f1")
            st.markdown(
                f"""
                <div style="background:#1e293b; border:1px solid #334155;
                            border-left:4px solid {color}; border-radius:8px; padding:14px;">
                    <div style="font-size:1rem; font-weight:600; color:#f1f5f9; margin-bottom:8px;">
                        {selected_node}
                    </div>
                    <div style="font-size:0.78rem; color:#94a3b8;">
                        <div>Type: <strong>{node_data.get('node_type','').title()}</strong></div>
                        <div>Detail: {node_data.get('detail','—')}</div>
                        <div>Connections: <strong>{G.degree(selected_node)}</strong></div>
                    </div>
                </div>
                """)

        with col2:
            st.html(f"**Connected to {len(neighbors)} entities:**")
            for neighbor in neighbors:
                edge_data = G.get_edge_data(selected_node, neighbor, {})
                rel = edge_data.get("relationship", "connected to")
                n_color = G.nodes[neighbor].get("color", "#6366f1")
                n_type = G.nodes[neighbor].get("node_type", "")
                st.markdown(
                    f'<div style="background:#0f172a; border:1px solid #1e293b; border-left:3px solid {n_color}; '
                    f'border-radius:4px; padding:5px 10px; margin-bottom:4px; font-size:0.78rem;">'
                    f'<strong style="color:{n_color};">{neighbor}</strong> '
                    f'<span style="color:#64748b;">— {rel} — ({n_type})</span>'
                    f'</div>')

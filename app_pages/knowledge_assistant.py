"""Knowledge Assistant page — chat interface with AI."""
from __future__ import annotations

import streamlit as st

from components.source_card import render_source_card


SAMPLE_QUESTIONS = [
    "What are the most urgent items requiring my attention today?",
    "Show me all upcoming meetings this week",
    "What budget decisions are pending?",
    "Which emails require a response?",
    "What are my overdue tasks?",
    "Summarise the Acme Corp situation",
    "What technical incidents are active?",
    "Show me all deadlines this week",
]

MOCK_CONTEXT = [
    {
        "source_type": "email",
        "source_title": "Email Intelligence",
        "content": "15 emails analysed. 2 critical, 5 high priority. Production outage and payment API issues active.",
        "relevance_score": 0.95,
    },
    {
        "source_type": "task",
        "source_title": "Task Manager",
        "content": "12 active tasks. 2 critical, 5 high priority. Multiple deadlines on June 30.",
        "relevance_score": 0.88,
    },
    {
        "source_type": "calendar",
        "source_title": "Calendar Events",
        "content": "12 calendar events. 1 conflict detected on July 1 (Board Meeting vs All-Hands).",
        "relevance_score": 0.82,
    },
]


def render():
    st.html("## 💬 Knowledge Assistant")
    st.markdown("*Ask anything about your emails, documents, tasks, and calendar*")

    bedrock = st.session_state.get("bedrock_service")

    # ── Initialise chat history ───────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        # Welcome message
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": "👋 Hello! I'm your Enterprise Intelligence Assistant powered by Claude AI.\n\nI can help you with:\n- 📧 Email analysis and summaries\n- ✅ Task priorities and deadlines\n- 📅 Meeting scheduling and conflicts\n- 📄 Document insights\n- 📊 Analytics and reports\n\nWhat would you like to know?",
            "sources": [],
        })

    # ── Layout ────────────────────────────────────────────────────────────────
    left_col, right_col = st.columns([3, 1])

    with right_col:
        st.markdown("### 💡 Sample Questions")
        for q in SAMPLE_QUESTIONS:
            if st.button(q[:45] + ("..." if len(q) > 45 else ""), key=f"sample_{hash(q)}", use_container_width=True):
                st.session_state["pending_question"] = q
                st.rerun()

        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()

        st.markdown("### 📊 Knowledge Sources")
        st.markdown(
            """
            <div style="font-size:0.78rem; color:#94a3b8;">
            Connected sources:<br/>
            ✅ Email Intelligence (15 emails)<br/>
            ✅ Task Manager (12 tasks)<br/>
            ✅ Calendar Events (12 events)<br/>
            🟡 Documents (upload to enable)<br/>
            🟡 AWS Knowledge Base (connect to enable)
            </div>
            """)

    with left_col:
        # ── Chat messages ─────────────────────────────────────────────────────
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state["chat_history"]:
                _render_message(msg)

        # ── Input ─────────────────────────────────────────────────────────────
        st.html("<br>")

        pending = st.session_state.pop("pending_question", None)

        with st.form("chat_form", clear_on_submit=True):
            form_cols = st.columns([8, 1])
            with form_cols[0]:
                user_input = st.text_input(
                    "Message",
                    value=pending or "",
                    placeholder="Ask anything about your enterprise data...",
                    label_visibility="collapsed",
                )
            with form_cols[1]:
                submitted = st.form_submit_button("➤", use_container_width=True, type="primary")

        if submitted and user_input.strip():
            # Add user message
            st.session_state["chat_history"].append({
                "role": "user",
                "content": user_input,
                "sources": [],
            })

            # Get AI response
            with st.spinner("🤖 Thinking..."):
                result = bedrock.answer_question(
                    user_input,
                    MOCK_CONTEXT,
                    conversation_history=st.session_state["chat_history"][-6:],
                )

            # Add assistant message
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": result.get("answer", "I couldn't generate a response."),
                "sources": result.get("sources", []),
                "confidence": result.get("confidence", 0.85),
            })

            # Log to audit
            audit = st.session_state.get("audit_service")
            if audit:
                audit.log("answer_question", "knowledge", details={"question": user_input[:100]})

            st.rerun()


def _render_message(msg: dict):
    """Render a single chat message."""
    role = msg["role"]
    content = msg["content"]
    sources = msg.get("sources", [])
    confidence = msg.get("confidence")

    if role == "user":
        st.html(f"""
            <div style="display:flex; justify-content:flex-end; margin-bottom:12px;">
                <div style="background:#6366f1; color:white; border-radius:12px 12px 2px 12px;
                            padding:10px 16px; max-width:80%; font-size:0.87rem; line-height:1.6;">
                    {content}
                </div>
            </div>
            """)
    else:
        st.html(f"""
            <div style="display:flex; justify-content:flex-start; margin-bottom:4px;">
                <div style="background:#1e293b; border:1px solid #334155; color:#e2e8f0;
                            border-radius:2px 12px 12px 12px; padding:12px 16px; max-width:85%;
                            font-size:0.87rem; line-height:1.7;">
                    <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px;">
                        <span style="font-size:0.8rem;">🧠</span>
                        <span style="font-size:0.72rem; color:#818cf8; font-weight:600;">Claude AI Assistant</span>
                        {f'<span style="font-size:0.65rem; color:#64748b;">Confidence: {int(confidence*100)}%</span>' if confidence else ''}
                    </div>
                    {content.replace(chr(10), '<br>')}
                </div>
            </div>
            """)

        # Render source citations
        if sources:
            st.html('<div style="font-size:0.7rem; color:#64748b; margin-left:8px; margin-bottom:2px;">Sources:</div>')
            for i, source in enumerate(sources[:3]):
                render_source_card(source, index=i)

        st.html("<br>")

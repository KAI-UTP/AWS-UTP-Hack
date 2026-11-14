"""Document Intelligence page — upload, extract, and analyse documents."""
from __future__ import annotations

import uuid
import streamlit as st

from models.document_models import DocumentData
from utils.file_validation import validate_uploaded_file


ALLOWED_TYPES = ["pdf", "docx", "xlsx", "csv", "txt", "pptx", "png", "jpg", "jpeg"]


def render():
    st.html("## 📄 Document Intelligence")
    st.markdown("*Upload and AI-analyse your enterprise documents*")

    doc_service = st.session_state.get("document_service")
    bedrock = st.session_state.get("bedrock_service")

    if not doc_service:
        st.error("Document service not initialised.")
        return

    # ── Upload Section ────────────────────────────────────────────────────────
    with st.expander("📤 Upload New Documents", expanded=True):
        uploaded_files = st.file_uploader(
            "Drop files here or click to browse",
            type=ALLOWED_TYPES,
            accept_multiple_files=True,
            help=f"Supported: {', '.join(ALLOWED_TYPES).upper()} · Max 10 MB per file",
        )

        if uploaded_files:
            col1, col2 = st.columns([3, 1])
            with col2:
                process_btn = st.button("🤖 Process & Analyse", type="primary", use_container_width=True)

            if process_btn:
                if "documents" not in st.session_state:
                    st.session_state["documents"] = []

                progress = st.progress(0)
                for i, f in enumerate(uploaded_files):
                    content = f.read()
                    is_valid, error = validate_uploaded_file(f.name, content)
                    if not is_valid:
                        st.error(f"❌ {f.name}: {error}")
                        continue

                    with st.spinner(f"Processing {f.name}..."):
                        doc = doc_service.process_upload(f.name, content)
                        # AI Analysis
                        analysis = bedrock.analyze_document(doc.content, doc.filename)
                        doc.analysis = analysis

                        # Avoid duplicates
                        existing_ids = [d.id for d in st.session_state["documents"]]
                        if doc.id not in existing_ids:
                            st.session_state["documents"].append(doc)

                    progress.progress((i + 1) / len(uploaded_files))

                st.success(f"✅ Processed {len(uploaded_files)} document(s)!")

    st.markdown("---")

    # ── Document List & Analysis ──────────────────────────────────────────────
    documents: list[DocumentData] = st.session_state.get("documents", [])

    if not documents:
        st.markdown(
            """
            <div style="text-align:center; padding:60px 20px; color:#64748b;">
                <div style="font-size:3rem; margin-bottom:16px;">📄</div>
                <div style="font-size:1.1rem; font-weight:600; margin-bottom:8px;">No documents yet</div>
                <div style="font-size:0.85rem;">Upload PDF, Word, Excel, CSV, PowerPoint, or image files above to get started</div>
            </div>
            """)
        return

    st.html(f"### 📁 Documents ({len(documents)})")

    for doc in documents:
        _render_document_card(doc, bedrock)


def _render_document_card(doc: DocumentData, bedrock):
    """Render a single document card with analysis."""
    ext_icons = {
        "pdf": "📕", "docx": "📘", "xlsx": "📗", "csv": "📊",
        "txt": "📝", "pptx": "📙", "png": "🖼️", "jpg": "🖼️", "jpeg": "🖼️",
    }
    icon = ext_icons.get(doc.file_type, "📄")

    with st.expander(f"{icon} {doc.filename} — {doc.size_mb} MB", expanded=False):
        col1, col2 = st.columns([2, 1])

        with col1:
            # File info
            st.markdown(
                f"**Type:** `{doc.file_type.upper()}` &nbsp;·&nbsp; "
                f"**Size:** {doc.size_mb} MB &nbsp;·&nbsp; "
                f"**Pages:** {doc.page_count or 'N/A'} &nbsp;·&nbsp; "
                f"**Uploaded:** {doc.uploaded_at[:10] if doc.uploaded_at else 'Unknown'}"
            )

        with col2:
            re_analyse = st.button("🔄 Re-analyse", key=f"reanalyse_{doc.id}", use_container_width=True)
            if re_analyse:
                with st.spinner("Running AI analysis..."):
                    import time; time.sleep(0.8)
                    doc.analysis = bedrock.analyze_document(doc.content, doc.filename)
                st.success("Re-analysis complete!")

        if doc.analysis:
            analysis = doc.analysis
            a_tab1, a_tab2, a_tab3, a_tab4 = st.tabs(["📋 Summary", "✅ Actions", "🔍 Details", "💬 Q&A"])

            with a_tab1:
                st.markdown(f"**AI Summary:** {analysis.summary}")
                if analysis.key_topics:
                    st.markdown("**Key Topics:** " + " · ".join(f"`{t}`" for t in analysis.key_topics))
                if analysis.financial_figures:
                    st.markdown("**Financial Figures:** " + ", ".join(analysis.financial_figures))
                if analysis.key_dates:
                    st.markdown("**Key Dates:** " + ", ".join(analysis.key_dates))

                conf_pct = int(analysis.confidence_score * 100)
                st.markdown(
                    f'<div style="margin-top:8px; font-size:0.8rem; color:#94a3b8;">AI Confidence: '
                    f'<span style="color:#22c55e; font-weight:600;">{conf_pct}%</span> · '
                    f'Reading Time: ~{analysis.reading_time_minutes} min · '
                    f'Word Count: {analysis.word_count:,}</div>')

            with a_tab2:
                if analysis.action_items:
                    for item in analysis.action_items:
                        st.markdown(f"- {item}")
                else:
                    st.info("No action items detected.")

                if analysis.recommendations:
                    st.markdown("**Recommendations:**")
                    for rec in analysis.recommendations:
                        st.markdown(f"💡 {rec}")

            with a_tab3:
                if analysis.entities:
                    st.markdown("**Entities:** " + ", ".join(analysis.entities))
                if analysis.risk_flags:
                    st.warning("**Risk Flags:**")
                    for flag in analysis.risk_flags:
                        st.markdown(f"⚠️ {flag}")
                else:
                    st.success("No risk flags detected.")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Document Type:** {analysis.document_type}")
                    st.markdown(f"**Sentiment:** {analysis.sentiment.title()}")
                with col_b:
                    st.markdown(f"**Language:** {analysis.language}")

                # Content preview
                st.markdown("**Content Preview:**")
                preview = doc.content[:1000] + "..." if len(doc.content) > 1000 else doc.content
                st.text_area("Content preview", preview, height=200, disabled=True, key=f"preview_{doc.id}", label_visibility="collapsed")

            with a_tab4:
                _render_document_qa(doc, bedrock)
        else:
            st.info("Document uploaded. Click **Re-analyse** to run AI analysis.")


def _render_document_qa(doc: DocumentData, bedrock):
    """Render Q&A interface for a specific document."""
    st.markdown("**Ask questions about this document:**")

    sample_questions = [
        "What are the main findings?",
        "What action items are mentioned?",
        "What are the key financial figures?",
        "What risks are identified?",
        "Summarise the recommendations",
    ]

    selected_q = st.selectbox("Sample questions", [""] + sample_questions, key=f"sample_q_{doc.id}")
    question = st.text_input("Your question", value=selected_q, key=f"doc_q_{doc.id}")

    if st.button("💬 Ask AI", key=f"ask_{doc.id}", type="primary") and question:
        with st.spinner("Thinking..."):
            context = [{"source_title": doc.filename, "content": doc.content[:3000]}]
            result = bedrock.answer_question(question, context)

        st.markdown(f"**Answer:** {result.get('answer','')}")

        # Save to history
        if not hasattr(doc, "qa_history"):
            doc.qa_history = []
        doc.qa_history.append({"question": question, "answer": result.get("answer", "")})

    # Show history
    if doc.qa_history:
        st.markdown("**Previous Questions:**")
        for qa in doc.qa_history[-3:]:
            with st.expander(f"Q: {qa['question'][:60]}..."):
                st.markdown(f"**A:** {qa['answer']}")

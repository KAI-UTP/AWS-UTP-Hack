"""
Enterprise Intelligence Hub — Main Streamlit Entry Point
AWS Hackathon 2026 | Phase 1: Mock Mode Demo
"""
import streamlit as st

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Enterprise Intelligence Hub",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
import sys
import os

# Ensure project root is on path regardless of how the app is launched
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from utils.config import get_config
from utils.logging_config import setup_logging
from components.navigation import render_navigation


# ── Logging ───────────────────────────────────────────────────────────────────
logger = setup_logging()


# ── Custom CSS ────────────────────────────────────────────────────────────────
def _inject_css():
    st.markdown(
        """
        <style>
        /* ── Global ── */
        html, body, [data-testid="stApp"] {
            background-color: #0f172a !important;
            color: #e2e8f0;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: transparent;
            border: 1px solid #1e293b;
            color: #cbd5e1;
            border-radius: 6px;
            text-align: left;
            font-size: 0.82rem;
            padding: 6px 10px;
            margin-bottom: 2px;
            transition: all 0.15s ease;
            width: 100%;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: #1e293b;
            border-color: #6366f1;
            color: #f1f5f9;
        }
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            border-color: #6366f1;
            color: white;
        }

        /* ── Hide default Streamlit page nav ── */
        [data-testid="stSidebarNav"] { display: none !important; }
        section[data-testid="stSidebarNav"] { display: none !important; }
        .stAppViewBlockContainer > div:first-child > div > ul { display: none !important; }

        /* ── Main content ── */
        .main .block-container {
            padding: 1.5rem 2rem 2rem 2rem;
            max-width: 100%;
        }

        /* ── Headings ── */
        h1, h2, h3, h4, h5 {
            color: #f1f5f9 !important;
        }

        /* ── Metric cards ── */
        [data-testid="stMetric"] {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px 16px;
        }
        [data-testid="stMetricValue"] { color: #f1f5f9 !important; }
        [data-testid="stMetricLabel"] { color: #94a3b8 !important; }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent;
            border-bottom: 1px solid #1e293b;
        }
        .stTabs [data-baseweb="tab"] {
            color: #94a3b8;
            font-size: 0.82rem;
        }
        .stTabs [aria-selected="true"] {
            color: #6366f1 !important;
            border-bottom-color: #6366f1 !important;
        }

        /* ── Inputs ── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            color: #e2e8f0 !important;
            border-radius: 6px !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
        }

        /* ── Buttons ── */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            border: none;
            color: white;
            border-radius: 6px;
            font-weight: 600;
        }
        .stButton > button[kind="secondary"] {
            background: #1e293b;
            border: 1px solid #334155;
            color: #cbd5e1;
            border-radius: 6px;
        }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
            color: #cbd5e1 !important;
        }

        /* ── Dataframe ── */
        [data-testid="stDataFrame"] {
            border: 1px solid #334155;
            border-radius: 6px;
        }

        /* ── Progress bar ── */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #6366f1, #818cf8);
            border-radius: 4px;
        }

        /* ── Alerts ── */
        .stAlert {
            border-radius: 8px !important;
            border-left-width: 4px !important;
        }

        /* ── Form ── */
        [data-testid="stForm"] {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 16px;
        }

        /* ── Divider ── */
        hr { border-color: #1e293b !important; }

        /* ── Chat containers ── */
        .chat-container { max-height: 500px; overflow-y: auto; }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Session State Initialisation ─────────────────────────────────────────────
def _init_session_state():
    """Initialise all session state on first load."""
    if st.session_state.get("_initialised"):
        return

    logger.info("Initialising session state...")

    # Load config
    config = get_config()
    st.session_state["app_config"] = config
    st.session_state["config_mock_mode"] = config.MOCK_MODE

    # Initialise services
    from services.bedrock_service import BedrockService
    from services.gmail_service import GmailService
    from services.calendar_service import CalendarService
    from services.document_service import DocumentService
    from services.notification_service import NotificationService
    from services.audit_service import AuditService

    bedrock = BedrockService(config=config)
    gmail = GmailService(config=config)
    calendar = CalendarService(config=config)
    doc_service = DocumentService(config=config)
    notif_service = NotificationService()
    audit_service = AuditService(config=config)

    st.session_state["bedrock_service"] = bedrock
    st.session_state["gmail_service"] = gmail
    st.session_state["calendar_service"] = calendar
    st.session_state["document_service"] = doc_service
    st.session_state["notification_service"] = notif_service
    st.session_state["audit_service"] = audit_service

    # Pre-load email stats for sidebar
    try:
        stats = gmail.get_stats()
        st.session_state["email_stats"] = stats
    except Exception as e:
        logger.warning(f"Could not pre-load email stats: {e}")
        st.session_state["email_stats"] = {}

    # Pre-load tasks from sample data
    from utils.json_utils import load_json_file
    tasks_raw = load_json_file(config.SAMPLE_TASKS_PATH, [])
    st.session_state["tasks"] = tasks_raw

    # Task stats for sidebar
    task_stats: dict[str, int] = {}
    overdue = 0
    from utils.date_utils import is_overdue as _is_overdue
    for t in tasks_raw:
        status = t.get("status", "Not Started")
        key = status.lower().replace(" ", "_")
        task_stats[key] = task_stats.get(key, 0) + 1
        due = t.get("due_date")
        if due and t.get("status") not in ("Completed", "Cancelled"):
            if _is_overdue(due):
                overdue += 1
    task_stats["overdue"] = overdue
    st.session_state["task_stats"] = task_stats

    # Default navigation
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "home"

    # Documents list
    if "documents" not in st.session_state:
        st.session_state["documents"] = []

    # Seed demo notifications
    notif_service.seed_demo_notifications()

    # Seed demo audit records
    audit_service.seed_demo_records()

    # Log app start
    audit_service.log("app_start", "system", details={"mock_mode": config.MOCK_MODE})

    st.session_state["_initialised"] = True
    logger.info("Session state initialised successfully")


# ── Page Router ───────────────────────────────────────────────────────────────
def _route_to_page(page_key: str):
    """Import and render the requested page module."""
    page_map = {
        "home": "app_pages.home",
        "daily_brief": "app_pages.daily_brief",
        "email_intelligence": "app_pages.email_intelligence",
        "document_intelligence": "app_pages.document_intelligence",
        "knowledge_assistant": "app_pages.knowledge_assistant",
        "tasks": "app_pages.tasks",
        "calendar": "app_pages.calendar_page",
        "knowledge_connections": "app_pages.knowledge_connections",
        "analytics": "app_pages.analytics",
        "data_sources": "app_pages.data_sources",
        "notifications": "app_pages.notifications",
        "audit_history": "app_pages.audit_history",
        "settings": "app_pages.settings",
        "system_status": "app_pages.system_status",
    }

    module_path = page_map.get(page_key, "app_pages.home")
    try:
        import importlib
        module = importlib.import_module(module_path)
        module.render()
    except ImportError as e:
        st.error(f"Page not found: {page_key} ({e})")
    except Exception as e:
        st.error(f"Page error on '{page_key}': {e}")
        import traceback
        with st.expander("Error details"):
            st.code(traceback.format_exc())


# ── Demo Mode Banner ──────────────────────────────────────────────────────────
def _show_demo_banner():
    mock_mode = st.session_state.get("config_mock_mode", True)
    if mock_mode:
        st.html(
            """
            <div style="
                background: rgba(245,158,11,0.08);
                border: 1px solid rgba(245,158,11,0.3);
                border-radius: 8px;
                padding: 8px 16px;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 0.82rem;
            ">
                <span style="font-size:1rem;">&#128993;</span>
                <span style="color:#fde68a; font-weight:600;">Demo Mode &mdash; Using Sample Data</span>
                <span style="color:#94a3b8; margin-left:8px;">
                    No real APIs connected. Set MOCK_MODE=false in .env to use live services.
                </span>
                <span style="margin-left:auto; color:#f59e0b; font-size:0.75rem;">
                    AWS Hackathon 2026 &middot; Phase 1
                </span>
            </div>
            """
        )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    _inject_css()
    _init_session_state()

    # Render sidebar navigation
    render_navigation()

    # Demo mode banner
    _show_demo_banner()

    # Route to current page
    current_page = st.session_state.get("current_page", "home")
    _route_to_page(current_page)


if __name__ == "__main__":
    main()
else:
    # Called directly by streamlit run app.py
    main()

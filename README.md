# 🧠 Enterprise Intelligence Hub

> AI-powered enterprise intelligence platform using **AWS Bedrock** and **Claude AI** — AWS Hackathon 2026

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)](https://streamlit.io/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange)](https://aws.amazon.com/bedrock/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## Overview

Enterprise Intelligence Hub transforms how enterprises process information by using AI to:

- 📧 **Analyse emails** — Auto-categorise, prioritise, extract tasks and meetings
- 📄 **Process documents** — Summarise PDFs, Word docs, spreadsheets with AI
- 💬 **Answer questions** — Natural language Q&A across all enterprise data
- 📋 **Generate daily briefs** — Executive AI briefings with urgent items, deadlines, risks
- ✅ **Manage tasks** — AI-extracted action items with Kanban, table, and timeline views
- 📅 **Intelligent calendar** — Detect meeting invitations from emails, resolve conflicts
- 🔗 **Knowledge graph** — Visualise connections across people, projects, topics
- 📊 **Analytics** — Time saved, ROI calculator, AI performance metrics

## Quick Start (Demo Mode)

```bash
# 1. Clone and navigate
cd enterprise-intelligence-hub

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Open http://localhost:8501 — the app runs in **Demo Mode** with 15 sample emails, 12 tasks, and 12 calendar events.

## Project Structure

```
enterprise-intelligence-hub/
├── app.py                    # Main entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
│
├── data/                     # Mock data (Phase 1)
│   ├── sample_emails.json    # 15 realistic enterprise emails
│   ├── sample_tasks.json     # 12 extracted tasks
│   └── sample_calendar.json  # 12 calendar events
│
├── utils/                    # Utilities
│   ├── config.py             # App configuration
│   ├── logging_config.py     # Structured logging
│   ├── date_utils.py         # Date helpers
│   ├── text_utils.py         # Text processing
│   ├── json_utils.py         # JSON parsing/repair
│   ├── security.py           # Security functions
│   └── file_validation.py    # File type validation
│
├── models/                   # Pydantic data models
│   ├── email_models.py
│   ├── document_models.py
│   ├── task_models.py
│   ├── calendar_models.py
│   ├── user_models.py
│   ├── audit_models.py
│   └── knowledge_models.py
│
├── services/                 # Business logic
│   ├── bedrock_service.py    # AWS Bedrock / Claude AI
│   ├── gmail_service.py      # Gmail API
│   ├── calendar_service.py   # Google Calendar API
│   ├── document_service.py   # Document processing
│   ├── notification_service.py
│   └── audit_service.py
│
├── components/               # Reusable UI components
│   ├── navigation.py
│   ├── metric_card.py
│   ├── email_card.py
│   ├── task_card.py
│   ├── calendar_card.py
│   ├── source_card.py
│   └── charts.py
│
├── pages/                    # Streamlit pages
│   ├── home.py               # Dashboard
│   ├── daily_brief.py        # AI daily briefing
│   ├── email_intelligence.py # Email analysis
│   ├── document_intelligence.py
│   ├── knowledge_assistant.py # Chat interface
│   ├── tasks.py              # Task management
│   ├── calendar_page.py      # Calendar view
│   ├── knowledge_connections.py # Knowledge graph
│   ├── analytics.py          # Analytics dashboard
│   ├── data_sources.py       # Service connections
│   ├── notifications.py
│   ├── audit_history.py
│   ├── settings.py
│   └── system_status.py
│
├── prompts/                  # AI prompt templates
│   ├── email_analysis.txt
│   ├── document_analysis.txt
│   ├── daily_brief.txt
│   ├── question_answering.txt
│   ├── task_extraction.txt
│   └── meeting_extraction.txt
│
└── tests/                    # Test suite
    ├── test_mock_mode.py
    ├── test_email_analysis.py
    ├── test_task_extraction.py
    └── test_security.py
```

## Connecting Real Services (Phase 2)

### Gmail
1. Create OAuth credentials in [Google Cloud Console](https://console.cloud.google.com/)
2. Download `credentials.json` to project root
3. Set `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` in `.env`

### AWS Bedrock
1. Ensure AWS account has Bedrock model access for Claude claude-sonnet-4-6
2. Set AWS credentials in `.env`
3. Set `MOCK_MODE=false`

### Full Configuration
Copy `.env.example` to `.env` and fill in your values.

## Running Tests

```bash
pytest tests/ -v
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.32+ |
| AI/LLM | AWS Bedrock (Claude claude-sonnet-4-6) |
| Email | Gmail API (Google OAuth) |
| Calendar | Google Calendar API |
| Data Models | Pydantic v2 |
| Visualisation | Plotly |
| Knowledge Graph | NetworkX + Plotly |
| Document Processing | pypdf, python-docx, pandas, openpyxl, python-pptx |
| Security | Custom validation + PII detection |

## AWS Architecture (Phase 2)

```
User Browser
    │
    ▼
Streamlit App (EC2/ECS)
    ├── AWS Bedrock (Claude AI) ──── Email/Doc Analysis
    ├── Amazon S3 ─────────────────── Document Storage
    ├── Amazon Bedrock KB ──────────── Vector Search
    ├── Gmail API ──────────────────── Email Sync
    └── Google Calendar API ─────────── Calendar Sync
```

## License

MIT License — see [LICENSE](LICENSE)

---

Built with ❤️ for AWS Hackathon 2026

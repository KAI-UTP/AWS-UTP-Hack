# Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Enterprise Intelligence Hub                      │
│                       Streamlit Application                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐ │
│  │   Pages      │   │  Components  │   │       Services            │ │
│  │              │   │              │   │                            │ │
│  │ • Dashboard  │   │ • EmailCard  │   │ ┌──────────────────────┐  │ │
│  │ • DailyBrief │   │ • TaskCard   │   │ │   BedrockService     │  │ │
│  │ • Email Intel│   │ • CalCard    │   │ │   (Mock | Live)      │  │ │
│  │ • Doc Intel  │◄──│ • MetricCard │   │ └──────────┬───────────┘  │ │
│  │ • Knowledge  │   │ • Charts     │   │            │               │ │
│  │ • Tasks      │   │ • Navigation │   │ ┌──────────▼───────────┐  │ │
│  │ • Calendar   │   │ • SourceCard │   │ │   GmailService       │  │ │
│  │ • KnowledgeG │   └──────────────┘   │ │   (Mock | OAuth)     │  │ │
│  │ • Analytics  │                       │ └──────────────────────┘  │ │
│  │ • Settings   │   ┌──────────────┐   │                            │ │
│  │ • Audit      │   │    Models    │   │ ┌──────────────────────┐  │ │
│  └──────────────┘   │              │   │ │  CalendarService     │  │ │
│                      │ • EmailData  │   │ │  (Mock | Google API) │  │ │
│                      │ • Task       │   │ └──────────────────────┘  │ │
│                      │ • CalEvent   │   │                            │ │
│                      │ • Document   │   │ ┌──────────────────────┐  │ │
│                      │ • AuditRec   │   │ │  DocumentService     │  │ │
│                      │ • KnowChunk  │   │ │  (pypdf, docx, xl)  │  │ │
│                      └──────────────┘   │ └──────────────────────┘  │ │
│                                          └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                     │
          ▼                    ▼                     ▼
  ┌───────────────┐   ┌───────────────┐   ┌────────────────┐
  │  AWS Bedrock  │   │   Gmail API   │   │ Google Calendar│
  │  Claude AI    │   │  (OAuth 2.0)  │   │    API         │
  │               │   │               │   │                │
  │  • Analysis   │   │  • Emails     │   │  • Events      │
  │  • Q&A        │   │  • Labels     │   │  • RSVP        │
  │  • Brief Gen  │   │  • Threads    │   │  • Conflicts   │
  └───────────────┘   └───────────────┘   └────────────────┘
          │
  ┌───────────────┐   ┌───────────────┐
  │  Amazon S3    │   │ Bedrock KB    │
  │               │   │               │
  │  • Documents  │   │  • Vector DB  │
  │  • Exports    │   │  • RAG Search │
  │  • Audit logs │   │  • Embeddings │
  └───────────────┘   └───────────────┘
```

## Data Flow

### Email Analysis Flow
```
Gmail API → GmailService → EmailData model → BedrockService.analyze_email()
    → EmailAnalysis model → UI (EmailCard component)
    → AuditService.log() → NotificationService (if critical)
    → TaskExtraction → Task[] → Task Manager
    → MeetingDetection → CalendarEvent[] → Calendar
```

### Document Analysis Flow
```
File Upload → FileValidation → DocumentService.process_upload()
    → Text Extraction (pypdf/docx/xlsx/pptx)
    → DocumentData model → BedrockService.analyze_document()
    → DocumentAnalysis model → UI display
    → Q&A queries → BedrockService.answer_question()
```

### Daily Brief Flow
```
User triggers brief → Aggregate data (emails + tasks + calendar)
    → BedrockService.generate_daily_brief()
    → Structured brief dict → DailyBrief page render
    → Optional export (MD/TXT)
```

## Session State Architecture

All application state lives in `st.session_state`:

| Key | Type | Description |
|-----|------|-------------|
| `_initialised` | bool | One-time init guard |
| `app_config` | AppConfig | Configuration object |
| `config_mock_mode` | bool | Current mode |
| `bedrock_service` | BedrockService | AI service singleton |
| `gmail_service` | GmailService | Email service singleton |
| `calendar_service` | CalendarService | Calendar service singleton |
| `document_service` | DocumentService | Doc processing singleton |
| `notification_service` | NotificationService | Notification manager |
| `audit_service` | AuditService | Audit log manager |
| `tasks` | list[dict] | Task list (mutable) |
| `documents` | list[DocumentData] | Uploaded documents |
| `notifications` | list[dict] | In-app notifications |
| `audit_records` | list[dict] | Audit log entries |
| `chat_history` | list[dict] | Chat conversation |
| `current_page` | str | Active page key |
| `email_stats` | dict | Cached email stats |
| `task_stats` | dict | Cached task stats |

## Mock Mode vs Live Mode

| Feature | Mock Mode | Live Mode |
|---------|-----------|-----------|
| Email source | `data/sample_emails.json` | Gmail API |
| AI analysis | Pre-computed in JSON | AWS Bedrock API |
| Calendar | `data/sample_calendar.json` | Google Calendar API |
| Documents | Text extraction only | Full AI analysis |
| AWS credentials | Not required | Required |
| Google OAuth | Not required | Required |

## Security Architecture

```
User Input → sanitize_input() → Application Logic
File Upload → validate_uploaded_file() → magic_byte_check() → Process
API Keys → .env file → AppConfig (never in session state)
Audit → Every action logged → AuditRecord → session/S3
PII → detect_pii() / mask_pii() → Safe processing
Rate Limiting → check_rate_limit() → API call protection
```

## Phase 2 Deployment (AWS)

```
Route 53 → CloudFront → ALB → ECS Fargate (Streamlit)
                                     │
                          ┌──────────┼──────────┐
                          ▼          ▼          ▼
                      Bedrock       S3        RDS/DynamoDB
                    (Claude AI)  (Storage)   (Persistence)
```

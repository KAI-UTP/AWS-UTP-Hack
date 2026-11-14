# Tasks

## Phase 1 — Mock Mode Demo (Current)

### Infrastructure
- [x] Project structure created
- [x] requirements.txt with all dependencies
- [x] pyproject.toml with build config
- [x] .env.example with all settings documented
- [x] .gitignore configured

### Data
- [x] data/sample_emails.json — 15 emails with full analysis
- [x] data/sample_tasks.json — 12 tasks
- [x] data/sample_calendar.json — 12 calendar events

### Utils
- [x] utils/config.py — AppConfig dataclass
- [x] utils/logging_config.py — Structured logging
- [x] utils/date_utils.py — Date helpers
- [x] utils/text_utils.py — Text cleaning
- [x] utils/json_utils.py — JSON parsing/repair
- [x] utils/security.py — Sanitization, PII, crypto
- [x] utils/file_validation.py — File type/size validation

### Models
- [x] models/email_models.py — EmailData, EmailAnalysis, Deadline, MeetingDetails
- [x] models/document_models.py — DocumentData, DocumentAnalysis
- [x] models/task_models.py — Task, SubTask
- [x] models/calendar_models.py — CalendarEvent, MeetingDetected
- [x] models/user_models.py — User, Settings
- [x] models/audit_models.py — AuditRecord
- [x] models/knowledge_models.py — KnowledgeChunk, Connection, KnowledgeGraph

### Services
- [x] services/bedrock_service.py — Mock + Live modes
- [x] services/gmail_service.py — Mock + Live modes
- [x] services/calendar_service.py — Mock + Live modes
- [x] services/document_service.py — Text extraction
- [x] services/notification_service.py — Session state notifications
- [x] services/audit_service.py — Session state audit log

### Components
- [x] components/navigation.py — Sidebar navigation
- [x] components/metric_card.py — KPI cards
- [x] components/email_card.py — Email display
- [x] components/task_card.py — Task display + actions
- [x] components/calendar_card.py — Event display
- [x] components/source_card.py — Citation display
- [x] components/charts.py — All Plotly charts

### Pages
- [x] pages/home.py — Dashboard
- [x] pages/daily_brief.py — AI daily brief
- [x] pages/email_intelligence.py — Email list + analysis
- [x] pages/document_intelligence.py — Upload + analyse documents
- [x] pages/knowledge_assistant.py — Chat interface
- [x] pages/tasks.py — Kanban + Table + Timeline
- [x] pages/calendar_page.py — Calendar + meetings
- [x] pages/knowledge_connections.py — Knowledge graph
- [x] pages/analytics.py — Full analytics
- [x] pages/data_sources.py — Service connections
- [x] pages/notifications.py — Notification centre
- [x] pages/audit_history.py — Audit log
- [x] pages/settings.py — Configuration
- [x] pages/system_status.py — Health dashboard

### Prompts
- [x] prompts/email_analysis.txt
- [x] prompts/document_analysis.txt
- [x] prompts/daily_brief.txt
- [x] prompts/question_answering.txt
- [x] prompts/task_extraction.txt
- [x] prompts/meeting_extraction.txt

### Tests
- [x] tests/test_mock_mode.py
- [x] tests/test_email_analysis.py
- [x] tests/test_task_extraction.py
- [x] tests/test_security.py

### Main App
- [x] app.py — Entry point with routing

## Phase 2 — Live AWS Integration

### AWS Setup
- [ ] Configure AWS account with Bedrock access
- [ ] Request Claude claude-sonnet-4-6 model access
- [ ] Create IAM role with Bedrock + S3 + CloudWatch permissions
- [ ] Set up S3 bucket for document storage

### Gmail Integration
- [ ] Set up Google Cloud project
- [ ] Enable Gmail API and Calendar API
- [ ] Create OAuth 2.0 credentials
- [ ] Test OAuth flow
- [ ] Handle token refresh

### Bedrock Integration
- [ ] Replace mock analysis with real Bedrock calls
- [ ] Add retry logic with exponential backoff (tenacity)
- [ ] Add response streaming
- [ ] Test prompt templates with real Claude

### Knowledge Base
- [ ] Create Bedrock Knowledge Base
- [ ] Configure S3 data source
- [ ] Implement document ingestion pipeline
- [ ] Replace mock context with real KB retrieval

### Persistence
- [ ] Move audit logs to DynamoDB or S3
- [ ] Session persistence (optional)
- [ ] User preferences storage

### Deployment
- [ ] Containerise with Docker
- [ ] Deploy to ECS Fargate
- [ ] Set up CloudFront + ALB
- [ ] Configure Route 53

## Backlog

- [ ] Email thread visualisation
- [ ] Calendar heat map
- [ ] Slack/Teams notifications integration
- [ ] Multi-user support
- [ ] Export daily brief to email
- [ ] Automated daily brief scheduling
- [ ] Mobile-responsive layout improvements
- [ ] Dark/light theme toggle
- [ ] Keyboard shortcuts

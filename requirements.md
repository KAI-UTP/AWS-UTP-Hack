# Requirements

## Functional Requirements

### FR-001: Email Intelligence
- FR-001.1: Connect to Gmail via OAuth 2.0
- FR-001.2: Fetch and display emails (last N days, configurable)
- FR-001.3: AI-categorise emails: Technical, Finance, HR, Meeting, Newsletter, Spam, Customer, Project Update, Legal, Security, General
- FR-001.4: AI-prioritise emails: Critical, High, Medium, Low
- FR-001.5: Extract action items from email body
- FR-001.6: Detect deadlines and urgency
- FR-001.7: Detect meeting invitations with date/time/location extraction
- FR-001.8: Support filtering by category, priority, date range, sender
- FR-001.9: Support full-text search across emails
- FR-001.10: Bulk analysis capability
- FR-001.11: Show AI confidence scores

### FR-002: Document Intelligence
- FR-002.1: Support PDF, DOCX, XLSX, CSV, TXT, PPTX, PNG, JPG uploads
- FR-002.2: Extract text from all supported formats
- FR-002.3: AI-generate document summary, key topics, action items
- FR-002.4: Extract financial figures and key dates from documents
- FR-002.5: Detect risk flags and compliance issues
- FR-002.6: Per-document Q&A with conversation history
- FR-002.7: File size validation (max 10 MB configurable)
- FR-002.8: Magic-byte file type verification

### FR-003: Knowledge Assistant
- FR-003.1: Natural language Q&A across emails, documents, tasks, calendar
- FR-003.2: Maintain conversation history within session
- FR-003.3: Display source citations with relevance scores
- FR-003.4: Provide sample questions for guidance
- FR-003.5: Stream responses (Phase 2)

### FR-004: Daily Brief
- FR-004.1: Generate AI executive brief on demand
- FR-004.2: Sections: Summary, Urgent, Action Required, Deadlines, Meetings, Risks, Recommendations
- FR-004.3: Date selector for historical briefs
- FR-004.4: Export as Markdown and plain text
- FR-004.5: Metrics snapshot in brief

### FR-005: Task Management
- FR-005.1: Auto-extract tasks from email analysis
- FR-005.2: Kanban view (Not Started / In Progress / Pending / Completed)
- FR-005.3: Table view with sorting and export
- FR-005.4: Timeline/Gantt view by due date
- FR-005.5: Filter by status, priority, source, category
- FR-005.6: Confirm/reject AI-extracted tasks
- FR-005.7: Manual task creation
- FR-005.8: Subtask support with completion percentage
- FR-005.9: Overdue detection

### FR-006: Calendar Intelligence
- FR-006.1: Display calendar events from Google Calendar API
- FR-006.2: Detect meeting invitations from emails
- FR-006.3: Detect calendar conflicts
- FR-006.4: Confirm/decline pending event invitations
- FR-006.5: Today/Week/Month views
- FR-006.6: Manual event creation
- FR-006.7: Add email-detected meetings to calendar

### FR-007: Knowledge Graph
- FR-007.1: Visualise entity relationships as interactive network graph
- FR-007.2: Node types: Email, Task, Person, Topic, Company, Calendar, Document
- FR-007.3: Filter by node type
- FR-007.4: Search to highlight specific nodes
- FR-007.5: Connection explorer for selected node

### FR-008: Analytics
- FR-008.1: Email volume trend chart (7-day)
- FR-008.2: Category distribution chart (donut)
- FR-008.3: Priority distribution chart
- FR-008.4: Task status chart
- FR-008.5: AI confidence distribution histogram
- FR-008.6: Response rate trend
- FR-008.7: Risk heatmap by category
- FR-008.8: Time savings calculator with ROI estimate
- FR-008.9: AI performance metrics table

### FR-009: Notifications
- FR-009.1: In-app notifications for critical events
- FR-009.2: Mark as read / delete individual notifications
- FR-009.3: Filter by level and read status
- FR-009.4: Level-based coloring: info/success/warning/error/critical

### FR-010: Audit History
- FR-010.1: Log all AI analysis actions
- FR-010.2: Log user interactions (confirm task, upload document)
- FR-010.3: Filter by action, resource type, success/error
- FR-010.4: Export audit log as CSV

### FR-011: Settings
- FR-011.1: Toggle demo/live mode
- FR-011.2: Configure Bedrock model and parameters
- FR-011.3: Configure email fetch parameters
- FR-011.4: Notification preferences
- FR-011.5: Security settings (file size, allowed types)

## Non-Functional Requirements

### NFR-001: Performance
- App must load within 3 seconds in mock mode
- Email analysis must complete within 5 seconds per email (live mode)
- Dashboard must render within 2 seconds

### NFR-002: Security
- Input sanitisation on all user inputs
- File type validation with magic byte verification
- Path traversal prevention
- PII detection capability
- Rate limiting for API calls
- No credentials stored in code or session state (only env vars)

### NFR-003: Reliability
- Graceful fallback to mock mode if AWS/Gmail unavailable
- Error messages must be user-friendly, not stack traces
- All data operations must be idempotent

### NFR-004: Scalability (Phase 2)
- Support up to 1,000 emails per analysis batch
- Support document files up to 50 MB (configurable)
- Support 100+ concurrent sessions via serverless deployment

### NFR-005: Usability
- Must work in mock mode with zero configuration
- All pages must have empty-state handling
- Colour-coded priority/status indicators throughout
- Responsive layout using Streamlit columns

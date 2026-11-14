# Design Document

## Design Philosophy

**Enterprise Dark Theme**: Professional, high-contrast dark UI suitable for executive use.

**Colour System:**
- Background: `#0f172a` (Slate 950)
- Surface: `#1e293b` (Slate 800)
- Border: `#334155` (Slate 700)
- Text Primary: `#f1f5f9` (Slate 100)
- Text Secondary: `#94a3b8` (Slate 400)
- Accent: `#6366f1` (Indigo 500)

**Priority Colours:**
- Critical: `#dc2626` (Red 600)
- High: `#f97316` (Orange 500)
- Medium: `#3b82f6` (Blue 500)
- Low: `#22c55e` (Green 500)

**Status Colours:**
- Not Started: `#64748b`
- In Progress: `#3b82f6`
- Pending: `#f59e0b`
- Completed: `#22c55e`
- Cancelled: `#6b7280`

## Layout Patterns

### Dashboard
```
[Metric][Metric][Metric][Metric]  ← Row 1: 4 cols
[Metric][Metric][Metric][Metric]  ← Row 2: 4 cols
───────────────────────────────
[Email Vol Chart (2/5)] [Donut (1.5/5)] [Priority Bar (1.5/5)]
───────────────────────────────
[Recent Emails (1/3)] [Tasks (1/3)] [Calendar (1/3)]
───────────────────────────────
[System Status Bar: 5 service chips]
```

### Email Card
```
[Priority Badge] [Category Badge]    [Date]
[Subject (bold)]
[Sender Name · email]
[AI Summary (2 lines)]
• Action Item 1
• Action Item 2
[⏰ Deadline] [📅 Meeting] [📎 Attachment] [↩️ Reply needed]
AI Confidence: 96% ▓▓▓▓▓▓▓▓▓░ 
[▼ View Details]
```

### Task Kanban
```
[Not Started (N)] [In Progress (N)] [Pending (N)] [Completed (N)]
 ┌─────────────┐   ┌─────────────┐  ┌──────────┐  ┌──────────────┐
 │[Crit] Title │   │[High] Title │  │[Med]Title│  │[Low] Title  │
 │ Description │   │  Progress % │  │ Due date │  │ ✓ Complete  │
 │ Due: Today  │   │ ▓▓▓▓▓░░░░░ │  │          │  │             │
 └─────────────┘   └─────────────┘  └──────────┘  └─────────────┘
```

### Chat Interface
```
                            [User message right-aligned ●]
[🧠 Claude AI]
[AI response text left-aligned, full width, with Markdown]
  Sources:
  [📧 Email Intelligence] [✅ Task Manager]
─────────────────────────────────────
[Message input...                  ] [➤]
```

### Daily Brief
```
[Date picker] [Generate] [Export MD] [Export TXT]
─────────────────────────────────────────────────
┌──────────────────────────────────────────────┐
│ 🧠 Executive Summary                         │
│ Text...                                      │
│ 📅 Brief for June 28, 2026 · Claude AI      │
└──────────────────────────────────────────────┘
[Metrics: 6 small cards]

[LEFT COLUMN]          [RIGHT COLUMN]
▼ 🚨 URGENT (2)       ▼ ⏰ TODAY'S DEADLINES
▼ ⚡ ACTION REQ (2)   ▼ 📅 WEEK'S DEADLINES  
▼ ⚠️ RISKS (4)       ▼ 📅 TODAY'S MEETINGS
                       ▼ 📅 WEEK'S MEETINGS

▼ 💡 AI RECOMMENDATIONS
```

## Component Inventory

| Component | File | Description |
|-----------|------|-------------|
| Navigation | `components/navigation.py` | Sidebar nav with badges |
| MetricCard | `components/metric_card.py` | KPI card with icon and delta |
| EmailCard | `components/email_card.py` | Full email card with analysis |
| TaskCard | `components/task_card.py` | Task card with actions |
| CalendarCard | `components/calendar_card.py` | Event card with confirm/decline |
| SourceCard | `components/source_card.py` | Citation card for Q&A |
| Charts | `components/charts.py` | All Plotly chart functions |

## UX Principles

1. **Zero friction** — Works out of the box in demo mode, no setup
2. **Progressive disclosure** — Summary first, details in expanders
3. **Visual hierarchy** — Critical items always red, at top
4. **Action-oriented** — Every card shows what to DO, not just what it is
5. **Confidence transparency** — AI confidence scores always visible
6. **Empty states** — Every page has a friendly empty state message

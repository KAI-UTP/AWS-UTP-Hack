"""End-to-end simulation of all page logic without Streamlit rendering."""
import sys, os, traceback, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_config
from services.gmail_service import GmailService
from services.calendar_service import CalendarService
from services.bedrock_service import BedrockService
from services.document_service import DocumentService
from services.notification_service import NotificationService
from services.audit_service import AuditService
from models.task_models import Task
from models.document_models import DocumentData
import datetime, pandas as pd, json

config = get_config()
errors = []

def ok(label, extra=""):
    print(f"  [OK] {label}" + (f" | {extra}" if extra else ""))

def fail(label, e):
    print(f"  [FAIL] {label}: {e}")
    errors.append((label, str(e)))
    traceback.print_exc()

# Init services
gmail = GmailService(config=config)
calendar = CalendarService(config=config)
bedrock = BedrockService(config=config)
doc_service = DocumentService(config=config)
notif = NotificationService()
audit = AuditService(config=config)
notif.seed_demo_notifications()
audit.seed_demo_records()

# ── 1. Home page ─────────────────────────────────────────────────────────────
print("\n=== HOME PAGE ===")
try:
    stats = gmail.get_stats()
    assert "total" in stats and "critical" in stats
    ok("gmail.get_stats()", f"total={stats['total']}")
except Exception as e: fail("gmail.get_stats()", e)

try:
    cal_stats = calendar.get_stats()
    assert "total" in cal_stats
    ok("calendar.get_stats()", f"total={cal_stats['total']}")
except Exception as e: fail("calendar.get_stats()", e)

try:
    tasks_raw = [{"id":"t1","title":"Test","status":"In Progress","priority":"High",
                  "category":"General","source":"email","ai_extracted":True,"confirmed":False,
                  "estimated_hours":2.0,"due_date":"2026-06-20"}]
    tasks = [Task.from_dict(t) for t in tasks_raw]
    overdue = [t for t in tasks if t.is_overdue]
    ok(f"Task.from_dict + is_overdue", f"overdue={len(overdue)}")
except Exception as e: fail("Task.from_dict", e)

try:
    emails = gmail.get_emails()
    critical = [e for e in emails if e.priority in ("Critical", "High")]
    ok(f"get_emails + priority filter", f"{len(critical)} critical/high")
except Exception as e: fail("get_emails priority filter", e)

try:
    cal_events = calendar.get_events()
    conflicts = [e for e in cal_events if e.conflict]
    ok("calendar.get_events()", f"{len(cal_events)} events, {len(conflicts)} conflicts")
except Exception as e: fail("calendar.get_events()", e)

# ── 2. Daily Brief ───────────────────────────────────────────────────────────
print("\n=== DAILY BRIEF PAGE ===")
try:
    brief = bedrock.generate_daily_brief({"date": str(datetime.date.today())})
    assert "executive_summary" in brief and "urgent_items" in brief and "recommendations" in brief
    ok("generate_daily_brief", f"{len(brief)} sections")
except Exception as e: fail("generate_daily_brief", e)

# ── 3. Email Intelligence ────────────────────────────────────────────────────
print("\n=== EMAIL INTELLIGENCE PAGE ===")
try:
    cats = gmail.get_categories()
    ok("get_categories", str(cats[:3]))
except Exception as e: fail("get_categories", e)

try:
    filtered = gmail.get_emails(category="Technical")
    ok("get_emails(category=Technical)", f"{len(filtered)} emails")
except Exception as e: fail("get_emails category", e)

try:
    filtered = gmail.get_emails(priority="Critical")
    ok("get_emails(priority=Critical)", f"{len(filtered)} emails")
except Exception as e: fail("get_emails priority", e)

try:
    filtered = gmail.get_emails(search_query="server")
    ok("get_emails(search_query=server)", f"{len(filtered)} emails")
except Exception as e: fail("get_emails search", e)

try:
    emails = gmail.get_emails()
    unread = [e for e in emails if e.is_unread]
    important = [e for e in emails if e.is_important]
    requires_resp = [e for e in emails if e.analysis and e.analysis.requires_response]
    ok("Label filters", f"unread={len(unread)}, important={len(important)}, resp={len(requires_resp)}")
except Exception as e: fail("label filters", e)

try:
    breakdown = {}
    for e in emails:
        cat = e.category
        pri = e.priority
        breakdown.setdefault(cat, {})
        breakdown[cat][pri] = breakdown[cat].get(pri, 0) + 1
    rows = [{"Category": cat, "Total": sum(p.values())} for cat, p in breakdown.items()]
    df = pd.DataFrame(rows)
    ok("Email breakdown DataFrame", f"{len(df)} rows")
except Exception as e: fail("Email breakdown DataFrame", e)

# ── 4. Document Intelligence ─────────────────────────────────────────────────
print("\n=== DOCUMENT INTELLIGENCE PAGE ===")
try:
    sample_text = "Sample project proposal. Budget: $150,000. Deadline: July 15, 2026."
    analysis = bedrock.analyze_document(sample_text, "proposal.pdf")
    assert hasattr(analysis, "summary") and hasattr(analysis, "key_topics")
    ok("analyze_document", f"'{analysis.summary[:50]}'")
except Exception as e: fail("analyze_document", e)

try:
    csv_content = b"Name,Value\nAlice,100\nBob,200"
    doc = doc_service.process_upload("test.csv", csv_content)
    assert doc.content
    ok("process_upload CSV", f"{len(doc.content)} chars")
except Exception as e: fail("process_upload CSV", e)

try:
    txt_content = b"Hello world. This is a test document."
    doc = doc_service.process_upload("test.txt", txt_content)
    ok("process_upload TXT", f"{len(doc.content)} chars")
except Exception as e: fail("process_upload TXT", e)

try:
    doc2 = DocumentData(id="d1", filename="test.txt", file_type="txt", content="hello")
    doc2.qa_history.append({"question": "What?", "answer": "Test"})
    assert len(doc2.qa_history) == 1
    ok("DocumentData.qa_history append")
except Exception as e: fail("DocumentData.qa_history", e)

# ── 5. Knowledge Assistant ───────────────────────────────────────────────────
print("\n=== KNOWLEDGE ASSISTANT PAGE ===")
mock_context = [
    {"source_title": "Email Analysis", "content": "Critical server outage detected."},
    {"source_title": "Task Manager", "content": "12 active tasks."},
]
try:
    result = bedrock.answer_question("What are urgent items?", mock_context)
    assert "answer" in result and "confidence" in result
    ok("answer_question", f"{result['answer'][:60]}")
except Exception as e: fail("answer_question", e)

try:
    result = bedrock.answer_question("Show upcoming meetings", mock_context, conversation_history=[])
    ok("answer_question with history")
except Exception as e: fail("answer_question with history", e)

# ── 6. Tasks page ────────────────────────────────────────────────────────────
print("\n=== TASKS PAGE ===")
try:
    tasks_raw = json.load(open("data/sample_tasks.json"))
    tasks = [Task.from_dict(t) for t in tasks_raw]
    ok("Load sample_tasks.json", f"{len(tasks)} tasks")
except Exception as e: fail("Load sample_tasks.json", e)

try:
    overdue = [t for t in tasks if t.is_overdue]
    critical = [t for t in tasks if t.priority == "Critical"]
    ai_tasks = [t for t in tasks if t.ai_extracted]
    ok("Task filters", f"overdue={len(overdue)}, critical={len(critical)}, ai={len(ai_tasks)}")
except Exception as e: fail("Task filters", e)

try:
    active_statuses = ["Not Started", "In Progress", "Pending", "Completed"]
    kanban = {s: [t for t in tasks if t.status == s] for s in active_statuses}
    summary = ", ".join(f"{k}={len(v)}" for k, v in kanban.items())
    ok("Kanban grouping", summary)
except Exception as e: fail("Kanban grouping", e)

try:
    rows = [{"Title": t.title, "Priority": t.priority, "Status": t.status,
             "Due": t.due_date or "-"} for t in tasks]
    df = pd.DataFrame(rows)
    ok("Tasks table DataFrame", f"{len(df)} rows")
except Exception as e: fail("Tasks table", e)

# ── 7. Calendar page ─────────────────────────────────────────────────────────
print("\n=== CALENDAR PAGE ===")
try:
    ev_all = calendar.get_events(view="all")
    ev_today = calendar.get_events(view="today")
    ev_week = calendar.get_events(view="week")
    ev_month = calendar.get_events(view="month")
    ok("get_events views", f"all={len(ev_all)}, today={len(ev_today)}, week={len(ev_week)}, month={len(ev_month)}")
except Exception as e: fail("get_events views", e)

try:
    pending = calendar.get_pending_confirmations()
    ok("get_pending_confirmations", f"{len(pending)}")
except Exception as e: fail("get_pending_confirmations", e)

try:
    conflicts = calendar.get_conflicts()
    ok("get_conflicts", f"{len(conflicts)}")
except Exception as e: fail("get_conflicts", e)

try:
    meetings = calendar.get_meetings_from_emails(gmail)
    ok("get_meetings_from_emails", f"{len(meetings)}")
except Exception as e: fail("get_meetings_from_emails", e)

try:
    pending = calendar.get_pending_confirmations()
    if pending:
        result = calendar.confirm_event(pending[0].id)
        ok("confirm_event", str(result))
    else:
        ok("confirm_event", "no pending events to test")
except Exception as e: fail("confirm_event", e)

# ── 8. Analytics ─────────────────────────────────────────────────────────────
print("\n=== ANALYTICS PAGE ===")
try:
    emails = gmail.get_emails()
    sentiment_data = {}
    for e in emails:
        if e.analysis:
            s = e.analysis.sentiment
            sentiment_data[s] = sentiment_data.get(s, 0) + 1
    ok("Sentiment aggregation", str(sentiment_data))
except Exception as e: fail("Sentiment aggregation", e)

try:
    risk_data = [{"category": e.category, "risk_level": e.analysis.risk_level}
                 for e in emails if e.analysis]
    ok("Risk data", f"{len(risk_data)} items")
except Exception as e: fail("Risk data", e)

try:
    from components.charts import (
        email_volume_chart, category_distribution_chart, priority_distribution_chart,
        task_status_chart, time_saved_gauge, sentiment_chart, response_rate_chart, risk_heatmap
    )
    dates = ["Jun 22","Jun 23","Jun 24","Jun 25","Jun 26","Jun 27","Jun 28"]
    counts = [3, 7, 5, 9, 4, 11, 15]
    email_volume_chart(dates, counts)
    category_distribution_chart({"Technical": 3, "Finance": 2, "General": 5})
    priority_distribution_chart({"Critical": 2, "High": 5, "Medium": 6, "Low": 2})
    task_status_chart({"Not Started": 3, "In Progress": 4, "Completed": 5})
    time_saved_gauge(3.5)
    sentiment_chart({"urgent": 2, "professional": 8})
    response_rate_chart(["W1","W2","W3"], [68, 75, 82])
    risk_heatmap(risk_data)
    ok("All 8 chart functions render")
except Exception as e: fail("Chart rendering", e)

# ── 9. Notifications ─────────────────────────────────────────────────────────
print("\n=== NOTIFICATIONS PAGE ===")
try:
    notifs = notif.get_notifications()
    unread = notif.get_unread_count()
    ok("get_notifications", f"{len(notifs)} total, {unread} unread")
except Exception as e: fail("get_notifications", e)

try:
    notif.mark_all_read()
    assert notif.get_unread_count() == 0
    ok("mark_all_read")
except Exception as e: fail("mark_all_read", e)

# ── 10. Audit History ────────────────────────────────────────────────────────
print("\n=== AUDIT HISTORY PAGE ===")
try:
    records = audit.get_records()
    assert len(records) > 0
    ok("get_records", f"{len(records)} records")
except Exception as e: fail("get_records", e)

try:
    audit.log("test_page_view", "test_user", details={"page": "home"})
    ok("audit.log")
except Exception as e: fail("audit.log", e)

# ── 11. Date utils ───────────────────────────────────────────────────────────
print("\n=== DATE UTILS ===")
try:
    from utils.date_utils import format_relative, format_date, format_datetime, days_until, is_today, is_overdue
    r1 = format_relative("2026-06-28T10:00:00Z")
    r2 = format_date("2026-06-28")
    r3 = format_datetime("2026-06-28T14:30:00Z")
    r4 = days_until("2026-07-05")
    r5 = is_today(datetime.datetime.now().isoformat())
    r6 = is_overdue("2026-01-01T00:00:00Z")
    ok("Date utils", f"relative='{r1}', date='{r2}', days_until={r4}, is_overdue={r6}")
except Exception as e: fail("Date utils", e)

# ── 12. Text utils ───────────────────────────────────────────────────────────
print("\n=== TEXT UTILS ===")
try:
    from utils.text_utils import truncate, clean_text
    t1 = truncate("Hello World this is a very long string", 20)
    t2 = clean_text("  Hello   World  \n\n  Test  ")
    ok("Text utils", f"truncate='{t1}', clean='{t2}'")
except Exception as e: fail("Text utils", e)

# ── 13. Security utils ───────────────────────────────────────────────────────
print("\n=== SECURITY UTILS ===")
try:
    from utils.security import sanitize_filename, generate_token, hash_string
    s1 = sanitize_filename("../../../etc/passwd")
    s3 = generate_token()
    s4 = hash_string("test password")
    ok("Security utils", f"sanitize='{s1}', token_len={len(s3)}")
except Exception as e: fail("Security utils", e)

# ── 14. JSON utils ───────────────────────────────────────────────────────────
print("\n=== JSON UTILS ===")
try:
    from utils.json_utils import safe_repair_loads, load_json_file
    j1 = safe_repair_loads('{"key": "value"}', {})
    j2 = safe_repair_loads('broken json', {"fallback": True})
    j3 = load_json_file("data/sample_emails.json", [])
    ok("JSON utils", f"valid={j1}, broken={j2}, emails={len(j3)}")
except Exception as e: fail("JSON utils", e)

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"RESULTS: {len(errors)} FAILURES")
if errors:
    print("\nFAILURES:")
    for label, err in errors:
        print(f"  FAIL: {label} -> {err}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED - App is fully functional!")
    sys.exit(0)

"""Runtime diagnostic - tests all services without Streamlit."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_config
from services.gmail_service import GmailService
from services.calendar_service import CalendarService
from services.bedrock_service import BedrockService
from services.notification_service import NotificationService
from services.audit_service import AuditService
from services.document_service import DocumentService

config = get_config()
errors = []

def check(label, fn):
    try:
        result = fn()
        print(f"  OK  {label}: {result}")
    except Exception as e:
        print(f"  FAIL {label}: {e}")
        errors.append((label, str(e)))
        import traceback; traceback.print_exc()

print("\n=== Gmail Service ===")
gs = GmailService(config=config)
check("get_emails count", lambda: len(gs.get_emails()))
check("get_stats keys", lambda: list(gs.get_stats().keys()))
check("get_email_by_id", lambda: gs.get_email_by_id(gs.get_emails()[0]["id"])["subject"][:40])
check("search_emails", lambda: len(gs.search_emails("urgent")))
check("get_threads", lambda: len(gs.get_threads()))

print("\n=== Calendar Service ===")
cs = CalendarService(config=config)
check("get_events count", lambda: len(cs.get_events()))
check("check_conflicts", lambda: type(cs.check_conflicts("2026-06-30", "09:00", "10:00")).__name__)
check("get_today_events", lambda: len(cs.get_today_events()))
check("get_upcoming_events", lambda: len(cs.get_upcoming_events(7)))
check("suggest_alternative_times", lambda: len(cs.suggest_alternative_times("2026-06-30", "09:00", "10:00")))

print("\n=== Bedrock Service (mock) ===")
bs = BedrockService(config=config)
emails = gs.get_emails()
check("analyze_email", lambda: list(bs.analyze_email(emails[0]).keys())[:5])
check("analyze_document", lambda: list(bs.analyze_document("Sample doc text", "test.pdf", "pdf").keys())[:5])
check("answer_question", lambda: bs.answer_question("What are my tasks?", emails[:2], [])["answer"][:50])
check("generate_daily_brief length", lambda: len(bs.generate_daily_brief(emails[:5], cs.get_events()[:3], [])))
check("extract_tasks", lambda: len(bs.extract_tasks(emails[0])))
check("detect_meetings", lambda: type(bs.detect_meetings(emails[0])).__name__)

print("\n=== Document Service ===")
ds = DocumentService(config=config)
check("supported_types", lambda: len(ds.SUPPORTED_TYPES))
check("extract text from string", lambda: len(ds.extract_text_from_string("Hello world test document")))

print("\n=== Notification Service ===")
ns = NotificationService()
ns.seed_demo_notifications()
check("get_notifications", lambda: len(ns.get_notifications()))
check("get_unread_count", lambda: ns.get_unread_count())

print("\n=== Audit Service ===")
aus = AuditService(config=config)
aus.seed_demo_records()
check("get_records", lambda: len(aus.get_records()))
aus.log("test_action", "test_user", details={"key": "value"})
check("log action", lambda: "ok")

print(f"\n{'='*40}")
if errors:
    print(f"FAILURES: {len(errors)}")
    for label, err in errors:
        print(f"  - {label}: {err}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")

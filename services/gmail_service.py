"""Gmail service with mock-mode support."""
from __future__ import annotations

from typing import Any, Optional

from models.email_models import EmailData
from utils.json_utils import load_json_file
from utils.logging_config import get_logger

logger = get_logger()


class GmailService:
    """Fetch and manage emails. In mock mode, reads from sample_emails.json."""

    def __init__(self, config: Any = None):
        from utils.config import get_config
        self.config = config or get_config()
        self.mock_mode = self.config.MOCK_MODE
        self._service = None
        self._emails_cache: list[EmailData] | None = None

        if not self.mock_mode:
            self._init_gmail()

    def _init_gmail(self):
        """Initialise the real Gmail API client."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import os

            creds = None
            token_file = self.config.GMAIL_TOKEN_FILE
            creds_file = self.config.GMAIL_CREDENTIALS_FILE

            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, self.config.GMAIL_SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_file, self.config.GMAIL_SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(token_file, "w") as token:
                    token.write(creds.to_json())

            self._service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail API client initialised")
        except Exception as e:
            logger.warning(f"Gmail init failed, falling back to mock: {e}")
            self.mock_mode = True

    # ── Public API ────────────────────────────────────────────────────────────

    def get_emails(
        self,
        max_results: int | None = None,
        days: int | None = None,
        category: str | None = None,
        priority: str | None = None,
        search_query: str | None = None,
    ) -> list[EmailData]:
        """Return emails, applying filters."""
        max_results = max_results or self.config.MAX_EMAILS_TO_FETCH
        emails = self._load_emails()

        # Apply filters
        if category and category != "All":
            emails = [e for e in emails if (e.analysis and e.analysis.category == category)]
        if priority and priority != "All":
            emails = [e for e in emails if e.priority == priority]
        if search_query:
            q = search_query.lower()
            emails = [
                e for e in emails
                if q in e.subject.lower()
                or q in e.sender.lower()
                or q in e.body.lower()
                or q in e.snippet.lower()
            ]

        return emails[:max_results]

    def get_email_by_id(self, email_id: str) -> Optional[EmailData]:
        """Return a single email by ID."""
        emails = self._load_emails()
        for email in emails:
            if email.id == email_id:
                return email
        return None

    def get_unread_count(self) -> int:
        return sum(1 for e in self._load_emails() if e.is_unread)

    def get_critical_count(self) -> int:
        return sum(1 for e in self._load_emails() if e.priority == "Critical")

    def get_emails_requiring_response(self) -> list[EmailData]:
        return [
            e for e in self._load_emails()
            if e.analysis and e.analysis.requires_response
        ]

    def get_emails_with_meetings(self) -> list[EmailData]:
        return [
            e for e in self._load_emails()
            if e.analysis and e.analysis.meeting_detected
        ]

    def get_emails_with_deadlines(self) -> list[EmailData]:
        return [
            e for e in self._load_emails()
            if e.analysis and e.analysis.deadline
        ]

    def get_categories(self) -> list[str]:
        """Return all unique email categories."""
        cats = set()
        for e in self._load_emails():
            if e.analysis:
                cats.add(e.analysis.category)
        return sorted(cats)

    def mark_as_read(self, email_id: str) -> bool:
        if self.mock_mode:
            emails = self._load_emails()
            for e in emails:
                if e.id == email_id and "UNREAD" in e.labels:
                    e.labels.remove("UNREAD")
            return True
        # Live implementation would call Gmail API
        return False

    def get_stats(self) -> dict:
        """Return email statistics."""
        emails = self._load_emails()
        cats: dict[str, int] = {}
        prios: dict[str, int] = {}
        for e in emails:
            cat = e.category
            pri = e.priority
            cats[cat] = cats.get(cat, 0) + 1
            prios[pri] = prios.get(pri, 0) + 1

        return {
            "total": len(emails),
            "unread": self.get_unread_count(),
            "critical": prios.get("Critical", 0),
            "high": prios.get("High", 0),
            "medium": prios.get("Medium", 0),
            "low": prios.get("Low", 0),
            "requiring_response": len(self.get_emails_requiring_response()),
            "with_meetings": len(self.get_emails_with_meetings()),
            "with_deadlines": len(self.get_emails_with_deadlines()),
            "categories": cats,
            "priorities": prios,
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load_emails(self) -> list[EmailData]:
        if self._emails_cache is not None:
            return self._emails_cache

        if self.mock_mode:
            raw = load_json_file(self.config.SAMPLE_EMAILS_PATH, [])
            if not raw:
                logger.warning("No sample emails loaded — check data/sample_emails.json")
            self._emails_cache = [EmailData.from_dict(e) for e in raw]
        else:
            self._emails_cache = self._fetch_live_emails()

        logger.info(f"Loaded {len(self._emails_cache)} emails")
        return self._emails_cache

    def _fetch_live_emails(self) -> list[EmailData]:
        """Fetch emails from Gmail API (live mode)."""
        if not self._service:
            return []
        try:
            results = self._service.users().messages().list(
                userId="me",
                maxResults=self.config.MAX_EMAILS_TO_FETCH,
            ).execute()
            messages = results.get("messages", [])
            emails = []
            for msg in messages:
                msg_data = self._service.users().messages().get(
                    userId="me", id=msg["id"], format="full"
                ).execute()
                email = self._parse_gmail_message(msg_data)
                if email:
                    emails.append(email)
            return emails
        except Exception as e:
            logger.error(f"Failed to fetch live emails: {e}")
            return []

    def _parse_gmail_message(self, msg: dict) -> Optional[EmailData]:
        """Parse a raw Gmail API message into EmailData."""
        try:
            headers = {
                h["name"]: h["value"]
                for h in msg.get("payload", {}).get("headers", [])
            }
            return EmailData(
                id=msg["id"],
                subject=headers.get("Subject", "(no subject)"),
                sender=headers.get("From", ""),
                sender_name=headers.get("From", "").split("<")[0].strip(),
                recipients=[headers.get("To", "")],
                date=headers.get("Date", ""),
                body="",
                snippet=msg.get("snippet", ""),
                thread_id=msg.get("threadId", ""),
                labels=msg.get("labelIds", []),
            )
        except Exception as e:
            logger.warning(f"Failed to parse Gmail message: {e}")
            return None

    def invalidate_cache(self):
        """Clear the in-memory email cache."""
        self._emails_cache = None

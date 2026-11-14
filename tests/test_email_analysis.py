"""Tests for email analysis models and parsing."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.email_models import EmailData, EmailAnalysis, Deadline, MeetingDetails, Attachment
from utils.json_utils import load_json_file


class TestEmailModels:
    def test_email_data_from_dict_basic(self):
        data = {
            "id": "test_001",
            "subject": "Test email",
            "sender": "test@test.com",
            "sender_name": "Test User",
            "date": "2026-06-28",
            "body": "Test body",
            "snippet": "Test",
            "labels": ["INBOX"],
        }
        email = EmailData.from_dict(data)
        assert email.id == "test_001"
        assert email.subject == "Test email"

    def test_email_data_from_dict_with_analysis(self):
        data = {
            "id": "test_002",
            "subject": "Critical alert",
            "sender": "alerts@system.com",
            "date": "2026-06-28",
            "body": "Server down",
            "analysis": {
                "category": "Technical",
                "priority": "Critical",
                "sentiment": "urgent",
                "summary": "Server is down",
                "action_items": ["Restart server"],
                "deadline": None,
                "meeting_detected": None,
                "key_entities": ["prod-server"],
                "requires_response": True,
                "estimated_time_to_handle": 30,
                "confidence_score": 0.95,
                "risk_level": "Critical",
                "tags": ["outage"],
            },
        }
        email = EmailData.from_dict(data)
        assert email.analysis is not None
        assert email.analysis.priority == "Critical"
        assert email.priority == "Critical"
        assert email.category == "Technical"

    def test_email_from_dict_with_deadline(self):
        data = {
            "id": "test_003",
            "subject": "Deadline",
            "sender": "hr@co.com",
            "date": "2026-06-28",
            "body": "Review due July 15",
            "analysis": {
                "category": "HR",
                "priority": "Medium",
                "sentiment": "informational",
                "summary": "Review needed",
                "action_items": [],
                "deadline": {
                    "text": "July 15",
                    "date": "2026-07-15",
                    "urgency": "medium",
                },
                "meeting_detected": None,
                "key_entities": [],
                "requires_response": False,
                "estimated_time_to_handle": 10,
                "confidence_score": 0.9,
                "risk_level": "Low",
                "tags": [],
            },
        }
        email = EmailData.from_dict(data)
        assert email.analysis.deadline is not None
        assert isinstance(email.analysis.deadline, Deadline)
        assert email.analysis.deadline.urgency == "medium"

    def test_email_from_dict_with_meeting(self):
        data = {
            "id": "test_004",
            "subject": "Meeting invite",
            "sender": "organiser@co.com",
            "date": "2026-06-28",
            "body": "Meeting on Monday",
            "analysis": {
                "category": "Meeting",
                "priority": "High",
                "sentiment": "professional",
                "summary": "Meeting invitation",
                "action_items": ["Confirm attendance"],
                "deadline": None,
                "meeting_detected": {
                    "title": "Team Sync",
                    "date": "2026-07-01",
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "timezone": "EST",
                    "location": "Zoom",
                    "attendees": ["a@co.com", "b@co.com"],
                    "agenda": ["Updates"],
                    "requires_confirmation": True,
                },
                "key_entities": [],
                "requires_response": True,
                "estimated_time_to_handle": 5,
                "confidence_score": 0.92,
                "risk_level": "Low",
                "tags": ["meeting"],
            },
        }
        email = EmailData.from_dict(data)
        assert email.analysis.meeting_detected is not None
        assert isinstance(email.analysis.meeting_detected, MeetingDetails)
        assert email.analysis.meeting_detected.title == "Team Sync"

    def test_email_with_attachments(self):
        data = {
            "id": "test_005",
            "subject": "With attachment",
            "sender": "doc@co.com",
            "date": "2026-06-28",
            "body": "See attached",
            "has_attachments": True,
            "attachments": [
                {"name": "report.pdf", "size": 1024000, "type": "application/pdf"}
            ],
        }
        email = EmailData.from_dict(data)
        assert email.has_attachments is True
        assert len(email.attachments) == 1
        assert isinstance(email.attachments[0], Attachment)
        assert email.attachments[0].name == "report.pdf"

    def test_invalid_priority_defaults_to_medium(self):
        analysis = EmailAnalysis(
            priority="INVALID",
            category="General",
        )
        assert analysis.priority == "Medium"

    def test_confidence_score_clamped(self):
        analysis = EmailAnalysis(confidence_score=1.5)
        assert analysis.confidence_score == 1.0

        analysis2 = EmailAnalysis(confidence_score=-0.5)
        assert analysis2.confidence_score == 0.0

    def test_load_all_sample_emails_as_email_data(self):
        emails_raw = load_json_file("data/sample_emails.json", [])
        assert len(emails_raw) > 0

        emails = [EmailData.from_dict(e) for e in emails_raw]
        assert len(emails) == len(emails_raw)

        for email in emails:
            assert email.id
            assert email.subject
            assert email.sender

    def test_is_unread_property(self):
        data = {"id": "x", "subject": "s", "sender": "a@b.c", "date": "2026-06-28",
                "body": "b", "labels": ["INBOX", "UNREAD"]}
        email = EmailData.from_dict(data)
        assert email.is_unread is True

    def test_is_not_unread(self):
        data = {"id": "x", "subject": "s", "sender": "a@b.c", "date": "2026-06-28",
                "body": "b", "labels": ["INBOX"]}
        email = EmailData.from_dict(data)
        assert email.is_unread is False

    def test_gmail_service_mock_returns_emails(self):
        from utils.config import AppConfig
        from services.gmail_service import GmailService
        config = AppConfig(MOCK_MODE=True)
        svc = GmailService(config=config)
        emails = svc.get_emails()
        assert len(emails) >= 15

    def test_gmail_service_filter_by_priority(self):
        from utils.config import AppConfig
        from services.gmail_service import GmailService
        config = AppConfig(MOCK_MODE=True)
        svc = GmailService(config=config)
        critical_emails = svc.get_emails(priority="Critical")
        for email in critical_emails:
            assert email.priority == "Critical"

    def test_gmail_service_search(self):
        from utils.config import AppConfig
        from services.gmail_service import GmailService
        config = AppConfig(MOCK_MODE=True)
        svc = GmailService(config=config)
        results = svc.get_emails(search_query="production")
        assert len(results) > 0

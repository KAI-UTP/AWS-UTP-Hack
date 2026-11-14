"""Tests for mock mode functionality."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import AppConfig
from utils.json_utils import load_json_file


class TestMockMode:
    def test_config_defaults_to_mock_mode(self):
        config = AppConfig()
        assert config.MOCK_MODE is True

    def test_config_from_env_respects_mock_mode(self, monkeypatch):
        monkeypatch.setenv("MOCK_MODE", "false")
        config = AppConfig.from_env()
        assert config.MOCK_MODE is False

    def test_config_from_env_mock_mode_true(self, monkeypatch):
        monkeypatch.setenv("MOCK_MODE", "true")
        config = AppConfig.from_env()
        assert config.MOCK_MODE is True

    def test_sample_emails_file_exists(self):
        emails = load_json_file("data/sample_emails.json", None)
        assert emails is not None, "data/sample_emails.json must exist"
        assert isinstance(emails, list)
        assert len(emails) >= 15, f"Expected 15+ emails, got {len(emails)}"

    def test_sample_tasks_file_exists(self):
        tasks = load_json_file("data/sample_tasks.json", None)
        assert tasks is not None, "data/sample_tasks.json must exist"
        assert isinstance(tasks, list)
        assert len(tasks) >= 10, f"Expected 10+ tasks, got {len(tasks)}"

    def test_sample_calendar_file_exists(self):
        events = load_json_file("data/sample_calendar.json", None)
        assert events is not None, "data/sample_calendar.json must exist"
        assert isinstance(events, list)
        assert len(events) >= 10, f"Expected 10+ events, got {len(events)}"

    def test_email_has_required_fields(self):
        emails = load_json_file("data/sample_emails.json", [])
        required_fields = ["id", "subject", "sender", "date", "body", "analysis"]
        for email in emails:
            for field in required_fields:
                assert field in email, f"Email missing field: {field}"

    def test_email_analysis_has_required_fields(self):
        emails = load_json_file("data/sample_emails.json", [])
        analysis_fields = ["category", "priority", "summary", "action_items", "confidence_score"]
        for email in emails:
            analysis = email.get("analysis", {})
            assert analysis, f"Email {email.get('id')} has no analysis"
            for field in analysis_fields:
                assert field in analysis, f"Analysis missing field: {field} in email {email.get('id')}"

    def test_priority_values_valid(self):
        emails = load_json_file("data/sample_emails.json", [])
        valid_priorities = {"Critical", "High", "Medium", "Low"}
        for email in emails:
            analysis = email.get("analysis", {})
            if analysis:
                priority = analysis.get("priority")
                assert priority in valid_priorities, f"Invalid priority: {priority}"

    def test_has_at_least_one_critical_email(self):
        emails = load_json_file("data/sample_emails.json", [])
        critical = [e for e in emails if e.get("analysis", {}).get("priority") == "Critical"]
        assert len(critical) >= 1, "Should have at least one critical email"

    def test_has_at_least_one_meeting_email(self):
        emails = load_json_file("data/sample_emails.json", [])
        meetings = [e for e in emails if e.get("analysis", {}).get("meeting_detected")]
        assert len(meetings) >= 1, "Should have at least one email with meeting detection"

    def test_bedrock_service_mock_mode(self):
        config = AppConfig(MOCK_MODE=True)
        from services.bedrock_service import BedrockService
        svc = BedrockService(config=config)
        assert svc.mock_mode is True

    def test_bedrock_mock_email_analysis(self):
        config = AppConfig(MOCK_MODE=True)
        from services.bedrock_service import BedrockService
        svc = BedrockService(config=config)
        result = svc.analyze_email({
            "subject": "URGENT: Server outage",
            "sender": "test@test.com",
            "body": "Production server is down",
            "snippet": "Server outage",
        })
        from models.email_models import EmailAnalysis
        assert isinstance(result, EmailAnalysis)
        assert result.priority in {"Critical", "High", "Medium", "Low"}
        assert result.confidence_score >= 0.0
        assert result.confidence_score <= 1.0

    def test_bedrock_mock_daily_brief(self):
        config = AppConfig(MOCK_MODE=True)
        from services.bedrock_service import BedrockService
        svc = BedrockService(config=config)
        result = svc.generate_daily_brief({"date": "2026-06-28"})
        assert isinstance(result, dict)
        assert "executive_summary" in result
        assert "urgent_items" in result
        assert "recommendations" in result

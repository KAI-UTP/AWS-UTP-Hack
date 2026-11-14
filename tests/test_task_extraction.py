"""Tests for task extraction and task models."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task_models import Task, SubTask
from utils.json_utils import load_json_file
from utils.config import AppConfig


class TestTaskModels:
    def test_task_from_dict_basic(self):
        data = {
            "id": "task_test_001",
            "title": "Test task",
            "status": "Not Started",
            "priority": "High",
            "category": "General",
            "source": "manual",
        }
        task = Task.from_dict(data)
        assert task.id == "task_test_001"
        assert task.status == "Not Started"
        assert task.priority == "High"

    def test_task_invalid_status_defaults(self):
        data = {"id": "t1", "title": "Test", "status": "INVALID_STATUS"}
        task = Task.from_dict(data)
        assert task.status == "Not Started"

    def test_task_invalid_priority_defaults(self):
        data = {"id": "t1", "title": "Test", "priority": "MEGA_CRITICAL"}
        task = Task.from_dict(data)
        assert task.priority == "Medium"

    def test_task_with_subtasks(self):
        data = {
            "id": "task_002",
            "title": "Task with subtasks",
            "status": "In Progress",
            "subtasks": [
                {"id": "sub1", "title": "Step 1", "done": True},
                {"id": "sub2", "title": "Step 2", "done": False},
                {"id": "sub3", "title": "Step 3", "done": False},
            ],
        }
        task = Task.from_dict(data)
        assert len(task.subtasks) == 3
        assert isinstance(task.subtasks[0], SubTask)
        assert task.subtasks[0].done is True
        assert task.completion_pct == pytest.approx(33.3, rel=0.1)

    def test_task_completion_pct_all_done(self):
        data = {
            "id": "t3",
            "title": "All done",
            "status": "Completed",
            "subtasks": [
                {"id": "s1", "title": "Step 1", "done": True},
                {"id": "s2", "title": "Step 2", "done": True},
            ],
        }
        task = Task.from_dict(data)
        assert task.completion_pct == 100.0

    def test_task_completion_pct_no_subtasks(self):
        data = {"id": "t4", "title": "No subtasks", "status": "Not Started"}
        task = Task.from_dict(data)
        assert task.completion_pct == 0.0

        data2 = {"id": "t5", "title": "Complete no subtasks", "status": "Completed"}
        task2 = Task.from_dict(data2)
        assert task2.completion_pct == 100.0

    def test_load_sample_tasks(self):
        tasks_raw = load_json_file("data/sample_tasks.json", [])
        assert len(tasks_raw) >= 10

        tasks = [Task.from_dict(t) for t in tasks_raw]
        assert len(tasks) == len(tasks_raw)
        for task in tasks:
            assert task.id
            assert task.title

    def test_sample_tasks_have_required_fields(self):
        tasks_raw = load_json_file("data/sample_tasks.json", [])
        required = ["id", "title", "status", "priority", "category"]
        for task in tasks_raw:
            for field in required:
                assert field in task, f"Task missing field: {field}"

    def test_bedrock_mock_extract_tasks(self):
        config = AppConfig(MOCK_MODE=True)
        from services.bedrock_service import BedrockService
        svc = BedrockService(config=config)
        result = svc.extract_tasks({
            "id": "email_001",
            "subject": "Critical: Server down",
            "body": "Server is down. Please restart and escalate.",
            "analysis": {
                "priority": "Critical",
                "action_items": [
                    "Restart the server",
                    "Escalate to infrastructure team",
                    "Notify stakeholders",
                ],
            },
        })
        assert isinstance(result, list)

    def test_bedrock_mock_detect_meetings(self):
        config = AppConfig(MOCK_MODE=True)
        from services.bedrock_service import BedrockService
        svc = BedrockService(config=config)
        result = svc.detect_meetings({
            "id": "email_002",
            "subject": "Meeting invite",
            "body": "Meeting on Thursday",
            "analysis": {
                "meeting_detected": {
                    "title": "Team Meeting",
                    "date": "2026-07-03",
                    "start_time": "14:00",
                    "end_time": "15:00",
                    "timezone": "EST",
                    "location": "Zoom",
                    "attendees": [],
                    "agenda": [],
                    "requires_confirmation": True,
                }
            },
        })
        assert isinstance(result, list)
        if result:
            assert "title" in result[0]

    def test_task_is_overdue(self):
        import datetime
        past_date = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
        data = {
            "id": "t_overdue",
            "title": "Overdue task",
            "status": "Not Started",
            "due_date": past_date,
        }
        task = Task.from_dict(data)
        assert task.is_overdue is True

    def test_completed_task_not_overdue(self):
        import datetime
        past_date = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
        data = {
            "id": "t_complete",
            "title": "Completed task",
            "status": "Completed",
            "due_date": past_date,
        }
        task = Task.from_dict(data)
        assert task.is_overdue is False

"""AWS Bedrock service with full mock-mode support."""
from __future__ import annotations

import json
import time
import random
from typing import Any, Optional

from models.email_models import EmailAnalysis, Deadline, MeetingDetails
from models.document_models import DocumentAnalysis
from utils.logging_config import get_logger

logger = get_logger()


class BedrockService:
    """Wrapper around AWS Bedrock / Claude API with mock-mode fallback."""

    def __init__(self, config: Any = None):
        from utils.config import get_config
        self.config = config or get_config()
        self.mock_mode = self.config.MOCK_MODE
        self._client = None

        if not self.mock_mode:
            self._init_client()

    def _init_client(self):
        try:
            import boto3
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=self.config.AWS_REGION,
            )
            logger.info("Bedrock client initialized (live mode)")
        except Exception as e:
            logger.warning(f"Bedrock client init failed, falling back to mock: {e}")
            self.mock_mode = True

    def _invoke_model(self, prompt: str) -> str:
        """Call Claude via Bedrock API."""
        if self.mock_mode or self._client is None:
            raise RuntimeError("Mock mode active – use mock methods")

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.config.BEDROCK_MAX_TOKENS,
            "temperature": self.config.BEDROCK_TEMPERATURE,
            "messages": [{"role": "user", "content": prompt}],
        })

        response = self._client.invoke_model(
            modelId=self.config.BEDROCK_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]

    # ── Email Analysis ────────────────────────────────────────────────────────

    def analyze_email(self, email_data: dict) -> EmailAnalysis:
        """Analyse an email. In mock mode returns pre-baked analysis."""
        if self.mock_mode:
            return self._mock_analyze_email(email_data)

        prompt_path = "prompts/email_analysis.txt"
        try:
            with open(prompt_path) as f:
                template = f.read()
        except FileNotFoundError:
            template = "Analyze this email and return JSON with fields: category, priority, sentiment, summary, action_items, deadline, meeting_detected, key_entities, requires_response, confidence_score, risk_level, tags"

        prompt = template + f"\n\nEMAIL:\nSubject: {email_data.get('subject','')}\nFrom: {email_data.get('sender','')}\n\n{email_data.get('body','')}"
        raw = self._invoke_model(prompt)

        from utils.json_utils import safe_repair_loads
        data = safe_repair_loads(raw, {})
        return EmailAnalysis(**data)

    def _mock_analyze_email(self, email_data: dict) -> EmailAnalysis:
        """Return realistic mock analysis based on subject/body content."""
        subject = (email_data.get("subject") or "").lower()
        body = (email_data.get("body") or "").lower()
        text = subject + " " + body

        # Priority mapping
        if any(w in text for w in ["critical", "outage", "urgent", "down", "failure"]):
            priority, risk = "Critical", "Critical"
        elif any(w in text for w in ["approval", "client", "contract", "churn", "payment"]):
            priority, risk = "High", "High"
        elif any(w in text for w in ["newsletter", "digest", "unsubscribe", "winner", "prize"]):
            priority, risk = "Low", "Low"
        else:
            priority, risk = "Medium", "Medium"

        # Category mapping
        if any(w in text for w in ["meeting", "schedule", "invite", "calendar"]):
            category = "Meeting"
        elif any(w in text for w in ["budget", "finance", "approval", "$", "payment"]):
            category = "Finance"
        elif any(w in text for w in ["hr", "performance", "review", "workday"]):
            category = "HR"
        elif any(w in text for w in ["outage", "error", "api", "server", "technical"]):
            category = "Technical"
        elif any(w in text for w in ["newsletter", "digest"]):
            category = "Newsletter"
        elif any(w in text for w in ["prize", "winner", "claim"]):
            category = "Spam"
        elif any(w in text for w in ["project", "milestone", "update", "phase"]):
            category = "Project Update"
        elif any(w in text for w in ["client", "customer", "acme", "contract"]):
            category = "Customer"
        else:
            category = "General"

        return EmailAnalysis(
            category=category,
            priority=priority,
            sentiment="urgent" if priority == "Critical" else "professional",
            summary=f"[Mock Analysis] {email_data.get('snippet', 'No summary available.')}",
            action_items=["Review this email", "Take appropriate action"],
            requires_response=priority in ("Critical", "High"),
            confidence_score=round(random.uniform(0.85, 0.98), 2),
            risk_level=risk,
            tags=[category.lower().replace(" ", "-")],
        )

    # ── Document Analysis ─────────────────────────────────────────────────────

    def analyze_document(self, content: str, filename: str) -> DocumentAnalysis:
        """Analyse document text. Mock returns template analysis."""
        if self.mock_mode:
            return self._mock_analyze_document(content, filename)

        prompt_path = "prompts/document_analysis.txt"
        try:
            with open(prompt_path) as f:
                template = f.read()
        except FileNotFoundError:
            template = "Analyze this document and return JSON analysis."

        prompt = f"{template}\n\nFILENAME: {filename}\n\nCONTENT:\n{content[:8000]}"
        raw = self._invoke_model(prompt)
        from utils.json_utils import safe_repair_loads
        data = safe_repair_loads(raw, {})
        return DocumentAnalysis(**data)

    def _mock_analyze_document(self, content: str, filename: str) -> DocumentAnalysis:
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

        doc_type_map = {
            "pdf": "Report", "docx": "Report", "xlsx": "Spreadsheet",
            "csv": "Data", "pptx": "Presentation", "txt": "General",
        }

        return DocumentAnalysis(
            summary=f"This {doc_type_map.get(ext,'document')} contains {word_count} words covering key business topics. The document appears to be structured around strategic or operational information relevant to the organization.",
            key_topics=["Business Strategy", "Operations", "Performance Metrics", "Action Items"],
            action_items=[
                "Review key findings and share with stakeholders",
                "Extract and track any deadlines mentioned",
                "Follow up on recommendations",
            ],
            entities=["Management Team", "Q3 2026", "Key Stakeholders"],
            sentiment="professional",
            document_type=doc_type_map.get(ext, "General"),
            risk_flags=[] if word_count > 100 else ["Document appears to be very short"],
            recommendations=[
                "Archive this document in the knowledge base",
                "Tag relevant team members for review",
            ],
            word_count=word_count,
            reading_time_minutes=reading_time,
            confidence_score=0.87,
            language="English",
            key_dates=[],
            financial_figures=[],
        )

    # ── Q&A ───────────────────────────────────────────────────────────────────

    def answer_question(
        self,
        question: str,
        context: list[dict],
        conversation_history: list[dict] | None = None,
    ) -> dict:
        """Answer a question given context chunks."""
        if self.mock_mode:
            return self._mock_answer_question(question, context)

        ctx_text = "\n\n".join(
            f"[Source: {c.get('source_title','Unknown')}]\n{c.get('content','')}"
            for c in context[:5]
        )
        prompt = f"Based on the following context, answer this question:\n\nQuestion: {question}\n\nContext:\n{ctx_text}\n\nProvide a detailed, accurate answer with source citations."
        answer = self._invoke_model(prompt)
        return {"answer": answer, "sources": context[:3], "confidence": 0.9}

    def _mock_answer_question(self, question: str, context: list[dict]) -> dict:
        q_lower = question.lower()

        if any(w in q_lower for w in ["urgent", "critical", "priority"]):
            answer = "Based on your emails, there are **2 critical items** requiring immediate attention:\n\n1. **Production Server Outage** (prod-web-01) — All customer-facing services are down since 08:12 UTC. The infrastructure team is investigating a connection timeout on port 443.\n\n2. **Payment API Issues** — The payment processing API is showing a 23% error rate due to database connection pool exhaustion, with an estimated $42,000 revenue impact.\n\nBoth issues are being tracked as active incidents."
        elif any(w in q_lower for w in ["meeting", "calendar", "schedule"]):
            answer = "You have **3 upcoming meetings** this week:\n\n1. **AWS Hackathon Project Review** — July 3 at 2 PM EST (pending confirmation)\n2. **Q2 Board of Directors Meeting** — July 1 at 9 AM EST ⚠️ Conflicts with All-Hands\n3. **Project Nexus Kick-off** — July 1 at 9 AM EST (confirmed)\n\n⚠️ There is a calendar conflict on July 1 at 9 AM between the Board Meeting and All-Hands. The Board Meeting takes priority per company policy."
        elif any(w in q_lower for w in ["budget", "finance", "money", "cost"]):
            answer = "Based on your recent financial emails:\n\n- **Q3 Budget Increase Request**: $150,000 pending approval from Finance Department (deadline June 30)\n- **Q3 Budget Spreadsheet**: Updated allocations shared — Engineering +$50K, Marketing -$20K\n- **Project Nexus**: $400,000 contract finalized with TechPartner (Phase 1: $240K, Phase 2: $160K)\n- **Acme Corp renewal**: $2.4M ARR at risk pending feature commitment\n\nTotal pending financial decisions: ~$2.95M"
        elif any(w in q_lower for w in ["task", "action", "todo", "do"]):
            answer = "You have **12 active tasks** extracted from your emails and calendar:\n\n**Critical (2):**\n• Resolve production server outage\n• Respond to Acme Corp feature request (July 2 deadline)\n\n**High Priority (5):**\n• Approve Q3 budget by June 30\n• Send Project Nexus contract to legal by June 28\n• Fix payment API connection pool issue\n• Return Q3 budget spreadsheet by June 30\n• Resolve July 1 calendar conflict\n\n**Medium/Low (5):**\n• Confirm hackathon meeting attendance, complete performance review, and others."
        elif any(w in q_lower for w in ["email", "inbox", "message"]):
            answer = "Your inbox has **15 analyzed emails**:\n\n- **2 Critical priority** emails (server outage, Acme Corp feature request)\n- **5 High priority** emails (budget approval, finance, tech issues, contract)\n- **6 Medium priority** emails (project updates, meetings, HR)\n- **2 Low priority** emails (newsletter, spam)\n\n**Requires response:** 7 emails\n**Has meeting invitation:** 3 emails\n**Has file attachments:** 5 emails"
        else:
            answer = f"Based on your Enterprise Intelligence Hub data, here is what I found regarding **'{question}'**:\n\nYour knowledge base contains emails, documents, tasks, and calendar events. For a more specific answer, try asking about:\n- Urgent emails or action items\n- Upcoming meetings and calendar events\n- Budget and financial matters\n- Project status updates\n- Task priorities and deadlines\n\nI'm currently operating in **demo mode** with sample data. Connect your Gmail and AWS services to query your real enterprise data."

        sources = context[:2] if context else [
            {"source_title": "Email Analysis", "content": "Mock source from email intelligence"},
            {"source_title": "Knowledge Base", "content": "Mock source from knowledge base"},
        ]

        return {
            "answer": answer,
            "sources": sources,
            "confidence": round(random.uniform(0.82, 0.96), 2),
        }

    # ── Daily Brief ───────────────────────────────────────────────────────────

    def generate_daily_brief(self, data: dict) -> dict:
        """Generate a structured daily briefing."""
        if self.mock_mode:
            return self._mock_daily_brief(data)

        context = json.dumps(data, indent=2, default=str)[:6000]
        prompt = f"Generate a professional executive daily brief based on this data:\n{context}"
        raw = self._invoke_model(prompt)
        from utils.json_utils import safe_repair_loads
        return safe_repair_loads(raw, {"brief": raw})

    def _mock_daily_brief(self, data: dict) -> dict:
        return {
            "date": "June 28, 2026",
            "executive_summary": "Today requires immediate attention on two critical incidents: a production server outage affecting all customer-facing services, and a payment API failure with $42K revenue impact. Additionally, the Acme Corp $2.4M contract renewal is at risk pending a feature commitment by July 2nd. Three budget deadlines fall on June 30th.",
            "urgent_items": [
                {
                    "title": "Production Server Outage (prod-web-01)",
                    "description": "All customer services down since 08:12 UTC. Infrastructure team investigating.",
                    "action": "Escalate to infrastructure team, communicate ETA to stakeholders",
                    "deadline": "Immediate",
                    "severity": "Critical",
                },
                {
                    "title": "Payment API Failure — $42K Revenue Impact",
                    "description": "23% payment failure rate due to connection pool exhaustion.",
                    "action": "Restart pods, increase connection pool, review 04:30 deployment",
                    "deadline": "Immediate",
                    "severity": "Critical",
                },
            ],
            "action_required": [
                {
                    "title": "Respond to Acme Corp ($2.4M at risk)",
                    "description": "David Walsh requires commitment on real-time webhooks by July 2",
                    "deadline": "July 2, 2026",
                },
                {
                    "title": "Send Project Nexus Contract to Legal",
                    "description": "TechPartner awaiting contract for $400K Project Nexus engagement",
                    "deadline": "June 28, 2026 (today)",
                },
            ],
            "deadlines_today": [
                {"item": "Project Nexus contract to legal", "time": "EOD"},
                {"item": "Stakeholder comms for server outage", "time": "ASAP"},
            ],
            "deadlines_this_week": [
                {"item": "Q3 Budget approval ($150K)", "date": "June 30"},
                {"item": "Q3 Budget spreadsheet return", "date": "June 30"},
                {"item": "Acme Corp feature commitment", "date": "July 2"},
                {"item": "AWS Hackathon review attendance confirmation", "date": "July 2"},
            ],
            "meetings_today": [
                {
                    "title": "Infrastructure Post-Incident Review",
                    "time": "3:00 PM",
                    "location": "War Room / Teams",
                    "attendees": 4,
                },
            ],
            "meetings_this_week": [
                {
                    "title": "Board of Directors Meeting",
                    "date": "July 1",
                    "time": "9:00 AM",
                    "note": "⚠️ Conflicts with All-Hands",
                },
                {
                    "title": "Project Nexus Kick-off",
                    "date": "July 1",
                    "time": "9:00 AM",
                    "note": "⚠️ Conflicts with Board Meeting",
                },
                {
                    "title": "Finance Committee - Q3 Budget",
                    "date": "June 30",
                    "time": "1:00 PM",
                    "note": "",
                },
                {
                    "title": "AWS Hackathon Project Review",
                    "date": "July 3",
                    "time": "2:00 PM",
                    "note": "Pending confirmation",
                },
            ],
            "risks": [
                {
                    "risk": "Customer churn risk: Acme Corp ($2.4M ARR)",
                    "level": "Critical",
                    "mitigation": "Immediate feature feasibility assessment and executive engagement",
                },
                {
                    "risk": "Revenue loss from payment API failure",
                    "level": "High",
                    "mitigation": "Emergency fix deployed — monitor error rates closely",
                },
                {
                    "risk": "Calendar conflict July 1 (Board + All-Hands)",
                    "level": "Medium",
                    "mitigation": "Arrange delegate for All-Hands per company policy",
                },
                {
                    "risk": "OpenSSL vulnerability CVE-2024-9999 in tech stack",
                    "level": "Medium",
                    "mitigation": "Security team reviewing affected systems this week",
                },
            ],
            "recommendations": [
                "Prioritize Acme Corp response — assign CTO and sales lead today",
                "Schedule post-mortem for server outage to prevent recurrence",
                "Consolidate June 30 budget deadlines — single finance committee review",
                "Delegate All-Hands attendance to deputy due to Board Meeting priority",
                "Fast-track OpenSSL vulnerability assessment before end of week",
            ],
            "metrics_snapshot": {
                "total_emails": 15,
                "critical_emails": 2,
                "pending_tasks": 10,
                "tasks_overdue": 2,
                "meetings_this_week": 5,
                "calendar_conflicts": 1,
                "estimated_time_saved_hours": 3.5,
            },
        }

    # ── Task Extraction ───────────────────────────────────────────────────────

    def extract_tasks(self, email_data: dict) -> list[dict]:
        """Extract actionable tasks from email content."""
        if self.mock_mode:
            return self._mock_extract_tasks(email_data)

        prompt = f"Extract actionable tasks from this email as JSON array:\n\nSubject: {email_data.get('subject','')}\n\n{email_data.get('body','')}"
        raw = self._invoke_model(prompt)
        from utils.json_utils import safe_repair_loads
        result = safe_repair_loads(raw, [])
        return result if isinstance(result, list) else []

    def _mock_extract_tasks(self, email_data: dict) -> list[dict]:
        subject = email_data.get("subject", "")
        analysis = email_data.get("analysis", {})
        action_items = analysis.get("action_items", []) if isinstance(analysis, dict) else []

        tasks = []
        for i, item in enumerate(action_items[:3]):
            tasks.append({
                "title": item,
                "priority": analysis.get("priority", "Medium") if isinstance(analysis, dict) else "Medium",
                "source": "email",
                "source_id": email_data.get("id", ""),
                "ai_extracted": True,
                "confidence": 0.88,
            })
        return tasks

    # ── Meeting Extraction ────────────────────────────────────────────────────

    def detect_meetings(self, email_data: dict) -> list[dict]:
        """Detect meeting invitations in an email."""
        if self.mock_mode:
            return self._mock_detect_meetings(email_data)

        prompt = f"Detect any meeting invitations in this email as JSON. Return [] if none found.\n\nSubject: {email_data.get('subject','')}\n\n{email_data.get('body','')}"
        raw = self._invoke_model(prompt)
        from utils.json_utils import safe_repair_loads
        result = safe_repair_loads(raw, [])
        return result if isinstance(result, list) else []

    def _mock_detect_meetings(self, email_data: dict) -> list[dict]:
        analysis = email_data.get("analysis", {})
        if not isinstance(analysis, dict):
            return []
        meeting = analysis.get("meeting_detected")
        if meeting and isinstance(meeting, dict):
            return [meeting]
        return []

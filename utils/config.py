"""Application configuration using dataclasses + dotenv."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppConfig:
    # ── App mode ──────────────────────────────────────────────────
    MOCK_MODE: bool = True
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    APP_ENV: str = "development"

    # ── AWS ───────────────────────────────────────────────────────
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_SESSION_TOKEN: str = ""

    # ── Bedrock ───────────────────────────────────────────────────
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_MAX_TOKENS: int = 4096
    BEDROCK_TEMPERATURE: float = 0.1
    BEDROCK_TOP_P: float = 0.9

    # ── Gmail OAuth ───────────────────────────────────────────────
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:8501"
    GMAIL_TOKEN_FILE: str = "token.json"
    GMAIL_CREDENTIALS_FILE: str = "credentials.json"
    GMAIL_SCOPES: list = field(default_factory=lambda: [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/calendar.readonly",
    ])

    # ── App settings ──────────────────────────────────────────────
    MAX_EMAILS_TO_FETCH: int = 50
    EMAIL_FETCH_DAYS: int = 7
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: list = field(default_factory=lambda: [
        "pdf", "docx", "xlsx", "csv", "txt", "pptx", "png", "jpg", "jpeg"
    ])

    # ── Knowledge base ────────────────────────────────────────────
    KNOWLEDGE_BASE_ID: str = ""
    KNOWLEDGE_BASE_BUCKET: str = ""

    # ── Security ──────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:8501"

    # ── Feature flags ─────────────────────────────────────────────
    ENABLE_CALENDAR: bool = True
    ENABLE_DOCUMENT_ANALYSIS: bool = True
    ENABLE_KNOWLEDGE_GRAPH: bool = True
    ENABLE_AUDIT_LOG: bool = True

    # ── Data paths ────────────────────────────────────────────────
    DATA_DIR: str = "data"
    SAMPLE_EMAILS_PATH: str = "data/sample_emails.json"
    SAMPLE_TASKS_PATH: str = "data/sample_tasks.json"
    SAMPLE_CALENDAR_PATH: str = "data/sample_calendar.json"

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create config from environment variables."""
        scopes_raw = os.getenv(
            "GMAIL_SCOPES",
            "https://www.googleapis.com/auth/gmail.readonly,"
            "https://www.googleapis.com/auth/calendar.readonly",
        )
        file_types_raw = os.getenv(
            "ALLOWED_FILE_TYPES", "pdf,docx,xlsx,csv,txt,pptx,png,jpg,jpeg"
        )

        return cls(
            MOCK_MODE=os.getenv("MOCK_MODE", "true").lower() == "true",
            DEBUG=os.getenv("DEBUG", "false").lower() == "true",
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
            APP_ENV=os.getenv("APP_ENV", "development"),
            AWS_REGION=os.getenv("AWS_REGION", "us-east-1"),
            AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID", ""),
            AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            AWS_SESSION_TOKEN=os.getenv("AWS_SESSION_TOKEN", ""),
            BEDROCK_MODEL_ID=os.getenv(
                "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
            ),
            BEDROCK_MAX_TOKENS=int(os.getenv("BEDROCK_MAX_TOKENS", "4096")),
            BEDROCK_TEMPERATURE=float(os.getenv("BEDROCK_TEMPERATURE", "0.1")),
            BEDROCK_TOP_P=float(os.getenv("BEDROCK_TOP_P", "0.9")),
            GMAIL_CLIENT_ID=os.getenv("GMAIL_CLIENT_ID", ""),
            GMAIL_CLIENT_SECRET=os.getenv("GMAIL_CLIENT_SECRET", ""),
            GMAIL_REDIRECT_URI=os.getenv("GMAIL_REDIRECT_URI", "http://localhost:8501"),
            GMAIL_TOKEN_FILE=os.getenv("GMAIL_TOKEN_FILE", "token.json"),
            GMAIL_CREDENTIALS_FILE=os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json"),
            GMAIL_SCOPES=[s.strip() for s in scopes_raw.split(",") if s.strip()],
            MAX_EMAILS_TO_FETCH=int(os.getenv("MAX_EMAILS_TO_FETCH", "50")),
            EMAIL_FETCH_DAYS=int(os.getenv("EMAIL_FETCH_DAYS", "7")),
            MAX_FILE_SIZE_MB=int(os.getenv("MAX_FILE_SIZE_MB", "10")),
            ALLOWED_FILE_TYPES=[t.strip() for t in file_types_raw.split(",") if t.strip()],
            KNOWLEDGE_BASE_ID=os.getenv("KNOWLEDGE_BASE_ID", ""),
            KNOWLEDGE_BASE_BUCKET=os.getenv("KNOWLEDGE_BASE_BUCKET", ""),
            SECRET_KEY=os.getenv("SECRET_KEY", "change-me-in-production"),
            ALLOWED_ORIGINS=os.getenv("ALLOWED_ORIGINS", "http://localhost:8501"),
            ENABLE_CALENDAR=os.getenv("ENABLE_CALENDAR", "true").lower() == "true",
            ENABLE_DOCUMENT_ANALYSIS=os.getenv("ENABLE_DOCUMENT_ANALYSIS", "true").lower() == "true",
            ENABLE_KNOWLEDGE_GRAPH=os.getenv("ENABLE_KNOWLEDGE_GRAPH", "true").lower() == "true",
            ENABLE_AUDIT_LOG=os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true",
        )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def aws_configured(self) -> bool:
        return bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY)

    @property
    def gmail_configured(self) -> bool:
        return bool(self.GMAIL_CLIENT_ID and self.GMAIL_CLIENT_SECRET)

    def __repr__(self) -> str:
        return (
            f"AppConfig(MOCK_MODE={self.MOCK_MODE}, "
            f"APP_ENV={self.APP_ENV}, "
            f"BEDROCK_MODEL_ID={self.BEDROCK_MODEL_ID})"
        )


# Singleton config instance
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Return singleton config, loading from environment."""
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config

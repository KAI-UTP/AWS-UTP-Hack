"""Structured logging configuration."""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """JSON-style structured log formatter."""

    LEVEL_COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelname, "")
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        prefix = f"{color}[{record.levelname}]{self.RESET}"
        location = f"{record.module}:{record.lineno}"
        return f"{ts} {prefix} {location} | {record.getMessage()}"


def setup_logging(level: str = "INFO", name: str = "enterprise_hub") -> logging.Logger:
    """Configure and return application logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)

    # Quieten noisy third-party loggers
    for noisy in ("boto3", "botocore", "urllib3", "google"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logger


def get_logger(name: str = "enterprise_hub") -> logging.Logger:
    """Get (or create) a named logger."""
    return logging.getLogger(name)

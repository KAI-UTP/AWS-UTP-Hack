"""Security utilities: sanitization, validation, safe file handling."""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import unicodedata
from pathlib import Path
from typing import Optional


# ── Sanitization ──────────────────────────────────────────────────────────────

def sanitize_filename(filename: str) -> str:
    """Return a safe filename, stripping path traversal and special chars."""
    # Normalize unicode
    filename = unicodedata.normalize("NFKD", filename)
    # Remove path separators and null bytes
    filename = re.sub(r"[/\\:\0]", "_", filename)
    # Keep only safe characters
    filename = re.sub(r"[^\w\s.\-]", "", filename)
    # Collapse whitespace
    filename = re.sub(r"\s+", "_", filename).strip("._")
    return filename[:255] or "unnamed_file"


def sanitize_input(text: str, max_length: int = 10_000) -> str:
    """Sanitize user input: strip dangerous patterns, limit length."""
    if not text:
        return ""
    # Remove null bytes and control characters (except newlines/tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Strip script tags and javascript: URLs
    text = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"javascript\s*:", "", text, flags=re.IGNORECASE)
    return text[:max_length]


def sanitize_html(html: str) -> str:
    """Strip all HTML tags from input."""
    return re.sub(r"<[^>]+>", "", html)


def is_safe_path(base_dir: str, target_path: str) -> bool:
    """Check that target_path does not escape base_dir (path traversal guard)."""
    base = Path(base_dir).resolve()
    target = Path(target_path).resolve()
    try:
        target.relative_to(base)
        return True
    except ValueError:
        return False


# ── Cryptography helpers ──────────────────────────────────────────────────────

def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def hash_string(value: str, salt: str = "") -> str:
    """Return SHA-256 hex digest of value + salt."""
    combined = (salt + value).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


def verify_hmac(key: str, message: str, signature: str) -> bool:
    """Verify an HMAC-SHA256 signature in constant time."""
    expected = hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


# ── PII / sensitive data detection ───────────────────────────────────────────

_PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
}


def detect_pii(text: str) -> dict[str, list[str]]:
    """Return a dict of PII type -> list of matches found in text."""
    findings: dict[str, list[str]] = {}
    for pii_type, pattern in _PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            findings[pii_type] = matches
    return findings


def mask_pii(text: str) -> str:
    """Replace detected PII with masked placeholders."""
    for pii_type, pattern in _PII_PATTERNS.items():
        text = pattern.sub(f"[REDACTED:{pii_type.upper()}]", text)
    return text


# ── Rate limiting (simple in-memory) ─────────────────────────────────────────

_rate_store: dict[str, list[float]] = {}


def check_rate_limit(key: str, max_calls: int, window_seconds: float) -> bool:
    """
    Return True if the call is allowed, False if rate limit exceeded.
    Uses a sliding window.
    """
    import time
    now = time.monotonic()
    timestamps = _rate_store.get(key, [])
    # Remove timestamps outside the window
    timestamps = [t for t in timestamps if now - t < window_seconds]
    if len(timestamps) >= max_calls:
        _rate_store[key] = timestamps
        return False
    timestamps.append(now)
    _rate_store[key] = timestamps
    return True

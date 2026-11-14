"""Text cleaning and manipulation helpers."""
from __future__ import annotations

import re
import unicodedata
from typing import Optional


def clean_text(text: str | None) -> str:
    """Remove HTML, excessive whitespace, and non-printable characters."""
    if not text:
        return ""
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Replace HTML entities
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    # Remove non-printable characters
    text = "".join(c for c in text if c.isprintable() or c in "\n\t")
    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def truncate(text: str | None, max_len: int = 200, ellipsis: str = "...") -> str:
    """Truncate text to max_len characters, appending ellipsis if needed."""
    if not text:
        return ""
    text = clean_text(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - len(ellipsis)].rstrip() + ellipsis


def extract_email_addresses(text: str) -> list[str]:
    """Extract all email addresses from text."""
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    return list(set(re.findall(pattern, text)))


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    pattern = r"https?://[^\s\"'>]+"
    return re.findall(pattern, text)


def extract_dollar_amounts(text: str) -> list[str]:
    """Extract dollar amounts from text (e.g. $150,000)."""
    pattern = r"\$[\d,]+(?:\.\d{2})?"
    return re.findall(pattern, text)


def count_words(text: str | None) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


def highlight_keywords(text: str, keywords: list[str], tag: str = "**") -> str:
    """Wrap keywords in text with a tag (Markdown bold by default)."""
    for kw in sorted(keywords, key=len, reverse=True):
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        text = pattern.sub(f"{tag}{kw}{tag}", text)
    return text


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def bullet_list(items: list[str]) -> str:
    """Format a list of strings as a bullet list."""
    return "\n".join(f"• {item}" for item in items)


def get_initials(name: str) -> str:
    """Get initials from a full name."""
    parts = name.strip().split()
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def mask_sensitive(text: str, keep_chars: int = 4) -> str:
    """Mask sensitive text, keeping only last N characters visible."""
    if len(text) <= keep_chars:
        return "*" * len(text)
    return "*" * (len(text) - keep_chars) + text[-keep_chars:]


def parse_key_value_pairs(text: str) -> dict[str, str]:
    """Parse 'Key: Value' pairs from text lines."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result

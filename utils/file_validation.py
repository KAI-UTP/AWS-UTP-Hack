"""File type and size validation utilities."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

# Magic bytes for common file types
_MAGIC_BYTES: dict[str, list[bytes]] = {
    "pdf": [b"%PDF"],
    "docx": [b"PK\x03\x04"],  # ZIP-based (Office Open XML)
    "xlsx": [b"PK\x03\x04"],
    "pptx": [b"PK\x03\x04"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "zip": [b"PK\x03\x04"],
}

_ALLOWED_EXTENSIONS = {
    "pdf", "docx", "xlsx", "csv", "txt",
    "pptx", "png", "jpg", "jpeg", "md",
}

DEFAULT_MAX_SIZE_MB = 10
DEFAULT_MAX_SIZE_BYTES = DEFAULT_MAX_SIZE_MB * 1024 * 1024


def get_extension(filename: str) -> str:
    """Return lowercase file extension without the dot."""
    return Path(filename).suffix.lstrip(".").lower()


def is_allowed_extension(filename: str, allowed: set[str] | None = None) -> bool:
    """Check if the file extension is in the allowed set."""
    allowed = allowed or _ALLOWED_EXTENSIONS
    return get_extension(filename) in allowed


def is_within_size_limit(
    size_bytes: int, max_mb: float = DEFAULT_MAX_SIZE_MB
) -> bool:
    """Check if file size is within the allowed limit."""
    return size_bytes <= max_mb * 1024 * 1024


def validate_magic_bytes(data: bytes, filename: str) -> bool:
    """Verify that the file content matches the expected magic bytes."""
    ext = get_extension(filename)
    magic_list = _MAGIC_BYTES.get(ext)
    if not magic_list:
        return True  # No magic bytes to check; accept by extension
    return any(data.startswith(magic) for magic in magic_list)


def validate_uploaded_file(
    filename: str,
    content: bytes,
    max_mb: float = DEFAULT_MAX_SIZE_MB,
    allowed_extensions: set[str] | None = None,
) -> tuple[bool, str]:
    """
    Validate an uploaded file.

    Returns:
        (is_valid, error_message) — error_message is empty string when valid.
    """
    # Extension check
    if not is_allowed_extension(filename, allowed_extensions):
        ext = get_extension(filename)
        allowed_str = ", ".join(sorted(allowed_extensions or _ALLOWED_EXTENSIONS))
        return False, f"File type '.{ext}' is not allowed. Allowed types: {allowed_str}"

    # Size check
    size_bytes = len(content)
    if not is_within_size_limit(size_bytes, max_mb):
        size_mb = size_bytes / (1024 * 1024)
        return False, f"File size {size_mb:.1f} MB exceeds the {max_mb} MB limit."

    # Magic bytes check
    if content and not validate_magic_bytes(content, filename):
        return False, "File content does not match its declared type. Possible spoofing attempt."

    return True, ""


def get_file_info(filename: str, content: bytes) -> dict:
    """Return metadata about a file."""
    return {
        "filename": filename,
        "extension": get_extension(filename),
        "size_bytes": len(content),
        "size_mb": round(len(content) / (1024 * 1024), 3),
        "is_allowed": is_allowed_extension(filename),
    }

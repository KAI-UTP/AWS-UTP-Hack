"""JSON repair and validation helpers."""
from __future__ import annotations

import json
import re
from typing import Any, Optional


def safe_loads(text: str, default: Any = None) -> Any:
    """Parse JSON string, returning default on failure."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def repair_json(text: str) -> str:
    """Attempt to repair common JSON issues."""
    if not text:
        return "{}"

    # Extract JSON if embedded in markdown code block
    code_block = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if code_block:
        text = code_block.group(1).strip()

    # Remove trailing commas before closing brackets/braces
    text = re.sub(r",\s*([}\]])", r"\1", text)

    # Add missing closing braces/brackets
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    text = text.rstrip()
    text += "}" * max(0, open_braces)
    text += "]" * max(0, open_brackets)

    return text


def safe_repair_loads(text: str, default: Any = None) -> Any:
    """Parse JSON, attempting repair if initial parse fails."""
    result = safe_loads(text, _SENTINEL := object())
    if result is not _SENTINEL:
        return result
    repaired = repair_json(text)
    return safe_loads(repaired, default)


def load_json_file(path: str, default: Any = None) -> Any:
    """Load and parse a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return default


def save_json_file(path: str, data: Any, indent: int = 2) -> bool:
    """Save data as JSON to a file. Returns True on success."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
        return True
    except (PermissionError, OSError):
        return False


def extract_json_from_text(text: str) -> Optional[Any]:
    """Try to find and extract JSON object or array from arbitrary text."""
    # Try direct parse first
    result = safe_loads(text.strip())
    if result is not None:
        return result

    # Try to find JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        result = safe_loads(match.group())
        if result is not None:
            return result

    # Try to find JSON array
    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        result = safe_loads(match.group())
        if result is not None:
            return result

    return None


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten a nested dictionary."""
    items: list = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

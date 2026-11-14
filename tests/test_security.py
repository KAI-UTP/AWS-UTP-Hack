"""Tests for security utilities."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.security import (
    sanitize_filename,
    sanitize_input,
    is_safe_path,
    detect_pii,
    mask_pii,
    generate_token,
    hash_string,
    check_rate_limit,
)
from utils.file_validation import (
    validate_uploaded_file,
    is_allowed_extension,
    is_within_size_limit,
    get_extension,
)


class TestSanitizeFilename:
    def test_safe_filename_unchanged(self):
        result = sanitize_filename("report.pdf")
        assert "report" in result
        assert ".pdf" in result

    def test_strips_path_traversal(self):
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_strips_null_bytes(self):
        result = sanitize_filename("file\x00name.txt")
        assert "\x00" not in result

    def test_empty_filename_becomes_unnamed(self):
        result = sanitize_filename("...")
        assert len(result) > 0

    def test_long_filename_truncated(self):
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 255


class TestSanitizeInput:
    def test_strips_script_tags(self):
        result = sanitize_input("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_strips_javascript_protocol(self):
        result = sanitize_input("javascript:alert(1)")
        assert "javascript:" not in result

    def test_limits_length(self):
        long_input = "a" * 20000
        result = sanitize_input(long_input, max_length=10000)
        assert len(result) <= 10000

    def test_normal_text_unchanged(self):
        normal = "Hello, this is a normal business email with numbers 12345."
        result = sanitize_input(normal)
        assert "Hello" in result
        assert "12345" in result


class TestSafePath:
    def test_safe_path_within_base(self):
        import tempfile
        base = tempfile.gettempdir()
        safe_target = os.path.join(base, "subdir", "file.txt")
        assert is_safe_path(base, safe_target) is True

    def test_unsafe_path_traversal_blocked(self):
        import tempfile
        base = os.path.join(tempfile.gettempdir(), "safe_dir")
        unsafe_target = os.path.join(base, "..", "..", "etc", "passwd")
        assert is_safe_path(base, unsafe_target) is False


class TestPIIDetection:
    def test_detects_email_address(self):
        result = detect_pii("Contact me at user@example.com for details")
        assert "email" in result
        assert "user@example.com" in result["email"]

    def test_detects_phone_number(self):
        result = detect_pii("Call us at 555-123-4567")
        assert "phone" in result

    def test_no_pii_empty_result(self):
        result = detect_pii("This text has no personal information, just business talk.")
        assert len(result) == 0 or all(len(v) == 0 for v in result.values())

    def test_mask_pii_replaces_email(self):
        text = "Contact user@example.com for help"
        masked = mask_pii(text)
        assert "user@example.com" not in masked
        assert "REDACTED" in masked


class TestFileValidation:
    def test_allowed_pdf_extension(self):
        assert is_allowed_extension("report.pdf") is True

    def test_disallowed_exe_extension(self):
        assert is_allowed_extension("malware.exe") is False

    def test_disallowed_sh_extension(self):
        assert is_allowed_extension("script.sh") is False

    def test_file_within_size_limit(self):
        assert is_within_size_limit(5 * 1024 * 1024, max_mb=10) is True

    def test_file_exceeds_size_limit(self):
        assert is_within_size_limit(15 * 1024 * 1024, max_mb=10) is False

    def test_get_extension_lowercase(self):
        assert get_extension("REPORT.PDF") == "pdf"
        assert get_extension("data.CSV") == "csv"

    def test_validate_uploaded_file_valid_pdf(self):
        # Create minimal valid PDF-like content
        content = b"%PDF-1.4 fake pdf content here"
        is_valid, error = validate_uploaded_file("test.pdf", content, max_mb=10)
        assert is_valid is True
        assert error == ""

    def test_validate_uploaded_file_too_large(self):
        content = b"x" * (11 * 1024 * 1024)  # 11 MB
        is_valid, error = validate_uploaded_file("big.pdf", content, max_mb=10)
        assert is_valid is False
        assert "MB" in error

    def test_validate_uploaded_file_disallowed_type(self):
        content = b"#!/bin/bash\nrm -rf /"
        is_valid, error = validate_uploaded_file("script.sh", content)
        assert is_valid is False
        assert "not allowed" in error


class TestRateLimiting:
    def test_within_rate_limit(self):
        key = "test_user_rate_limit"
        # Should allow first call
        assert check_rate_limit(key, max_calls=5, window_seconds=60) is True

    def test_exceeds_rate_limit(self):
        key = "test_user_exceed"
        for _ in range(5):
            check_rate_limit(key, max_calls=5, window_seconds=60)
        # 6th call should be blocked
        assert check_rate_limit(key, max_calls=5, window_seconds=60) is False


class TestCryptography:
    def test_generate_token_is_random(self):
        t1 = generate_token()
        t2 = generate_token()
        assert t1 != t2
        assert len(t1) > 10

    def test_hash_string_consistent(self):
        h1 = hash_string("hello", "salt")
        h2 = hash_string("hello", "salt")
        assert h1 == h2

    def test_hash_string_different_salts(self):
        h1 = hash_string("hello", "salt1")
        h2 = hash_string("hello", "salt2")
        assert h1 != h2

"""
exercises/6.1-test-basics/test_validators.py
Tests demonstrating pytest assertion patterns, exception testing with pytest.raises,
and clear one-assertion-per-test discipline.
"""

import pytest
from validators import is_valid_email, is_strong_password, validate_age


def test_is_valid_email_with_standard_address():
    """Verify common valid email addresses return True."""
    assert is_valid_email("dev.engineer@example.com") is True


def test_is_valid_email_rejects_missing_at_symbol():
    """Verify email without '@' returns False."""
    assert is_valid_email("user.example.com") is False


def test_is_valid_email_rejects_missing_domain():
    """Verify email without domain returns False."""
    assert is_valid_email("user@") is False


def test_is_valid_email_rejects_empty_or_whitespace():
    """Verify empty string or whitespace returns False."""
    assert is_valid_email("") is False
    assert is_valid_email("   ") is False


def test_is_strong_password_accepts_compliant_password():
    """Verify password meeting all length, casing, digit, and symbol criteria passes."""
    assert is_strong_password("Secret123!Safe") is True


def test_is_strong_password_rejects_too_short():
    """Verify password shorter than 8 characters is rejected."""
    assert is_strong_password("A1!b2") is False


def test_is_strong_password_rejects_missing_special_char():
    """Verify password missing symbols is rejected."""
    assert is_strong_password("Password123") is False


def test_is_strong_password_rejects_missing_digit():
    """Verify password missing numeric digits is rejected."""
    assert is_strong_password("Password!Special") is False


def test_validate_age_accepts_valid_boundaries():
    """Verify valid lower, middle, and upper age boundaries return True."""
    assert validate_age(0) is True
    assert validate_age(25) is True
    assert validate_age(120) is True


def test_validate_age_raises_value_error_for_negative_age():
    """Verify negative age raises ValueError with descriptive message."""
    with pytest.raises(ValueError, match="Age cannot be negative"):
        validate_age(-1)


def test_validate_age_raises_value_error_for_excessive_age():
    """Verify age greater than 120 raises ValueError."""
    with pytest.raises(ValueError, match="Age cannot exceed 120"):
        validate_age(121)


def test_validate_age_raises_type_error_for_non_integer():
    """Verify non-integer input (e.g. string or float) raises TypeError."""
    with pytest.raises(TypeError, match="Age must be an integer"):
        validate_age("twenty-five")

"""
1.6 Exceptions: Custom Exception Hierarchy & Validation Utilities
Demonstrates: Custom exception inheritance trees, raising exceptions with context,
and cleanly distinguishing domain validation errors from general Python errors.
"""

from typing import Any


# =====================================================================
# Custom Exception Hierarchy
# =====================================================================
class BaseValidationError(Exception):
    """Root class for all expected domain validation failures."""
    pass


class EmailValidationError(BaseValidationError):
    """Raised when an email address violates structural or domain rules."""
    pass


class NumericRangeError(BaseValidationError):
    """Raised when a number falls outside required boundaries."""
    pass


class MissingFieldError(BaseValidationError):
    """Raised when a mandatory string or collection is missing or empty."""
    pass


# =====================================================================
# Validation Functions
# =====================================================================
def validate_email(email: Any) -> str:
    """
    Validates email format.
    Raises TypeError for non-strings, EmailValidationError for format flaws.
    """
    if not isinstance(email, str):
        raise TypeError(f"Email must be a string, got {type(email).__name__}")

    cleaned = email.strip()
    if "@" not in cleaned or "." not in cleaned or " " in cleaned:
        raise EmailValidationError(f"Invalid email address format: '{email}'")

    parts = cleaned.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise EmailValidationError(f"Malformed local or domain part in email: '{email}'")

    domain_parts = parts[1].split(".")
    if len(domain_parts) < 2 or not all(domain_parts):
        raise EmailValidationError(f"Incomplete domain in email: '{email}'")

    return cleaned


def validate_positive_number(value: Any, field_name: str = "Value") -> float:
    """
    Validates that a numeric value is strictly positive (> 0).
    Raises NumericRangeError on zero or negative values.
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        raise BaseValidationError(f"{field_name} must be numeric, received: '{value}'")

    if num <= 0:
        raise NumericRangeError(f"{field_name} must be strictly positive (> 0), got: {num}")

    return num


def validate_range(value: float, min_val: float, max_val: float, field_name: str = "Value") -> float:
    """Validates that a number falls within [min_val, max_val]."""
    num = float(value)
    if num < min_val or num > max_val:
        raise NumericRangeError(f"{field_name} must be between {min_val} and {max_val}, got: {num}")
    return num


def validate_non_empty(text: Any, field_name: str = "Field") -> str:
    """Validates that text is non-empty after stripping whitespace."""
    if not isinstance(text, str):
        raise TypeError(f"{field_name} must be a string, got {type(text).__name__}")
    cleaned = text.strip()
    if not cleaned:
        raise MissingFieldError(f"{field_name} cannot be empty or whitespace.")
    return cleaned


if __name__ == "__main__":
    print("=== Validation Utilities Demo ===")
    try:
        email = validate_email("developer@company.com")
        print("Valid Email:", email)
        validate_email("bad-email@")
    except EmailValidationError as err:
        print("Caught expected EmailValidationError:", err)

    try:
        validate_positive_number(-15, field_name="Account Balance")
    except NumericRangeError as err:
        print("Caught expected NumericRangeError:", err)

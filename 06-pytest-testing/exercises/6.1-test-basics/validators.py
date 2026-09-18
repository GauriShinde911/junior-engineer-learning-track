"""
exercises/6.1-test-basics/validators.py
Input validation functions demonstrating error raising and boundary assertions.
"""

import re


def is_valid_email(email: str) -> bool:
    """Validate standard email format.

    Args:
        email: Email string to check.

    Returns:
        True if formatted as user@domain.tld, False otherwise.
    """
    if not isinstance(email, str) or not email.strip():
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def is_strong_password(password: str) -> bool:
    """Check password strength.

    Must have:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special symbol (!@#$%^&*()-_+=)

    Args:
        password: Password string.

    Returns:
        True if all criteria met, False otherwise.
    """
    if not isinstance(password, str) or len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()-_+=<>?/{}~" for c in password)

    return has_upper and has_lower and has_digit and has_special


def validate_age(age: int) -> bool:
    """Validate age within standard human lifetime bounds (0-120).

    Args:
        age: Integer age value.

    Returns:
        True if valid age.

    Raises:
        TypeError: If age is not an integer.
        ValueError: If age is negative or exceeds 120.
    """
    if not isinstance(age, int) or isinstance(age, bool):
        raise TypeError("Age must be an integer")
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 120:
        raise ValueError("Age cannot exceed 120")
    return True

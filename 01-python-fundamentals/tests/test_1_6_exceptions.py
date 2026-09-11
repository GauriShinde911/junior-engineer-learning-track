"""
Tests for 1.6 Exceptions
Covers: validation_utils (custom exception hierarchy), failure_handling (try/except/else/finally).
"""

import sys
from pathlib import Path
import pytest

MODULE_ROOT = Path(__file__).resolve().parent.parent
SUBSECTION_DIR = MODULE_ROOT / "exercises" / "1.6-exceptions"
if str(SUBSECTION_DIR) not in sys.path:
    sys.path.insert(0, str(SUBSECTION_DIR))

from validation_utils import (
    BaseValidationError,
    EmailValidationError,
    MissingFieldError,
    NumericRangeError,
    validate_email,
    validate_non_empty,
    validate_positive_number,
    validate_range
)
from failure_handling import process_user_registration


# =====================================================================
# Validation Utils Tests
# =====================================================================
def test_validate_email():
    assert validate_email("user@test.org") == "user@test.org"

    with pytest.raises(EmailValidationError):
        validate_email("missing-at.com")

    with pytest.raises(EmailValidationError):
        validate_email("user@no-extension")

    with pytest.raises(TypeError):
        validate_email(12345)


def test_validate_positive_number():
    assert validate_positive_number(42.5) == 42.5
    assert validate_positive_number("100") == 100.0

    with pytest.raises(NumericRangeError, match="strictly positive"):
        validate_positive_number(0)

    with pytest.raises(NumericRangeError, match="strictly positive"):
        validate_positive_number(-10)

    with pytest.raises(BaseValidationError, match="must be numeric"):
        validate_positive_number("not-a-number")


def test_validate_range():
    assert validate_range(50, 0, 100) == 50.0

    with pytest.raises(NumericRangeError, match="must be between"):
        validate_range(150, 0, 100)


def test_validate_non_empty():
    assert validate_non_empty("Valid Text") == "Valid Text"

    with pytest.raises(MissingFieldError):
        validate_non_empty("   ")

    with pytest.raises(TypeError):
        validate_non_empty(None)


# =====================================================================
# Failure Handling Tests
# =====================================================================
def test_process_registration_success():
    audit_trail = []
    payload = {"name": "Gauri Shinde", "email": "gauri@company.com", "initial_deposit": 250.0}
    res = process_user_registration(payload, audit_trail)

    assert res["success"] is True
    assert res["data"]["email"] == "gauri@company.com"
    assert len(audit_trail) == 1
    assert audit_trail[0]["status"] == "SUCCESS"


def test_process_registration_validation_failure():
    audit_trail = []
    payload = {"name": "Gauri Shinde", "email": "bad-email", "initial_deposit": 250.0}
    res = process_user_registration(payload, audit_trail)

    assert res["success"] is False
    assert res["error_type"] == "VALIDATION_FAILURE"
    assert len(audit_trail) == 1
    assert audit_trail[0]["status"] == "FAILED"


def test_process_registration_missing_field_failure():
    audit_trail = []
    payload = {"name": "", "email": "gauri@company.com", "initial_deposit": 250.0}
    res = process_user_registration(payload, audit_trail)

    assert res["success"] is False
    assert res["error_type"] == "VALIDATION_FAILURE"
    assert len(audit_trail) == 1
    assert audit_trail[0]["status"] == "FAILED"

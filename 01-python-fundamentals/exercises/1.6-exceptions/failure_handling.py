"""
1.6 Exceptions: Failure Handling & Error Discrimination
Demonstrates:
- try / except / else / finally construct
- Distinguishing expected domain validation errors from unexpected software defects
- Safe recovery strategies and guaranteed resource cleanup in finally
"""

from typing import Any, Dict, Optional

try:
    from .validation_utils import (
        BaseValidationError,
        EmailValidationError,
        MissingFieldError,
        NumericRangeError,
        validate_email,
        validate_non_empty,
        validate_positive_number
    )
except ImportError:
    from validation_utils import (
        BaseValidationError,
        EmailValidationError,
        MissingFieldError,
        NumericRangeError,
        validate_email,
        validate_non_empty,
        validate_positive_number
    )


def process_user_registration(payload: Dict[str, Any], audit_log: list) -> Dict[str, Any]:
    """
    Processes a user signup dictionary.
    Demonstrates try/except/else/finally:
    - try: perform validation and business registration
    - except BaseValidationError: handle expected user input mistakes gracefully
    - except Exception as bug: identify unexpected programming/system defects
    - else: execute operations that only run when NO errors occur
    - finally: append audit trail record unconditionally
    """
    result = {"success": False, "data": None, "error_type": None, "message": ""}
    email_for_audit = payload.get("email", "unknown")

    try:
        # Step 1: Expected validation checks
        name = validate_non_empty(payload.get("name"), field_name="User Name")
        email = validate_email(payload.get("email"))
        deposit = validate_positive_number(payload.get("initial_deposit", 0.0), field_name="Initial Deposit")

        # Step 2: Simulated core domain transformation
        account_id = f"ACC-{abs(hash(email)) % 100000:05d}"
        registered_user = {
            "account_id": account_id,
            "name": name,
            "email": email,
            "balance": round(deposit, 2)
        }

    except BaseValidationError as expected_err:
        # Expected user validation error -> client-facing guidance
        result["error_type"] = "VALIDATION_FAILURE"
        result["message"] = str(expected_err)

    except (KeyError, TypeError, AttributeError) as system_defect:
        # Unexpected programming defect -> log for engineers
        result["error_type"] = "SYSTEM_DEFECT"
        result["message"] = f"Internal processing error: {type(system_defect).__name__} - {system_defect}"

    else:
        # Runs ONLY if try succeeded without any exceptions
        result["success"] = True
        result["data"] = registered_user
        result["message"] = f"Account {registered_user['account_id']} created successfully."

    finally:
        # Guarantees audit record is stored regardless of success or failure
        audit_log.append({
            "target": email_for_audit,
            "status": "SUCCESS" if result["success"] else "FAILED",
            "error_type": result["error_type"]
        })

    return result


if __name__ == "__main__":
    print("=== Failure Handling Verification ===")
    audit_trail = []

    # Case 1: Happy path
    valid_payload = {"name": "Gauri Shinde", "email": "gauri@company.com", "initial_deposit": 500.0}
    r1 = process_user_registration(valid_payload, audit_trail)
    print("1. Valid Registration:", r1["message"])

    # Case 2: Expected validation error
    invalid_email_payload = {"name": "Gauri Shinde", "email": "invalid-email", "initial_deposit": 500.0}
    r2 = process_user_registration(invalid_email_payload, audit_trail)
    print("2. Validation Failure:", r2["message"], f"(Type: {r2['error_type']})")

    # Case 3: Expected negative amount error
    negative_deposit_payload = {"name": "Gauri Shinde", "email": "gauri@company.com", "initial_deposit": -20}
    r3 = process_user_registration(negative_deposit_payload, audit_trail)
    print("3. Negative Deposit:", r3["message"], f"(Type: {r3['error_type']})")

    print("\nAudit Trail Entries Recorded in finally:", audit_trail)

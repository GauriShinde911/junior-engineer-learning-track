import sys
import logging
from pathlib import Path
import pytest

# Add exercise directory to sys.path
EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "10.3-logging"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from logged_app import LoggedPaymentService, PaymentGatewayError


def test_logging_levels_and_context(caplog):
    service = LoggedPaymentService()
    
    with caplog.at_level(logging.DEBUG, logger="payment_service"):
        # Trigger DEBUG and INFO via authentication
        auth_success = service.authenticate_user("alice", "SuperSecretPassword!123", "tok_live_99887766")
        assert auth_success is True

        # Trigger WARNING and ERROR via insufficient funds
        with pytest.raises(PaymentGatewayError):
            service.process_payment(
                order_id="ORD-999",
                user_id="usr_200",  # Has balance 15.00 (< 50.0 triggers WARNING, < 100 triggers ERROR)
                amount=100.00,
                card_details={"card_number": "4111222233334444", "cvv": "987"},
                idempotency_key="key_123"
            )

    levels_seen = {record.levelname for record in caplog.records}
    assert "DEBUG" in levels_seen
    assert "INFO" in levels_seen
    assert "WARNING" in levels_seen
    assert "ERROR" in levels_seen


def test_exception_logging_captures_traceback(caplog):
    service = LoggedPaymentService()

    with caplog.at_level(logging.ERROR, logger="payment_service"):
        with pytest.raises(PaymentGatewayError):
            service.process_payment(
                order_id="ORD-EXC-1",
                user_id="usr_200",
                amount=500.00,
                card_details={"card_number": "4111222233334444", "cvv": "123"},
                idempotency_key="idem_err"
            )

    error_records = [r for r in caplog.records if r.levelname == "ERROR"]
    assert len(error_records) >= 1
    # Check that logger.exception attached exc_info
    exc_record = error_records[0]
    assert exc_record.exc_info is not None
    assert "PaymentGatewayError: Insufficient funds" in caplog.text


def test_sensitive_credentials_never_logged(caplog):
    service = LoggedPaymentService()

    secret_password = "SuperSecretPassword!123"
    secret_token = "tok_live_99887766"
    raw_card_number = "4111222233334444"
    secret_cvv = "987"

    with caplog.at_level(logging.DEBUG, logger="payment_service"):
        # Authenticate
        service.authenticate_user("alice", secret_password, secret_token)

        # Process payment
        service.process_payment(
            order_id="ORD-SEC-01",
            user_id="usr_100",
            amount=25.00,
            card_details={"card_number": raw_card_number, "cvv": secret_cvv},
            idempotency_key="idem_sec"
        )

    log_output = caplog.text

    # Assert secrets do NOT appear in log output
    assert secret_password not in log_output
    assert secret_token not in log_output
    assert raw_card_number not in log_output
    assert f"cvv={secret_cvv}" not in log_output
    assert f"'{secret_cvv}'" not in log_output

    # Assert masked PAN is present instead
    assert "****-****-****-4444" in log_output

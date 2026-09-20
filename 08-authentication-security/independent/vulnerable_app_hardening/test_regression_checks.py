"""Regression test suite proving all 6 vulnerabilities from FINDINGS.md are remediated."""

import os
import sys
from pathlib import Path
import pytest

app_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(app_dir))

from fixed_app import (
    HardenedBankingApp,
    AuthenticationFailedError,
    SessionExpiredError,
    UnauthorizedAccessError,
    ValidationError
)


@pytest.fixture
def app():
    # 5-second TTL and fast bcrypt rounds for testing
    return HardenedBankingApp(session_ttl_seconds=5, bcrypt_rounds=4)


def test_regression_vuln01_secret_key_from_environment(monkeypatch):
    """VULN-01 REGRESSION: Verifies SECRET_KEY is dynamically loaded from environment."""
    import fixed_app
    test_key = "custom_dynamic_production_secret_key_12345"
    monkeypatch.setenv("APP_SECRET_KEY", test_key)
    assert fixed_app.get_secret_key() == test_key


def test_regression_vuln02_plaintext_passwords_never_stored(app):
    """VULN-02 REGRESSION: Verifies passwords are saved only as bcrypt hashes, never plaintext."""
    alice = app.users["alice"]
    raw_pass = "AliceSecurePass2026!"

    # Plaintext password is not stored anywhere
    assert alice.password_hash != raw_pass
    assert raw_pass not in alice.password_hash
    assert alice.password_hash.startswith("$2b$") or alice.password_hash.startswith("$2a$")

    # Authentication works with correct password
    token = app.login_user("alice", raw_pass)
    assert token is not None

    # Fails with wrong password
    with pytest.raises(AuthenticationFailedError):
        app.login_user("alice", "WrongGuess123")


def test_regression_vuln03_cryptographic_tokens_and_ttl_expiration(app):
    """VULN-03 REGRESSION: Verifies high-entropy token generation and TTL session expiration."""
    t0 = 5000.0
    token = app.login_user("alice", "AliceSecurePass2026!", current_time=t0)

    # 1. Entropy verification (not a 4-digit number like sess-1234)
    assert len(token) >= 40
    assert not token.startswith("sess-")

    # 2. Active within TTL (t0 + 4 < t0 + 5)
    statement = app.get_account_statement(token, "ACC-1001", current_time=t0 + 4.0)
    assert statement["owner"] == "alice"

    # 3. Expired beyond TTL (t0 + 6 > t0 + 5)
    with pytest.raises(SessionExpiredError):
        app.get_account_statement(token, "ACC-1001", current_time=t0 + 6.0)


def test_regression_vuln04_idor_blocked_on_account_statements(app):
    """VULN-04 REGRESSION: Verifies users cannot access account statements they do not own."""
    alice_token = app.login_user("alice", "AliceSecurePass2026!")
    bob_token = app.login_user("bob", "BobSecretPass2026!")

    # Alice accessing her own account ACC-1001 succeeds
    alice_stmt = app.get_account_statement(alice_token, "ACC-1001")
    assert alice_stmt["owner"] == "alice"
    assert alice_stmt["balance"] == 5200.0

    # Alice attempting to access Bob's account ACC-1002 is BLOCKED
    with pytest.raises(UnauthorizedAccessError):
        app.get_account_statement(alice_token, "ACC-1002")

    # Bob accessing his own account ACC-1002 succeeds
    bob_stmt = app.get_account_statement(bob_token, "ACC-1002")
    assert bob_stmt["owner"] == "bob"

    # Bob attempting to access Alice's account ACC-1001 is BLOCKED
    with pytest.raises(UnauthorizedAccessError):
        app.get_account_statement(bob_token, "ACC-1001")


def test_regression_vuln05_mass_assignment_privilege_escalation_blocked(app):
    """VULN-05 REGRESSION: Verifies user registration cannot be tricked into granting admin rights."""
    malicious_registration_payload = {
        "password": "HackerPassword2026!",
        "full_name": "Eve Attacker",
        "is_admin": True,           # Injected admin flag
        "role": "admin",            # Injected admin role
        "balance": 9999999.0        # Injected balance
    }

    registered = app.register_user("eve", malicious_registration_payload)

    # Injected privileges are completely ignored and stripped
    assert registered["role"] == "customer"
    assert registered["is_admin"] is False
    assert app.users["eve"].role == "customer"
    assert app.users["eve"].is_admin is False

    # Account balance starts at 0.0, injected balance ignored
    eve_token = app.login_user("eve", "HackerPassword2026!")
    eve_stmt = app.get_account_statement(eve_token, registered["account_id"])
    assert eve_stmt["balance"] == 0.0


def test_regression_vuln06_safe_logging_never_exposes_credentials(app):
    """VULN-06 REGRESSION: Verifies audit logs redact plaintext passwords and active tokens."""
    plain_password = "AliceSecurePass2026!"
    token = app.login_user("alice", plain_password)

    # Inspect all recorded audit log strings
    all_logs = " ".join(app.audit_log_entries)

    # Plaintext password must NEVER appear in logs
    assert plain_password not in all_logs

    # Active session token must NEVER appear in logs
    assert token not in all_logs

    # Redaction marker must be present
    assert "[REDACTED]" in all_logs

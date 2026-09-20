"""Tests verifying vulnerability mechanics and risk findings from Exercise 8.1.

These tests prove that the deliberate security anti-patterns in insecure_sample_app.py
actually reproduce the specific security violations detailed in RISK_FINDINGS.md.
"""

import sys
from pathlib import Path

# Add exercises folder to sys.path for direct imports
exercises_dir = Path(__file__).resolve().parent.parent / "exercises" / "8.1-security-basics"
sys.path.insert(0, str(exercises_dir))

import insecure_sample_app as app


def test_vulnerability_sec01_hardcoded_secret_is_exposed():
    """SEC-01: Verifies that sensitive cryptographic key is accessible as hardcoded module constant."""
    assert hasattr(app, "JWT_SECRET_KEY")
    assert isinstance(app.JWT_SECRET_KEY, str)
    assert app.JWT_SECRET_KEY == "hardcoded_secret_key_xyz_12345"


def test_vulnerability_sec02_plaintext_passwords_and_comparison():
    """SEC-02: Verifies that database stores plaintext passwords and allows direct plaintext auth."""
    # Stored value is raw plaintext, not a salted cryptographic hash
    assert app.USERS_DB["alice"]["password"] == "alice_password_123"
    assert app.authenticate_user_insecure("alice", "alice_password_123") is True
    assert app.authenticate_user_insecure("alice", "wrong_password") is False


def test_vulnerability_sec03_unauthorized_privilege_escalation():
    """SEC-03: Verifies unprivileged user can escalate privileges due to missing authorization checks."""
    assert app.USERS_DB["alice"]["role"] == "user"

    # Alice (regular user) elevates herself to admin
    success = app.update_user_role_insecure(caller="alice", target_user="alice", new_role="admin")
    assert success is True
    assert app.USERS_DB["alice"]["role"] == "admin"

    # Reset role back to user for other tests
    app.USERS_DB["alice"]["role"] = "user"


def test_vulnerability_sec04_arbitrary_resource_access_idor():
    """SEC-04: Verifies arbitrary document access allows reading confidential system secrets."""
    secret_doc = app.read_document_insecure("system/secrets.txt")
    assert secret_doc is not None
    assert "CONFIDENTIAL: System payroll" in secret_doc


def test_vulnerability_sec05_mass_assignment_overwrites_protected_fields():
    """SEC-05: Verifies that unbounded dictionary updates allow overwriting protected role attribute."""
    assert app.USERS_DB["alice"]["role"] == "user"

    # Client payload injects 'role' into profile update
    malicious_payload = {
        "bio": "Hacker",
        "role": "superadmin"
    }
    updated = app.process_profile_update_insecure("alice", malicious_payload)
    assert updated["role"] == "superadmin"
    assert app.USERS_DB["alice"]["role"] == "superadmin"

    # Reset role
    app.USERS_DB["alice"]["role"] = "user"

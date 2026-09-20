"""Tests for Exercise 8.5 verifying security hardening against Exercise 8.1 vulnerabilities."""

import sys
from pathlib import Path
import pytest

exercises_dir = Path(__file__).resolve().parent.parent / "exercises" / "8.5-web-api-security"
sys.path.insert(0, str(exercises_dir))

import hardened_sample_app as app
from hardened_sample_app import (
    SecurityValidationError,
    AuthenticationRequiredError,
    AccessForbiddenError,
    ResourceNotFoundError
)


@pytest.fixture(autouse=True)
def reset_app_state():
    """Resets users and active sessions before each test."""
    app.initialize_sample_users(bcrypt_rounds=4)
    app.ACTIVE_SESSIONS.clear()


def test_hardened_authentication_with_bcrypt():
    """SEC-02 FIX: Verifies authentication succeeds with correct password and fails with invalid."""
    token = app.authenticate_user_hardened("alice", "AliceSecurePass2026!")
    assert token is not None
    assert token in app.ACTIVE_SESSIONS

    # Wrong password rejected
    fail_token = app.authenticate_user_hardened("alice", "WrongPassword!")
    assert fail_token is None

    # Unknown user rejected
    ghost_token = app.authenticate_user_hardened("unknown", "AnyPassword!")
    assert ghost_token is None


def test_role_update_requires_authentication():
    """SEC-03 FIX: Verifies unauthenticated callers cannot modify roles."""
    with pytest.raises(AuthenticationRequiredError):
        app.update_user_role_hardened(
            auth_token="invalid_or_missing_token",
            target_username="alice",
            new_role="admin"
        )


def test_role_update_denies_non_admin_user():
    """SEC-03 FIX: Verifies regular users cannot escalate their own or other users' roles."""
    alice_token = app.authenticate_user_hardened("alice", "AliceSecurePass2026!")
    assert alice_token is not None

    with pytest.raises(AccessForbiddenError):
        app.update_user_role_hardened(
            auth_token=alice_token,
            target_username="alice",
            new_role="admin"
        )


def test_role_update_succeeds_for_authenticated_admin():
    """SEC-03 FIX: Verifies authorized administrator can modify roles to allowed values."""
    admin_token = app.authenticate_user_hardened("admin", "AdminMasterPass2026!")
    assert admin_token is not None

    # Admin changes alice to admin
    success = app.update_user_role_hardened(
        auth_token=admin_token,
        target_username="alice",
        new_role="admin"
    )
    assert success is True
    assert app.USERS_DB["alice"].role == "admin"


def test_role_update_rejects_invalid_roles():
    """SEC-03 FIX: Verifies role must match allowed enum values."""
    admin_token = app.authenticate_user_hardened("admin", "AdminMasterPass2026!")

    with pytest.raises(SecurityValidationError):
        app.update_user_role_hardened(
            auth_token=admin_token,
            target_username="alice",
            new_role="superuser_root"
        )


def test_read_document_rejects_path_traversal_attempts():
    """SEC-04 FIX: Verifies directory traversal syntax is rejected by allow-list validation."""
    alice_token = app.authenticate_user_hardened("alice", "AliceSecurePass2026!")

    # Attempt path traversal to reach system secrets
    traversal_payloads = [
        "../system/secrets",
        "..\\system\\secrets",
        "secrets/../system",
        "notes;cat /etc/passwd"
    ]
    for payload in traversal_payloads:
        with pytest.raises(SecurityValidationError):
            app.read_document_hardened(alice_token, payload)


def test_read_document_enforces_tenant_isolation():
    """SEC-04 FIX: Verifies users cannot read documents belonging to other users or system."""
    alice_token = app.authenticate_user_hardened("alice", "AliceSecurePass2026!")

    # Even with a safe slug name, alice cannot read system's secrets document
    with pytest.raises(ResourceNotFoundError):
        app.read_document_hardened(alice_token, "secrets")

    # Alice can read her own document
    doc = app.read_document_hardened(alice_token, "notes")
    assert "Alice's verified private notes" in doc


def test_profile_update_blocks_mass_assignment():
    """SEC-05 FIX: Verifies that inject attempts on protected fields like 'role' are rejected."""
    alice_token = app.authenticate_user_hardened("alice", "AliceSecurePass2026!")

    # Attacker tries to elevate role via profile update payload
    malicious_payload = {
        "bio": "Updated developer bio",
        "role": "admin"
    }
    with pytest.raises(SecurityValidationError) as exc_info:
        app.process_profile_update_hardened(alice_token, "alice", malicious_payload)
    assert "Disallowed fields" in str(exc_info.value)
    assert "role" in str(exc_info.value)


def test_profile_update_blocks_editing_other_users():
    """SEC-05 FIX: Verifies users cannot update another user's profile."""
    alice_token = app.authenticate_user_hardened("alice", "AliceSecurePass2026!")

    with pytest.raises(AccessForbiddenError):
        app.process_profile_update_hardened(
            alice_token,
            "admin",
            {"bio": "Tampered admin bio"}
        )


def test_profile_update_accepts_valid_allowlisted_fields():
    """SEC-05 FIX: Verifies valid profile updates succeed."""
    alice_token = app.authenticate_user_hardened("alice", "AliceSecurePass2026!")

    valid_payload = {
        "email": "alice_new@company.org",
        "bio": "Lead security researcher"
    }
    updated = app.process_profile_update_hardened(alice_token, "alice", valid_payload)
    assert updated["email"] == "alice_new@company.org"
    assert updated["bio"] == "Lead security researcher"
    assert app.USERS_DB["alice"].email == "alice_new@company.org"

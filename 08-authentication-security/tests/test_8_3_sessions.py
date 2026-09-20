"""Tests for Exercise 8.3 session management and role-based access control."""

import sys
import time
from pathlib import Path
import pytest

exercises_dir = Path(__file__).resolve().parent.parent / "exercises" / "8.3-sessions"
sys.path.insert(0, str(exercises_dir))

from auth_service import (
    AuthService,
    AuthenticationError,
    SessionExpiredError,
    InvalidSessionError
)
from role_based_access import (
    ApplicationPortalService,
    AccessDeniedError
)


@pytest.fixture
def auth_service():
    # 5-second TTL for fast testing of expiration
    return AuthService(session_ttl_seconds=5)


@pytest.fixture
def portal(auth_service):
    return ApplicationPortalService(auth_service)


def test_login_successful_creates_unpredictable_session(auth_service):
    """Verifies that login issues a valid, non-empty session token."""
    token = auth_service.login("alice", "AliceSecurePass2026!")
    assert isinstance(token, str)
    assert len(token) >= 32
    assert auth_service.is_authenticated(token) is True

    session = auth_service.get_session(token)
    assert session.username == "alice"
    assert session.role == "user"


def test_login_invalid_credentials_rejected(auth_service):
    """Verifies that wrong passwords or non-existent usernames fail authentication."""
    with pytest.raises(AuthenticationError):
        auth_service.login("alice", "WrongPassword123")

    with pytest.raises(AuthenticationError):
        auth_service.login("ghost_user", "AnyPassword123")


def test_logout_invalidates_session(auth_service):
    """Verifies that logging out immediately revokes the session token."""
    token = auth_service.login("alice", "AliceSecurePass2026!")
    assert auth_service.is_authenticated(token) is True

    logged_out = auth_service.logout(token)
    assert logged_out is True
    assert auth_service.is_authenticated(token) is False

    with pytest.raises(InvalidSessionError):
        auth_service.get_session(token)


def test_session_expiration_after_ttl(auth_service):
    """Verifies that a session token becomes invalid once TTL passes."""
    start_time = 1000.0
    token = auth_service.login("alice", "AliceSecurePass2026!", current_time=start_time)

    # Within TTL (start + 4s < start + 5s)
    assert auth_service.is_authenticated(token, current_time=start_time + 4.0) is True

    # Beyond TTL (start + 6s > start + 5s)
    assert auth_service.is_authenticated(token, current_time=start_time + 6.0) is False

    with pytest.raises(SessionExpiredError):
        auth_service.get_session(token, current_time=start_time + 6.0)


def test_role_based_access_allows_user_actions(portal, auth_service):
    """Verifies regular users can perform user-level actions."""
    user_token = auth_service.login("alice", "AliceSecurePass2026!")

    profile = portal.view_my_profile(user_token)
    assert profile["username"] == "alice"
    assert profile["role"] == "user"

    ticket = portal.submit_support_ticket(user_token, "Broken Link", "Help fixing 404")
    assert ticket["author"] == "alice"
    assert ticket["ticket_id"].startswith("TCK-")


def test_role_based_access_denies_unauthorized_user(portal, auth_service):
    """Verifies regular users are denied when attempting admin actions."""
    user_token = auth_service.login("bob", "BobSecretPass2026!")

    # Regular user attempting admin audit log inspection
    with pytest.raises(AccessDeniedError):
        portal.view_system_audit_logs(user_token)

    # Regular user attempting admin user deletion
    with pytest.raises(AccessDeniedError):
        portal.delete_system_user(user_token, "alice")


def test_role_based_access_allows_admin_actions(portal, auth_service):
    """Verifies admin users can perform both administrative and standard actions."""
    admin_token = auth_service.login("admin_carol", "CarolMasterAdmin2026!")

    # Admin viewing audit logs
    logs = portal.view_system_audit_logs(admin_token)
    assert len(logs) >= 2

    # Admin deleting a user
    result = portal.delete_system_user(admin_token, "bob")
    assert result is True

    # Audit log reflects the deletion
    updated_logs = portal.view_system_audit_logs(admin_token)
    assert any(log["event"] == "USER_DELETED" for log in updated_logs)


def test_purge_expired_sessions(auth_service):
    """Verifies batch purging removes all expired sessions."""
    t0 = 2000.0
    tok1 = auth_service.login("alice", "AliceSecurePass2026!", current_time=t0)
    tok2 = auth_service.login("bob", "BobSecretPass2026!", current_time=t0 + 2.0)

    # At t0 + 6, tok1 is expired (t0+5), tok2 is still active (t0+7)
    purged = auth_service.purge_expired_sessions(current_time=t0 + 6.0)
    assert purged == 1
    assert auth_service.is_authenticated(tok1, current_time=t0 + 6.0) is False
    assert auth_service.is_authenticated(tok2, current_time=t0 + 6.0) is True

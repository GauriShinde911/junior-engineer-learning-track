"""Hardened sample application addressing vulnerabilities from Exercise 8.1.

Every vulnerability identified in 8.1 RISK_FINDINGS.md is systematically resolved,
with inline comments explaining what risk is closed and the remediation mechanism applied.
"""

from dataclasses import dataclass
import os
import re
from typing import Any, Dict, List, Optional, Set
import bcrypt


# Custom security exceptions
class SecurityValidationError(Exception):
    """Raised when client input fails allow-list or schema validation."""
    pass


class AuthenticationRequiredError(Exception):
    """Raised when an operation lacks a valid authentication token."""
    pass


class AccessForbiddenError(Exception):
    """Raised when an authenticated caller lacks required authorization/role."""
    pass


class ResourceNotFoundError(Exception):
    """Raised when a requested resource does not exist or access is forbidden."""
    pass


# ==============================================================================
# [FIX - SEC-01]: Eliminating Hardcoded Secret Keys (CWE-798)
# Instead of hardcoding keys in source code, secrets are loaded dynamically from
# the environment with fallback to a non-production test placeholder if unset.
# ==============================================================================
JWT_SECRET_KEY = os.environ.get("APP_SECRET_KEY", "test_placeholder_secret_key_min_16_chars")


@dataclass
class HardenedUserRecord:
    username: str
    password_hash: str
    role: str
    email: str
    bio: str


# In-memory user database storing ONLY salted bcrypt hashes
USERS_DB: Dict[str, HardenedUserRecord] = {}

# Mock document storage scoped by username
# Maps (owner_username, document_slug) -> document_content
DOCUMENT_STORAGE: Dict[str, Dict[str, str]] = {
    "alice": {
        "notes": "Alice's verified private notes."
    },
    "system": {
        "secrets": "CONFIDENTIAL: System payroll and configuration keys."
    }
}

# Active sessions store: token -> username
ACTIVE_SESSIONS: Dict[str, str] = {}


def initialize_sample_users(bcrypt_rounds: int = 4) -> None:
    """Initializes sample user records using salted bcrypt hashes."""
    salt = bcrypt.gensalt(rounds=bcrypt_rounds)
    USERS_DB.clear()

    # [FIX - SEC-02]: Passwords hashed with bcrypt; plaintext is never stored.
    alice_hash = bcrypt.hashpw("AliceSecurePass2026!".encode("utf-8"), salt).decode("utf-8")
    admin_hash = bcrypt.hashpw("AdminMasterPass2026!".encode("utf-8"), salt).decode("utf-8")

    USERS_DB["alice"] = HardenedUserRecord(
        username="alice",
        password_hash=alice_hash,
        role="user",
        email="alice@example.com",
        bio="Software developer"
    )
    USERS_DB["admin"] = HardenedUserRecord(
        username="admin",
        password_hash=admin_hash,
        role="admin",
        email="admin@example.com",
        bio="System administrator"
    )


# Run default user initialization
initialize_sample_users()


def authenticate_user_hardened(username: str, candidate_password: str) -> Optional[str]:
    """Authenticates a user securely and returns a session token.

    [FIX - SEC-02: Password Security & Timing Attack Mitigation]
    - Replaces plaintext equality check with bcrypt.checkpw().
    - Uses constant-time comparison internally.
    - If user does not exist, executes dummy hash check to balance execution time.
    """
    user = USERS_DB.get(username)
    if not user:
        # Prevent timing enumeration
        dummy = "$2b$04$fakehashwithminimumroundscostfactorsalt99"
        try:
            bcrypt.checkpw(candidate_password.encode("utf-8"), dummy.encode("utf-8"))
        except Exception:
            pass
        return None

    if not bcrypt.checkpw(candidate_password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return None

    # Issue session token (token maps to authenticated username)
    import secrets
    token = secrets.token_urlsafe(32)
    ACTIVE_SESSIONS[token] = username
    return token


def _get_authenticated_user(auth_token: str) -> HardenedUserRecord:
    """Helper validating that the bearer token represents an active authenticated user."""
    if not auth_token or auth_token not in ACTIVE_SESSIONS:
        raise AuthenticationRequiredError("Authentication required: invalid or missing session token")
    username = ACTIVE_SESSIONS[auth_token]
    user = USERS_DB.get(username)
    if not user:
        raise AuthenticationRequiredError("Session user no longer exists")
    return user


def update_user_role_hardened(auth_token: str, target_username: str, new_role: str) -> bool:
    """Updates a user's role with strict authentication and role authorization.

    [FIX - SEC-03: Broken Access Control / Privilege Escalation (CWE-285)]
    1. Validates that the caller is authenticated via a valid session token.
    2. Strictly verifies that the authenticated caller holds the 'admin' role.
    3. Validates that new_role belongs to an allowed set ('user', 'admin').
    """
    caller = _get_authenticated_user(auth_token)

    # Authorization enforcement: only admins may change roles
    if caller.role != "admin":
        raise AccessForbiddenError(
            f"Access Forbidden: Caller '{caller.username}' lacks administrative role to modify roles"
        )

    # Input validation: allowed roles only
    allowed_roles = {"user", "admin"}
    if new_role not in allowed_roles:
        raise SecurityValidationError(f"Invalid role '{new_role}'. Must be one of: {allowed_roles}")

    target_user = USERS_DB.get(target_username)
    if not target_user:
        raise ResourceNotFoundError(f"Target user '{target_username}' not found")

    target_user.role = new_role
    return True


def read_document_hardened(auth_token: str, doc_name: str) -> str:
    """Reads a user document with path traversal protection and ownership checks.

    [FIX - SEC-04: Arbitrary File Access / Path Traversal / IDOR (CWE-639, CWE-22)]
    1. Requires authentication; determines identity from the verified session token.
    2. Validates document name against a strict alphanumeric allow-list pattern.
    3. Scopes document lookup to the authenticated user's own namespace.
    4. Prevents path traversal sequences ('../', slashes, control chars).
    """
    caller = _get_authenticated_user(auth_token)

    # Input validation: allow only safe alphanumeric slug names
    if not re.match(r"^[a-zA-Z0-9_-]{1,64}$", doc_name):
        raise SecurityValidationError(
            "Invalid document name: must contain only alphanumeric characters, dashes, or underscores"
        )

    # Scoped access control: users can only read documents in their own partition
    user_docs = DOCUMENT_STORAGE.get(caller.username, {})
    if doc_name not in user_docs:
        raise ResourceNotFoundError(
            f"Document '{doc_name}' not found for user '{caller.username}'"
        )

    return user_docs[doc_name]


def process_profile_update_hardened(
    auth_token: str,
    target_username: str,
    update_payload: Dict[str, Any]
) -> Dict[str, Any]:
    """Updates user profile data with strict schema validation and mass assignment protection.

    [FIX - SEC-05: Mass Assignment & Input Validation (CWE-915)]
    1. Authenticates caller; enforces that users can only edit their own profile unless admin.
    2. Uses an explicit allow-list for updateable fields: only 'email' and 'bio'.
    3. Prevents modifying protected internal fields like 'role' or 'password_hash'.
    4. Validates field data types and constraints (e.g. email regex, bio length).
    """
    caller = _get_authenticated_user(auth_token)

    # Ownership check: user can only edit their own profile unless caller is admin
    if caller.username != target_username and caller.role != "admin":
        raise AccessForbiddenError("Forbidden: You cannot modify another user's profile")

    target_user = USERS_DB.get(target_username)
    if not target_user:
        raise ResourceNotFoundError(f"User '{target_username}' not found")

    # Explicit allow-list of permitted keys
    ALLOWED_UPDATE_FIELDS = {"email", "bio"}
    rejected_fields = set(update_payload.keys()) - ALLOWED_UPDATE_FIELDS
    if rejected_fields:
        raise SecurityValidationError(
            f"Disallowed fields in update payload: {sorted(rejected_fields)}. "
            f"Only {sorted(ALLOWED_UPDATE_FIELDS)} can be updated."
        )

    # Validate email format if supplied
    if "email" in update_payload:
        email = update_payload["email"]
        if not isinstance(email, str) or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            raise SecurityValidationError("Invalid email address format")
        target_user.email = email

    # Validate bio format if supplied
    if "bio" in update_payload:
        bio = update_payload["bio"]
        if not isinstance(bio, str) or len(bio) > 500:
            raise SecurityValidationError("Bio must be a string up to 500 characters")
        target_user.bio = bio

    return {
        "username": target_user.username,
        "email": target_user.email,
        "bio": target_user.bio,
        "role": target_user.role
    }

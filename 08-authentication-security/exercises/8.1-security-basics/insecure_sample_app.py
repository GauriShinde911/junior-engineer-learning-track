"""Deliberately insecure sample application for educational analysis.

WARNING: This module contains intentional, critical security vulnerabilities.
Do NOT use this code in production. It exists solely to demonstrate security
anti-patterns for vulnerability assessment in Exercise 8.1.
"""

from typing import Dict, Any, Optional

# VULNERABILITY 1: Hardcoded sensitive secret in source code
# Risk: Anyone with repository access can extract this key.
JWT_SECRET_KEY = "hardcoded_secret_key_xyz_12345"

# In-memory mock database
# VULNERABILITY 2: Storing plaintext passwords in memory/database
# Risk: A database leak exposes all user passwords instantly.
USERS_DB: Dict[str, Dict[str, Any]] = {
    "alice": {
        "password": "alice_password_123",  # Plaintext password
        "role": "user",
        "email": "alice@example.com",
        "bio": "Software developer"
    },
    "admin": {
        "password": "admin_master_password",  # Plaintext password
        "role": "admin",
        "email": "admin@example.com",
        "bio": "System administrator"
    }
}

# Mock file storage
DOCUMENTS_STORE: Dict[str, str] = {
    "alice/notes.txt": "Alice's public notes.",
    "system/secrets.txt": "CONFIDENTIAL: System payroll and configuration keys."
}


def authenticate_user_insecure(username: str, plaintext_password: str) -> bool:
    """Authenticates a user via direct plaintext string comparison.

    Vulnerabilities:
    - Compares raw plaintext password directly against stored plaintext.
    - Vulnerable to timing attacks (non-constant-time string comparison).
    """
    user = USERS_DB.get(username)
    if not user:
        return False
    # Direct equality check on plaintext
    return user["password"] == plaintext_password


def update_user_role_insecure(caller: str, target_user: str, new_role: str) -> bool:
    """Updates a user's role without verifying caller authorization.

    Vulnerability: Broken Access Control / Missing Authorization.
    Any regular user can elevate themselves or others to 'admin'.
    """
    if target_user not in USERS_DB:
        return False
    # No check whether 'caller' has administrative privileges!
    USERS_DB[target_user]["role"] = new_role
    return True


def read_document_insecure(doc_path: str) -> Optional[str]:
    """Reads a document without path sanitization or access control.

    Vulnerability: Path Traversal / Insecure Direct Object Reference (IDOR).
    Accepts arbitrary paths without verifying ownership or restricting boundaries.
    """
    # Directly looks up arbitrary keys including system files
    return DOCUMENTS_STORE.get(doc_path)


def process_profile_update_insecure(username: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates user profile data without input validation or field filtering.

    Vulnerability: Mass Assignment / Missing Input Validation.
    Allows malicious users to overwrite protected fields like 'role' or inject unexpected payloads.
    """
    user = USERS_DB.get(username)
    if not user:
        raise ValueError(f"User {username} not found")

    # Unfiltered dict update allows modifying 'role', 'password', etc.
    user.update(profile_data)
    return user

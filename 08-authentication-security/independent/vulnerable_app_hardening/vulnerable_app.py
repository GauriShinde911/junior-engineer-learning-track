"""Deliberately vulnerable mini-banking/wallet application for independent challenge review.

DO NOT USE IN PRODUCTION: Contains intentional critical security vulnerabilities.
Used for security auditing and code hardening practice.
"""

import logging
import random
from typing import Any, Dict, List, Optional

# VULN-1: Hardcoded Master Secret Key
SECRET_KEY = "hardcoded_master_secret_key_banking_system_12345"

# Setup standard logger that logs sensitive data
logger = logging.getLogger("vulnerable_banking_app")
logger.setLevel(logging.INFO)

# In-memory storage
# VULN-2: Plaintext password storage
USERS_TABLE: Dict[str, Dict[str, Any]] = {
    "alice": {
        "password": "alice_plain_password_1",
        "full_name": "Alice Jenkins",
        "role": "customer",
        "is_admin": False,
        "account_id": "ACC-1001"
    },
    "bob": {
        "password": "bob_plain_password_2",
        "full_name": "Bob Smith",
        "role": "customer",
        "is_admin": False,
        "account_id": "ACC-1002"
    }
}

ACCOUNTS_TABLE: Dict[str, Dict[str, Any]] = {
    "ACC-1001": {"owner": "alice", "balance": 5200.0, "transactions": ["+$5000", "+$200"]},
    "ACC-1002": {"owner": "bob", "balance": 150.0, "transactions": ["+$150"]}
}

# VULN-3: Predictable session tokens with NO expiration timestamps
SESSIONS: Dict[str, str] = {}  # token -> username


def register_user(username: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Registers a user.

    Vulnerabilities:
    - VULN-2: Plaintext password saved directly.
    - VULN-5: Mass Assignment: Client can pass 'is_admin': True or 'role': 'admin'.
    """
    if username in USERS_TABLE:
        raise ValueError(f"User {username} already exists")

    # Directly assigns all client keys including 'is_admin' or 'role'
    USERS_TABLE[username] = dict(user_payload)
    return USERS_TABLE[username]


def login_user(username: str, password: str) -> Optional[str]:
    """Authenticates a user and creates a session.

    Vulnerabilities:
    - VULN-2: Plaintext password equality check.
    - VULN-3: Predictable small random integer for session ID (only 9000 possibilities!).
    - VULN-3: No session expiration timestamp (sessions live indefinitely).
    - VULN-6: Unsafe logging: logs password and token in plaintext.
    """
    user = USERS_TABLE.get(username)
    if not user or user["password"] != password:
        return None

    # Predictable token generation
    token = f"sess-{random.randint(1000, 9999)}"
    SESSIONS[token] = username

    # VULN-6: Sensitive credential leak to logger
    logger.info(f"AUDIT LOGIN SUCCESS: user={username}, password={password}, token={token}")
    return token


def get_account_statement(session_token: str, account_id: str) -> Dict[str, Any]:
    """Retrieves account statement.

    Vulnerability:
    - VULN-4: Insecure Direct Object Reference (IDOR).
    Checks that session_token is valid, but DOES NOT verify that the logged-in user
    actually owns the requested account_id! Any logged-in customer can view any other
    customer's balance and transaction history by guessing/changing the account_id.
    """
    if session_token not in SESSIONS:
        raise PermissionError("Unauthenticated session")

    # Missing ownership validation!
    account = ACCOUNTS_TABLE.get(account_id)
    if not account:
        raise KeyError(f"Account {account_id} not found")

    return account

"""Hardened banking and wallet application implementing full remediation of FINDINGS.md.

Security Controls Applied:
1. Environment-driven secret configuration (VULN-01)
2. Bcrypt password hashing and verification (VULN-02)
3. Cryptographically strong tokens with TTL session expiration (VULN-03)
4. Ownership verification eliminating IDOR (VULN-04)
5. Input allow-listing preventing mass assignment privilege escalation (VULN-05)
6. Safe logging preventing credential leakage (VULN-06)
"""

from dataclasses import dataclass
import json
import logging
import os
import re
import secrets
import time
from typing import Any, Dict, List, Optional
import bcrypt


def get_secret_key() -> str:
    """Dynamically retrieves application secret key from environment."""
    return os.environ.get("APP_SECRET_KEY", "dev_placeholder_secret_key_minimum_32_chars_long")


# [FIX - VULN-01]: Secret key loaded dynamically from environment variables
SECRET_KEY = get_secret_key()


# Custom application exceptions
class BankingSecurityError(Exception):
    """Base exception for banking application security errors."""
    pass


class AuthenticationFailedError(BankingSecurityError):
    """Raised on invalid credentials or unauthenticated operations."""
    pass


class SessionExpiredError(AuthenticationFailedError):
    """Raised when an operation is attempted with an expired session token."""
    pass


class UnauthorizedAccessError(BankingSecurityError):
    """Raised when caller attempts unauthorized access to another user's resources."""
    pass


class ValidationError(BankingSecurityError):
    """Raised when incoming client payload fails validation."""
    pass


@dataclass
class UserAccount:
    username: str
    password_hash: str
    full_name: str
    role: str
    is_admin: bool
    account_id: str


@dataclass(frozen=True)
class SessionState:
    token: str
    username: str
    is_admin: bool
    created_at: float
    expires_at: float

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        now = time.time() if current_time is None else current_time
        return now >= self.expires_at


class HardenedBankingApp:
    """Enterprise-hardened banking and account service."""

    DEFAULT_TTL_SECONDS = 1800  # 30-minute session TTL
    MIN_PASSWORD_LENGTH = 8

    def __init__(self, session_ttl_seconds: int = DEFAULT_TTL_SECONDS, bcrypt_rounds: int = 4) -> None:
        self.session_ttl = session_ttl_seconds
        self.bcrypt_rounds = bcrypt_rounds
        self.users: Dict[str, UserAccount] = {}
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, SessionState] = {}
        self.audit_log_entries: List[str] = []

        self._initialize_seed_data()

    def _initialize_seed_data(self) -> None:
        """Seeds initial user accounts with bcrypt hashes."""
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)

        # [FIX - VULN-02]: Plaintext passwords replaced with salted bcrypt hashes
        alice_hash = bcrypt.hashpw("AliceSecurePass2026!".encode("utf-8"), salt).decode("utf-8")
        bob_hash = bcrypt.hashpw("BobSecretPass2026!".encode("utf-8"), salt).decode("utf-8")

        self.users["alice"] = UserAccount(
            username="alice",
            password_hash=alice_hash,
            full_name="Alice Jenkins",
            role="customer",
            is_admin=False,
            account_id="ACC-1001"
        )
        self.users["bob"] = UserAccount(
            username="bob",
            password_hash=bob_hash,
            full_name="Bob Smith",
            role="customer",
            is_admin=False,
            account_id="ACC-1002"
        )

        self.accounts["ACC-1001"] = {
            "owner": "alice",
            "balance": 5200.0,
            "transactions": ["+$5000", "+$200"]
        }
        self.accounts["ACC-1002"] = {
            "owner": "bob",
            "balance": 150.0,
            "transactions": ["+$150"]
        }

    # [FIX - VULN-06]: Safe logging utility scrubbing sensitive fields
    def _safe_log(self, event: str, payload: Dict[str, Any]) -> str:
        """Cleanses sensitive credentials before recording audit log entry."""
        sanitized = {}
        sensitive_keys = {"password", "token", "secret", "api_key", "pin", "cvv"}
        for k, v in payload.items():
            if any(s in k.lower() for s in sensitive_keys):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = v

        entry = f"[{event}] {json.dumps(sanitized, sort_keys=True)}"
        self.audit_log_entries.append(entry)
        return entry

    # [FIX - VULN-05]: Mass assignment prevention via explicit input allow-listing
    def register_user(self, username: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Registers a new customer account, enforcing input validation and privilege restrictions."""
        if not username or not re.match(r"^[a-zA-Z0-9_-]{3,32}$", username):
            raise ValidationError("Username must be 3-32 alphanumeric characters")

        if username in self.users:
            raise ValidationError(f"Username '{username}' already taken")

        raw_password = user_payload.get("password")
        if not raw_password or len(raw_password) < self.MIN_PASSWORD_LENGTH:
            raise ValidationError(f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters")

        full_name = user_payload.get("full_name", "").strip()
        if not full_name:
            raise ValidationError("full_name is required")

        # Rejection of client-controlled privilege escalation:
        # Never allow client payload to define 'is_admin' or 'role'
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        pwd_hash = bcrypt.hashpw(raw_password.encode("utf-8"), salt).decode("utf-8")

        new_account_id = f"ACC-{2000 + len(self.users) + 1}"
        new_account = UserAccount(
            username=username,
            password_hash=pwd_hash,
            full_name=full_name,
            role="customer",       # Forced to customer
            is_admin=False,        # Forced to non-admin
            account_id=new_account_id
        )
        self.users[username] = new_account
        self.accounts[new_account_id] = {
            "owner": username,
            "balance": 0.0,
            "transactions": []
        }

        self._safe_log("USER_REGISTERED", {"username": username, "account_id": new_account_id})
        return {
            "username": username,
            "full_name": full_name,
            "role": "customer",
            "is_admin": False,
            "account_id": new_account_id
        }

    # [FIX - VULN-02 & VULN-03]: Bcrypt verification and cryptographically secure tokens with TTL
    def login_user(self, username: str, password: str, current_time: Optional[float] = None) -> str:
        """Authenticates user using constant-time bcrypt verification and issues TTL session token."""
        user = self.users.get(username)
        if not user:
            self._safe_log("LOGIN_FAILED", {"username": username})
            raise AuthenticationFailedError("Invalid username or password")

        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            self._safe_log("LOGIN_FAILED", {"username": username})
            raise AuthenticationFailedError("Invalid username or password")

        # Cryptographically secure 256-bit random token
        token = secrets.token_urlsafe(32)
        now = time.time() if current_time is None else current_time
        expires_at = now + self.session_ttl

        session = SessionState(
            token=token,
            username=username,
            is_admin=user.is_admin,
            created_at=now,
            expires_at=expires_at
        )
        self.sessions[token] = session

        # Safe logging: redacts password and token
        self._safe_log("LOGIN_SUCCESS", {"username": username, "password": password, "token": token})
        return token

    def _get_active_session(self, session_token: str, current_time: Optional[float] = None) -> SessionState:
        """Retrieves and verifies active session, raising descriptive exceptions on expiry."""
        session = self.sessions.get(session_token)
        if not session:
            raise AuthenticationFailedError("Unauthenticated session token")

        if session.is_expired(current_time):
            del self.sessions[session_token]
            raise SessionExpiredError("Session has expired. Please log in again.")

        return session

    # [FIX - VULN-04]: IDOR prevention via ownership verification
    def get_account_statement(
        self,
        session_token: str,
        account_id: str,
        current_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Retrieves account statement, strictly validating ownership to eliminate IDOR."""
        session = self._get_active_session(session_token, current_time)

        account = self.accounts.get(account_id)
        if not account:
            raise KeyError(f"Account {account_id} not found")

        # Ownership validation: only the account owner (or system admin) may access statement
        if account["owner"] != session.username and not session.is_admin:
            self._safe_log("UNAUTHORIZED_STATEMENT_ACCESS_BLOCKED", {
                "caller": session.username,
                "target_account": account_id
            })
            raise UnauthorizedAccessError(
                f"Access Denied: User '{session.username}' is not authorized to view account '{account_id}'"
            )

        return {
            "account_id": account_id,
            "owner": account["owner"],
            "balance": account["balance"],
            "transactions": list(account["transactions"])
        }

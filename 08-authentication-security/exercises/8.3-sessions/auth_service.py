"""Session authentication service with cryptographically secure tokens and TTL expiry."""

from dataclasses import dataclass
from datetime import datetime, timezone
import secrets
import time
from typing import Dict, Optional, Set
import bcrypt


class AuthenticationError(Exception):
    """Raised when authentication fails or credentials are invalid."""
    pass


class SessionExpiredError(AuthenticationError):
    """Raised when an operation is attempted with an expired session."""
    pass


class InvalidSessionError(AuthenticationError):
    """Raised when an unrecognized session token is supplied."""
    pass


@dataclass(frozen=True)
class SessionRecord:
    """Immutable representation of an active user session."""
    token: str
    username: str
    role: str
    created_at: float
    expires_at: float

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """Returns True if current timestamp exceeds expiration timestamp."""
        now = time.time() if current_time is None else current_time
        return now >= self.expires_at


class AuthService:
    """Manages user authentication and time-bounded session lifecycle."""

    DEFAULT_TTL_SECONDS = 1800  # 30-minute session TTL

    def __init__(self, session_ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self.session_ttl = session_ttl_seconds
        # In-memory session store: token -> SessionRecord
        self._sessions: Dict[str, SessionRecord] = {}
        # Set of recently expired tokens for accurate error reporting
        self._expired_tokens: Set[str] = set()
        # In-memory mock user database: username -> {password_hash, role}
        self._user_credentials: Dict[str, Dict[str, str]] = {}
        self._seed_default_users()

    def _seed_default_users(self) -> None:
        """Seeds initial user accounts with bcrypt hashes for testing."""
        users = [
            ("alice", "AliceSecurePass2026!", "user"),
            ("bob", "BobSecretPass2026!", "user"),
            ("admin_carol", "CarolMasterAdmin2026!", "admin")
        ]
        salt = bcrypt.gensalt(rounds=4)  # Fast rounds for in-memory service
        for uname, pwd, role in users:
            hashed = bcrypt.hashpw(pwd.encode("utf-8"), salt).decode("utf-8")
            self._user_credentials[uname] = {
                "password_hash": hashed,
                "role": role
            }

    def register_user(self, username: str, password_hash: str, role: str = "user") -> None:
        """Registers a user into the authentication service."""
        self._user_credentials[username] = {
            "password_hash": password_hash,
            "role": role
        }

    def login(self, username: str, password: str, current_time: Optional[float] = None) -> str:
        """Authenticates credentials and issues a cryptographically secure session token."""
        user = self._user_credentials.get(username)
        if not user:
            raise AuthenticationError("Invalid username or password")

        # Verify password hash
        if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            raise AuthenticationError("Invalid username or password")

        # Generate a cryptographically unpredictable session token (256-bit entropy)
        token = secrets.token_urlsafe(32)
        now = time.time() if current_time is None else current_time
        expires_at = now + self.session_ttl

        record = SessionRecord(
            token=token,
            username=username,
            role=user["role"],
            created_at=now,
            expires_at=expires_at
        )
        self._sessions[token] = record
        return token

    def logout(self, token: str) -> bool:
        """Invalidates a session token, preventing any further use."""
        if token in self._sessions:
            del self._sessions[token]
            return True
        return False

    def is_authenticated(self, token: str, current_time: Optional[float] = None) -> bool:
        """Verifies session existence and non-expiration.

        Automatically purges session if expired.
        """
        session = self._sessions.get(token)
        if not session:
            return False

        if session.is_expired(current_time):
            del self._sessions[token]
            self._expired_tokens.add(token)
            return False

        return True

    def get_session(self, token: str, current_time: Optional[float] = None) -> SessionRecord:
        """Retrieves active session details; raises error if missing or expired."""
        session = self._sessions.get(token)
        if not session:
            if token in self._expired_tokens:
                raise SessionExpiredError("Session has expired. Please log in again.")
            raise InvalidSessionError("Invalid or missing session token.")

        if session.is_expired(current_time):
            del self._sessions[token]
            self._expired_tokens.add(token)
            raise SessionExpiredError("Session has expired. Please log in again.")

        return session

    def purge_expired_sessions(self, current_time: Optional[float] = None) -> int:
        """Removes all expired sessions from memory, returning count purged."""
        now = time.time() if current_time is None else current_time
        expired_tokens = [
            tok for tok, sess in self._sessions.items()
            if sess.is_expired(now)
        ]
        for tok in expired_tokens:
            del self._sessions[tok]
            self._expired_tokens.add(tok)
        return len(expired_tokens)

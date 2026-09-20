"""User store implementation utilizing bcrypt for secure password hashing and verification.

========================================================================================
CRITICAL SECURITY CONCEPT: HASHING VS. ENCRYPTION
========================================================================================
- HASHING (One-Way Transformation):
  Hashing transforms input data (such as a password) into a fixed-length string of bytes
  using a mathematical one-way function. It is irreversible by design—there is no key or
  mathematical formula that can decrypt the hash back into the original plaintext password.
  When verifying credentials during authentication, the system hashes the candidate password
  with the stored salt and checks if the resulting hash matches the stored hash.
  Because the plaintext is never stored, an attacker who compromises the database cannot
  directly read user passwords.

- ENCRYPTION (Two-Way Transformation):
  Encryption scrambles plaintext into ciphertext using an encryption algorithm and a secret
  cryptographic key. It is intentionally reversible: anyone with the decryption key can
  restore the original plaintext. Encryption is ideal for data confidentiality in transit
  (TLS/HTTPS) or data at rest that must later be read back by authorized services (such as
  stored customer credit cards or medical records).

PASSWORDS SHOULD NEVER BE ENCRYPTED; THEY MUST ALWAYS BE HASHED WITH SALT AND WORK FACTOR.
If passwords were encrypted, a leaked decryption key would expose every single user's password.
With modern slow hashing algorithms like bcrypt or Argon2, each password receives a unique
cryptographic salt (preventing rainbow table lookups) and a configurable cost factor
(making brute-force search prohibitively expensive for attackers).
========================================================================================
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Dict, List, Optional
import bcrypt


class UserSecurityError(Exception):
    """Base exception for user security operations."""
    pass


class UserAlreadyExistsError(UserSecurityError):
    """Raised when attempting to register a username that already exists."""
    pass


class UserNotFoundError(UserSecurityError):
    """Raised when the specified user does not exist."""
    pass


class WeakPasswordError(UserSecurityError):
    """Raised when a candidate password fails policy validation."""
    pass


class InvalidCredentialsError(UserSecurityError):
    """Raised when authentication verification fails."""
    pass


@dataclass(frozen=True)
class UserRecord:
    """Immutable representation of a stored user account.

    Notice that this model stores only the password_hash, never the raw password.
    """
    username: str
    password_hash: str
    email: str
    created_at: str


class UserStore:
    """In-memory user store using bcrypt for password hashing and authentication."""

    MIN_PASSWORD_LENGTH = 8
    DEFAULT_BCRYPT_ROUNDS = 12

    def __init__(self, bcrypt_rounds: int = DEFAULT_BCRYPT_ROUNDS) -> None:
        """Initializes an empty user store with configurable bcrypt work factor."""
        self.bcrypt_rounds = bcrypt_rounds
        self._users: Dict[str, UserRecord] = {}

    def _validate_password_strength(self, password: str) -> None:
        """Validates that a password satisfies minimum complexity requirements."""
        if not password or len(password) < self.MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(
                f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters long"
            )
        # Avoid common trivial passwords
        if password.lower() in {"password", "12345678", "admin123", "qwerty123"}:
            raise WeakPasswordError("Password is too common and easily guessed")

    def _validate_username(self, username: str) -> None:
        """Validates username format."""
        if not username or not re.match(r"^[a-zA-Z0-9_-]{3,32}$", username):
            raise ValueError(
                "Username must be 3-32 characters containing alphanumeric, underscore, or hyphen"
            )

    def register(self, username: str, password: str, email: str = "") -> UserRecord:
        """Registers a new user account with a salted bcrypt password hash.

        Never stores or logs the plaintext password.
        """
        self._validate_username(username)
        if username in self._users:
            raise UserAlreadyExistsError(f"User '{username}' already exists")

        self._validate_password_strength(password)

        # Generate a unique cryptographic salt and compute bcrypt hash
        # bcrypt handles salt generation and embedding automatically
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
        password_hash = hashed_bytes.decode("utf-8")

        record = UserRecord(
            username=username,
            password_hash=password_hash,
            email=email,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        self._users[username] = record
        return record

    def verify(self, username: str, password: str) -> bool:
        """Verifies candidate credentials against the stored bcrypt hash.

        Returns True if credentials match, False otherwise.
        Uses constant-time comparison internally via bcrypt.checkpw.
        """
        user = self._users.get(username)
        if not user:
            # Timing mitigation: execute a dummy check if user not found to balance response time
            dummy_hash = "$2b$12$e8Y7z7K7d/4E3i9mR1J6ce/6uW9EZbJq7V0nS1x2v4k6b7c8d9e0f"
            bcrypt.checkpw(password.encode("utf-8"), dummy_hash.encode("utf-8"))
            return False

        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                user.password_hash.encode("utf-8")
            )
        except Exception:
            return False

    def get_user(self, username: str) -> Optional[UserRecord]:
        """Retrieves user profile record if exists."""
        return self._users.get(username)

    def change_password(self, username: str, current_password: str, new_password: str) -> bool:
        """Verifies current password before updating to a new salted bcrypt hash."""
        if not self.verify(username, current_password):
            raise InvalidCredentialsError("Current password verification failed")

        self._validate_password_strength(new_password)
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), salt).decode("utf-8")

        existing = self._users[username]
        updated_record = UserRecord(
            username=existing.username,
            password_hash=new_hash,
            email=existing.email,
            created_at=existing.created_at
        )
        self._users[username] = updated_record
        return True

    def list_usernames(self) -> List[str]:
        """Returns all registered usernames."""
        return list(self._users.keys())

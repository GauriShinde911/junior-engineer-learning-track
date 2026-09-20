"""Tests for Exercise 8.2 password security and user store."""

import sys
from pathlib import Path
import pytest

exercises_dir = Path(__file__).resolve().parent.parent / "exercises" / "8.2-password-security"
sys.path.insert(0, str(exercises_dir))

from user_store import (
    UserStore,
    UserAlreadyExistsError,
    WeakPasswordError,
    InvalidCredentialsError
)


@pytest.fixture
def store():
    # Use rounds=4 in tests for fast execution
    return UserStore(bcrypt_rounds=4)


def test_register_and_verify_valid_credentials(store):
    """Verifies that user can register and verify credentials successfully."""
    record = store.register("bob_builder", "CorrectHorseBatteryStaple!", "bob@example.com")
    assert record.username == "bob_builder"
    assert record.email == "bob@example.com"

    # Successful verification
    assert store.verify("bob_builder", "CorrectHorseBatteryStaple!") is True
    # Failed verification
    assert store.verify("bob_builder", "WrongPassword123") is False
    # Non-existent user
    assert store.verify("unknown_user", "AnyPassword123") is False


def test_plaintext_password_is_never_stored(store):
    """Asserts that plaintext password is never accessible anywhere in the store."""
    raw_secret = "UltraSecretP@ss99"
    store.register("charlie", raw_secret, "charlie@example.com")

    record = store.get_user("charlie")
    assert record is not None
    # Password hash must not equal or contain the plaintext password
    assert record.password_hash != raw_secret
    assert raw_secret not in record.password_hash
    # Must start with bcrypt algorithm identifier ($2b$ or $2a$)
    assert record.password_hash.startswith("$2b$") or record.password_hash.startswith("$2a$")


def test_salt_uniqueness_for_identical_passwords(store):
    """Proves that two users with the exact same password produce distinct hashes due to salting."""
    common_password = "SharedSecretPass2026!"
    u1 = store.register("user_one", common_password)
    u2 = store.register("user_two", common_password)

    # Hashes must differ because bcrypt generates unique salts
    assert u1.password_hash != u2.password_hash
    # Both still verify successfully
    assert store.verify("user_one", common_password) is True
    assert store.verify("user_two", common_password) is True


def test_reject_weak_and_trivial_passwords(store):
    """Verifies that short and easily guessed passwords are rejected."""
    with pytest.raises(WeakPasswordError):
        store.register("dave", "short")  # Under 8 chars

    with pytest.raises(WeakPasswordError):
        store.register("dave", "password")  # Common dictionary word


def test_reject_duplicate_username(store):
    """Verifies duplicate registration attempt raises UserAlreadyExistsError."""
    store.register("eve_user", "ValidPassword123!")
    with pytest.raises(UserAlreadyExistsError):
        store.register("eve_user", "AnotherValidPassword456!")


def test_change_password_requires_current_credential(store):
    """Verifies password change checks old password before updating hash."""
    store.register("frank", "OldPassword123!", "frank@example.com")

    # Wrong current password fails
    with pytest.raises(InvalidCredentialsError):
        store.change_password("frank", "WrongOldPassword!", "NewPassword123!")

    # Correct current password succeeds
    success = store.change_password("frank", "OldPassword123!", "NewPassword123!")
    assert success is True
    assert store.verify("frank", "NewPassword123!") is True
    assert store.verify("frank", "OldPassword123!") is False

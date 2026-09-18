"""
exercises/6.4-mocking/repository_service.py
Service layer depending on an injected data repository.
Demonstrates dependency injection where the persistence boundary can be cleanly mocked
to verify application business logic in unit tests.
"""

from typing import Any, Dict, Optional, Protocol


class UserAlreadyExistsError(Exception):
    """Raised when registering an email that is already in use."""
    pass


class UserNotFoundError(Exception):
    """Raised when requesting operations on a non-existent user."""
    pass


class UserRepository(Protocol):
    """Repository protocol defining data access contract."""

    def find_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        ...

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        ...

    def save(self, user_data: Dict[str, Any]) -> int:
        ...

    def update(self, user_id: int, updates: Dict[str, Any]) -> bool:
        ...


class UserService:
    """Business service governing user registration, validation, and status lifecycle."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def register_user(self, username: str, email: str, role: str = "member") -> Dict[str, Any]:
        """Register a new user account if the email is not already taken.

        Args:
            username: Display username.
            email: Unique account email.
            role: Authorization tier.

        Returns:
            Dictionary representing newly created user record.

        Raises:
            ValueError: If username or email are blank or invalid.
            UserAlreadyExistsError: If a user with that email already exists in the repository.
        """
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")
        if not email or "@" not in email:
            raise ValueError("Invalid email address format")

        clean_email = email.strip().lower()
        existing = self.repository.find_by_email(clean_email)
        if existing is not None:
            raise UserAlreadyExistsError(f"User with email '{clean_email}' already exists")

        new_record = {
            "username": username.strip(),
            "email": clean_email,
            "role": role,
            "is_active": True,
        }
        new_id = self.repository.save(new_record)
        return {**new_record, "id": new_id}

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate an active user account.

        Args:
            user_id: ID of the user to deactivate.

        Returns:
            True if account was deactivated, False if it was already inactive.

        Raises:
            UserNotFoundError: If user does not exist in repository.
        """
        user = self.repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with ID {user_id} does not exist")

        if not user.get("is_active", True):
            return False

        return self.repository.update(user_id, {"is_active": False})

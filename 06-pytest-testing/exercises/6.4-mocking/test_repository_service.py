"""
exercises/6.4-mocking/test_repository_service.py
Demonstrating dependency mocking with injected repository interfaces.

WHAT SHOULD AND SHOULD NOT BE MOCKED:
- WHAT SHOULD BE MOCKED:
  The `UserRepository` dependency. In unit tests for `UserService`, the persistence engine
  (e.g., PostgreSQL, SQLite, Redis) should be mocked using a Mock object adhering to
  the repository interface. This isolates the service logic so failures indicate bugs
  in business rules (e.g. duplicate email checks, input validation), not database connection
  or SQL schema issues.
- WHAT SHOULD NOT BE MOCKED:
  Do NOT mock the `UserService` itself, its internal methods, or simple parameter objects.
  Testing a mock of the service you are trying to verify leads to tautological tests
  (testing that the mock does what you told the mock to do) without validating real behavior.
"""

from unittest.mock import Mock
import pytest

from repository_service import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)


@pytest.fixture
def mock_repo() -> Mock:
    """Fixture providing a mock implementation of the UserRepository interface."""
    repo = Mock()
    repo.find_by_id = Mock()
    repo.find_by_email = Mock()
    repo.save = Mock()
    repo.update = Mock()
    return repo


@pytest.fixture
def user_service(mock_repo: Mock) -> UserService:
    """Constructs real UserService with injected mock repository."""
    return UserService(repository=mock_repo)


def test_register_user_success(user_service: UserService, mock_repo: Mock):
    """Verify new user registration when email is unallocated."""
    # Configure mock: email lookup returns None (user does not exist yet)
    mock_repo.find_by_email.return_value = None
    mock_repo.save.return_value = 101

    created_user = user_service.register_user(
        username="carol_dev",
        email="CAROL@Example.com",
        role="developer",
    )

    # Verify repository was queried with normalized lowercase email
    mock_repo.find_by_email.assert_called_once_with("carol@example.com")

    # Verify save was called with correct sanitized record structure
    mock_repo.save.assert_called_once_with({
        "username": "carol_dev",
        "email": "carol@example.com",
        "role": "developer",
        "is_active": True,
    })

    # Assert returned aggregate includes the repository-generated ID
    assert created_user["id"] == 101
    assert created_user["username"] == "carol_dev"


def test_register_user_duplicate_email_raises_error(user_service: UserService, mock_repo: Mock):
    """Verify registration aborts with UserAlreadyExistsError if email already exists."""
    # Configure mock: email lookup returns an existing user record
    mock_repo.find_by_email.return_value = {
        "id": 45,
        "username": "existing_user",
        "email": "taken@example.com",
    }

    with pytest.raises(UserAlreadyExistsError, match="already exists"):
        user_service.register_user("new_name", "taken@example.com")

    # Critical: assert save was NEVER invoked when validation fails
    mock_repo.save.assert_not_called()


def test_register_user_invalid_input_validation(user_service: UserService, mock_repo: Mock):
    """Verify service validates empty username and email before querying repository."""
    with pytest.raises(ValueError, match="Username cannot be empty"):
        user_service.register_user("", "test@example.com")

    with pytest.raises(ValueError, match="Invalid email address"):
        user_service.register_user("valid_user", "invalid_email_format")

    # Repository was never touched
    mock_repo.find_by_email.assert_not_called()
    mock_repo.save.assert_not_called()


def test_deactivate_user_success(user_service: UserService, mock_repo: Mock):
    """Verify active user is transitioned to inactive status."""
    mock_repo.find_by_id.return_value = {"id": 12, "is_active": True}
    mock_repo.update.return_value = True

    result = user_service.deactivate_user(12)

    assert result is True
    mock_repo.find_by_id.assert_called_once_with(12)
    mock_repo.update.assert_called_once_with(12, {"is_active": False})


def test_deactivate_user_already_inactive(user_service: UserService, mock_repo: Mock):
    """Verify already inactive user returns False and update is bypassed."""
    mock_repo.find_by_id.return_value = {"id": 15, "is_active": False}

    result = user_service.deactivate_user(15)

    assert result is False
    mock_repo.update.assert_not_called()


def test_deactivate_user_not_found(user_service: UserService, mock_repo: Mock):
    """Verify non-existent user raises UserNotFoundError."""
    mock_repo.find_by_id.return_value = None

    with pytest.raises(UserNotFoundError, match="User with ID 999 does not exist"):
        user_service.deactivate_user(999)

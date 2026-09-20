"""Tests for Exercise 8.4 secrets configuration and safe logging."""

import os
import sys
from pathlib import Path
import pytest

exercises_dir = Path(__file__).resolve().parent.parent / "exercises" / "8.4-secrets-configuration"
sys.path.insert(0, str(exercises_dir))

from config import (
    load_app_config,
    AppConfig,
    MissingConfigurationError,
    InvalidConfigurationError
)
from safe_logging import (
    redact_sensitive_data,
    SafeLogger,
    demo_safe_logging
)


def test_load_app_config_success():
    """Verifies that complete environment variables load into AppConfig."""
    mock_env = {
        "APP_SECRET_KEY": "super_secure_production_secret_key_999",
        "DATABASE_URL": "sqlite:///training_db.sqlite3",
        "APP_ENVIRONMENT": "production",
        "SESSION_TTL_SECONDS": "7200",
        "LOG_LEVEL": "WARNING"
    }
    cfg = load_app_config(override_env=mock_env)
    assert cfg.app_secret_key == "super_secure_production_secret_key_999"
    assert cfg.database_url == "sqlite:///training_db.sqlite3"
    assert cfg.app_environment == "production"
    assert cfg.session_ttl_seconds == 7200
    assert cfg.log_level == "WARNING"


def test_load_app_config_missing_secret_key_raises():
    """Verifies that missing APP_SECRET_KEY raises MissingConfigurationError."""
    mock_env = {
        "DATABASE_URL": "sqlite:///app.db"
    }
    with pytest.raises(MissingConfigurationError) as exc_info:
        load_app_config(override_env=mock_env)
    assert "APP_SECRET_KEY" in str(exc_info.value)


def test_load_app_config_missing_database_url_raises():
    """Verifies that missing DATABASE_URL raises MissingConfigurationError."""
    mock_env = {
        "APP_SECRET_KEY": "valid_length_secret_key_12345"
    }
    with pytest.raises(MissingConfigurationError) as exc_info:
        load_app_config(override_env=mock_env)
    assert "DATABASE_URL" in str(exc_info.value)


def test_load_app_config_short_secret_raises_invalid_error():
    """Verifies that a secret key shorter than 16 chars is rejected for security."""
    mock_env = {
        "APP_SECRET_KEY": "too_short",
        "DATABASE_URL": "sqlite:///app.db"
    }
    with pytest.raises(InvalidConfigurationError):
        load_app_config(override_env=mock_env)


def test_load_app_config_invalid_environment_raises():
    """Verifies invalid APP_ENVIRONMENT is rejected."""
    mock_env = {
        "APP_SECRET_KEY": "valid_length_secret_key_12345",
        "DATABASE_URL": "sqlite:///app.db",
        "APP_ENVIRONMENT": "invalid_staging_sandbox"
    }
    with pytest.raises(InvalidConfigurationError):
        load_app_config(override_env=mock_env)


def test_masked_secret_representation():
    """Verifies secret key masking preserves prefix and suffix for debugging while hiding body."""
    cfg = AppConfig(
        app_secret_key="my_ultra_secret_api_key_2026",
        database_url="sqlite:///app.db"
    )
    masked = cfg.get_masked_secret()
    assert masked.startswith("my_u")
    assert masked.endswith("2026")
    assert "secret" not in masked
    assert "*" in masked


def test_redact_sensitive_nested_dictionary():
    """Verifies that redact_sensitive_data recursively scrubs credentials."""
    payload = {
        "user_id": 42,
        "username": "tester",
        "password": "ClearTextPassword123!",
        "auth_token": "token-xyz-12345",
        "nested": {
            "api_key": "sk-1234567890",
            "safe_counter": 100
        },
        "list_items": [
            {"secret_code": "code-999"},
            {"public_name": "item1"}
        ]
    }
    clean = redact_sensitive_data(payload)
    assert clean["user_id"] == 42
    assert clean["password"] == "[REDACTED]"
    assert clean["auth_token"] == "[REDACTED]"
    assert clean["nested"]["api_key"] == "[REDACTED]"
    assert clean["nested"]["safe_counter"] == 100
    assert clean["list_items"][0]["secret_code"] == "[REDACTED]"
    assert clean["list_items"][1]["public_name"] == "item1"


def test_redact_bearer_token_in_string():
    """Verifies regex string cleansing of Authorization: Bearer tokens."""
    log_line = "Incoming request headers: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.user_token_123"
    sanitized = redact_sensitive_data(log_line)
    assert "Bearer [REDACTED]" in sanitized
    assert "user_token_123" not in sanitized


def test_safe_logger_outputs_sanitized_logs():
    """Verifies SafeLogger captures cleansed entries without leaking plain passwords."""
    logger = SafeLogger("test_app")
    entry = logger.info(
        "User authenticated",
        context={"username": "alice", "password": "SecretPassword123", "token": "tok-99"}
    )
    assert "alice" in entry
    assert "SecretPassword123" not in entry
    assert "[REDACTED]" in entry


def test_demo_safe_logging_demonstration():
    """Verifies demonstration output contains raw vs sanitized payload comparisons."""
    demo = demo_safe_logging()
    raw = demo["raw_payload"]
    sanitized = demo["sanitized_payload"]

    assert raw["password"] == "MySuperSecretPassword2026!"
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["session"]["api_key"] == "[REDACTED]"

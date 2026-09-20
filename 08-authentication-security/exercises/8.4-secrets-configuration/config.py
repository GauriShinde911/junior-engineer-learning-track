"""Application configuration module using python-dotenv and environment variable validation.

Follows 12-Factor App methodology: strict separation of config from code.
Secrets and environment-dependent settings are loaded dynamically at runtime,
never hardcoded in source control.
"""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Base exception for application configuration failures."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when a mandatory environment variable is absent or empty."""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Raised when an environment variable contains an invalid value or format."""
    pass


@dataclass(frozen=True)
class AppConfig:
    """Immutable application settings container loaded from environment."""
    app_secret_key: str
    database_url: str
    app_environment: str = "development"
    session_ttl_seconds: int = 3600
    log_level: str = "INFO"

    def get_masked_secret(self) -> str:
        """Returns a masked representation of the secret key for diagnostic logs."""
        if not self.app_secret_key or len(self.app_secret_key) <= 8:
            return "********"
        prefix = self.app_secret_key[:4]
        suffix = self.app_secret_key[-4:]
        return f"{prefix}{'*' * (len(self.app_secret_key) - 8)}{suffix}"

    def to_dict(self, mask_secrets: bool = True) -> Dict[str, Any]:
        """Serializes configuration, masking sensitive keys by default."""
        return {
            "app_secret_key": self.get_masked_secret() if mask_secrets else self.app_secret_key,
            "database_url": self.database_url,
            "app_environment": self.app_environment,
            "session_ttl_seconds": self.session_ttl_seconds,
            "log_level": self.log_level
        }


def load_app_config(
    env_file_path: Optional[str] = None,
    override_env: Optional[Dict[str, str]] = None
) -> AppConfig:
    """Loads and validates application settings from environment variables.

    Args:
        env_file_path: Optional path to a specific .env file to load.
        override_env: Optional dictionary of environment variables (useful for isolated tests).

    Raises:
        MissingConfigurationError: If any required setting is missing or empty.
        InvalidConfigurationError: If any setting has an invalid value.
    """
    # 1. Load .env file if it exists and no explicit override is provided
    if override_env is None:
        if env_file_path:
            load_dotenv(dotenv_path=Path(env_file_path), override=True)
        else:
            load_dotenv(override=False)

    source = override_env if override_env is not None else os.environ

    # 2. Validate mandatory settings
    secret_key = source.get("APP_SECRET_KEY", "").strip()
    if not secret_key:
        raise MissingConfigurationError(
            "Missing mandatory configuration: 'APP_SECRET_KEY' environment variable must be set"
        )
    if len(secret_key) < 16:
        raise InvalidConfigurationError(
            "APP_SECRET_KEY must be at least 16 characters for cryptographic safety"
        )

    db_url = source.get("DATABASE_URL", "").strip()
    if not db_url:
        raise MissingConfigurationError(
            "Missing mandatory configuration: 'DATABASE_URL' environment variable must be set"
        )

    # 3. Parse and validate optional settings
    env_name = source.get("APP_ENVIRONMENT", "development").strip().lower()
    valid_environments = {"development", "staging", "production", "test"}
    if env_name not in valid_environments:
        raise InvalidConfigurationError(
            f"APP_ENVIRONMENT '{env_name}' is invalid. Must be one of: {sorted(valid_environments)}"
        )

    raw_ttl = source.get("SESSION_TTL_SECONDS", "3600").strip()
    try:
        ttl = int(raw_ttl)
        if ttl <= 0:
            raise ValueError
    except ValueError:
        raise InvalidConfigurationError(
            f"SESSION_TTL_SECONDS must be a positive integer, received: '{raw_ttl}'"
        )

    log_level = source.get("LOG_LEVEL", "INFO").strip().upper()
    valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level not in valid_log_levels:
        raise InvalidConfigurationError(
            f"LOG_LEVEL '{log_level}' is invalid. Must be one of: {sorted(valid_log_levels)}"
        )

    return AppConfig(
        app_secret_key=secret_key,
        database_url=db_url,
        app_environment=env_name,
        session_ttl_seconds=ttl,
        log_level=log_level
    )

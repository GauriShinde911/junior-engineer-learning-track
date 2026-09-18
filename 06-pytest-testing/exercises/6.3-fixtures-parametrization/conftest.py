"""
exercises/6.3-fixtures-parametrization/conftest.py
Shared reusable pytest fixtures automatically discovered across tests in this directory.
"""

from pathlib import Path
from typing import Any, Dict, List
import pytest


@pytest.fixture
def sample_app_config() -> Dict[str, Any]:
    """Provides a fresh, immutable copy of standard test configuration settings."""
    return {
        "app_env": "testing",
        "api_base_url": "https://api.internal.service.local",
        "request_timeout_seconds": 5.0,
        "max_retries": 3,
        "feature_flags": {
            "enable_rate_limiting": True,
            "enable_caching": False,
        },
    }


@pytest.fixture
def sample_user_catalog() -> List[Dict[str, Any]]:
    """Provides a deterministic list of user dictionaries representing various account tiers."""
    return [
        {"id": 1, "username": "alice_admin", "role": "admin", "is_active": True},
        {"id": 2, "username": "bob_member", "role": "member", "is_active": True},
        {"id": 3, "username": "charlie_guest", "role": "guest", "is_active": False},
    ]


@pytest.fixture
def temp_log_file(tmp_path: Path) -> Path:
    """Creates a clean temporary log file on the filesystem for file I/O tests.

    Pytest's built-in tmp_path fixture automatically provisions a unique directory
    per test invocation and handles teardown.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "service_audit.log"
    log_file.write_text("INIT_SYSTEM_LOG\n", encoding="utf-8")
    return log_file

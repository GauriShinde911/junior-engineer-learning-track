import os
import sys
from pathlib import Path
import pytest

# Add exercise directory to sys.path
EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "10.4-runtime-diagnosis"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from broken_config_env import (
    load_application_config,
    diagnose_config_environment,
    ConfigurationError,
)
from broken_network_env import (
    fetch_remote_service_data,
    diagnose_network_target,
    NetworkServiceError,
)
from broken_dependency_env import (
    load_required_engine,
    diagnose_python_environment,
    DependencyError,
)


# =====================================================================
# Configuration & File-Path Diagnostic Tests
# =====================================================================

def test_config_env_raises_when_variable_unset(monkeypatch):
    monkeypatch.delenv("APP_CONFIG_PATH", raising=False)
    with pytest.raises(ConfigurationError) as exc_info:
        load_application_config("APP_CONFIG_PATH")
    assert "unset" in str(exc_info.value).lower()

    diag = diagnose_config_environment("APP_CONFIG_PATH")
    assert diag["category"] == "ENVIRONMENT"


def test_config_env_raises_when_path_does_not_exist(monkeypatch, tmp_path):
    missing_file = tmp_path / "non_existent_settings.json"
    monkeypatch.setenv("APP_CONFIG_PATH", str(missing_file))
    
    with pytest.raises(ConfigurationError) as exc_info:
        load_application_config("APP_CONFIG_PATH")
    assert "not found" in str(exc_info.value).lower()

    diag = diagnose_config_environment("APP_CONFIG_PATH")
    assert diag["category"] == "INFRASTRUCTURE"


def test_config_env_raises_when_json_is_corrupted(monkeypatch, tmp_path):
    corrupt_file = tmp_path / "corrupt_config.json"
    corrupt_file.write_text("{invalid_json: true,", encoding="utf-8")
    monkeypatch.setenv("APP_CONFIG_PATH", str(corrupt_file))

    with pytest.raises(ConfigurationError) as exc_info:
        load_application_config("APP_CONFIG_PATH")
    assert "invalid json" in str(exc_info.value).lower()

    diag = diagnose_config_environment("APP_CONFIG_PATH")
    assert diag["category"] == "CODE_OR_DATA"


# =====================================================================
# Network & Service Diagnostic Tests
# =====================================================================

def test_network_env_raises_on_unresolvable_dns():
    unresolvable_host = "invalid-test-domain-not-real-xyz.invalid"
    with pytest.raises(NetworkServiceError) as exc_info:
        fetch_remote_service_data(unresolvable_host, 8080, timeout_sec=0.5)
    
    assert exc_info.value.error_type == "DNS_FAILURE"
    assert "dns" in str(exc_info.value).lower()

    diag = diagnose_network_target(unresolvable_host, 8080)
    assert diag["category"] == "INFRASTRUCTURE_DNS"


def test_network_env_identifies_connection_refusal():
    # Loopback address with an unused high port triggers immediate connection refusal
    diag = diagnose_network_target("127.0.0.1", 59999)
    # On most OSes without a listener on 59999, this will be connection refused or timeout
    assert diag["category"] in {"INFRASTRUCTURE_SERVICE", "INFRASTRUCTURE_NETWORK", "GENERAL_NETWORK_ERROR"}


# =====================================================================
# Dependency Diagnostic Tests
# =====================================================================

def test_dependency_env_raises_on_missing_module():
    missing_pkg = "non_existent_fake_package_987654"
    with pytest.raises(DependencyError) as exc_info:
        load_required_engine(missing_pkg)

    assert exc_info.value.error_type == "MISSING_MODULE"
    assert "not installed" in str(exc_info.value)

    diag = diagnose_python_environment(missing_pkg)
    assert diag["status"] == "MISSING"


def test_dependency_env_raises_on_incompatible_version():
    # Use an installed module (pytest) and require impossible version
    with pytest.raises(DependencyError) as exc_info:
        load_required_engine("pytest", min_version="999.0.0")

    assert exc_info.value.error_type == "INCOMPATIBLE_VERSION"
    assert "incompatible" in str(exc_info.value)

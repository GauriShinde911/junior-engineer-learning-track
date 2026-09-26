"""
broken_config_env.py - Runtime Diagnosis: Configuration & File Path Failures

Simulates environment-level configuration defects where configuration files
are missing, environment variables are unset, or paths are corrupted.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any


class ConfigurationError(Exception):
    """Raised when required configuration cannot be loaded."""
    pass


def load_application_config(env_var_name: str = "APP_CONFIG_PATH") -> Dict[str, Any]:
    """
    Attempts to read and parse the application configuration from a path specified
    in an environment variable.
    Raises ConfigurationError if the variable is unset or file does not exist.
    """
    config_path_str = os.getenv(env_var_name)
    if not config_path_str:
        raise ConfigurationError(
            f"Environment variable '{env_var_name}' is unset. Please configure application path."
        )

    config_path = Path(config_path_str)
    if not config_path.exists():
        raise ConfigurationError(
            f"Config file not found at path '{config_path_str}'. Verify mount points and working directory."
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Config file '{config_path_str}' contains invalid JSON: {exc}")


def diagnose_config_environment(env_var_name: str = "APP_CONFIG_PATH") -> Dict[str, Any]:
    """
    Diagnostic triage tool: Dissects whether failure is Environment, Infrastructure, or Code.
    """
    raw_val = os.getenv(env_var_name)
    if raw_val is None:
        return {
            "category": "ENVIRONMENT",
            "root_cause": f"Environment variable '{env_var_name}' is not set in current shell/container.",
            "remediation": f"Export {env_var_name}=/path/to/valid_config.json in environment."
        }

    target = Path(raw_val)
    if not target.exists():
        return {
            "category": "INFRASTRUCTURE",
            "root_cause": f"Path '{raw_val}' does not exist on filesystem. Possible volume mount or disk path issue.",
            "remediation": f"Ensure file exists and file permissions allow read access."
        }

    try:
        with open(target, "r", encoding="utf-8") as f:
            json.load(f)
    except Exception as e:
        return {
            "category": "CODE_OR_DATA",
            "root_cause": f"File exists but content is corrupted: {e}",
            "remediation": "Validate JSON syntax in configuration file."
        }

    return {"category": "HEALTHY", "root_cause": "None", "remediation": "Configuration valid."}


if __name__ == "__main__":
    print("Testing unconfigured environment:")
    try:
        load_application_config()
    except ConfigurationError as err:
        print("Caught expected error:", err)
        print("Diagnostic triage:", diagnose_config_environment())

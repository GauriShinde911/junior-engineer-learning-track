"""
Configuration manager for target_app.
Handles external configuration file loading from user or application directories.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "app_name": "DataAuditor",
    "version": "1.0.0",
    "log_level": "INFO",
    "max_file_size_mb": 50,
    "allowed_extensions": [".txt", ".csv", ".json", ".log", ".md"],
    "compute_hash": True,
    "log_to_file": True
}


def get_default_config_path() -> Path:
    """Return the standard platform-specific configuration path."""
    appdata = os.environ.get("APPDATA")
    if appdata and sys.platform.startswith("win"):
        base_dir = Path(appdata) / "DataAuditor"
    else:
        base_dir = Path.home() / ".data_auditor"
    return base_dir / "config.json"


def load_config(custom_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from custom path, env var, or standard user location.
    Falls back gracefully to DEFAULT_CONFIG if no file exists.
    """
    candidates = []

    if custom_path:
        candidates.append(Path(custom_path))

    env_path = os.environ.get("AUDITOR_CONFIG_PATH")
    if env_path:
        candidates.append(Path(env_path))

    # Adjacent to executable or script
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent
    else:
        exe_dir = Path(__file__).resolve().parent
    candidates.append(exe_dir / "config.json")

    # Standard per-user appdata path
    candidates.append(get_default_config_path())

    config = dict(DEFAULT_CONFIG)
    loaded_from = None

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    user_data = json.load(f)
                if isinstance(user_data, dict):
                    config.update(user_data)
                    loaded_from = candidate
                    break
            except Exception as e:
                # If explicitly provided custom path fails, propagate error
                if candidate == Path(custom_path or ""):
                    raise ValueError(f"Invalid configuration file {candidate}: {e}")

    config["_loaded_from"] = str(loaded_from) if loaded_from else "defaults"
    return config

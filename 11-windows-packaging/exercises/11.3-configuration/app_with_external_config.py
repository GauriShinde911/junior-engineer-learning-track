"""
app_with_external_config.py - Configuration Read from an External File

Demonstrates the CORRECT pattern: configuration is read at runtime from a
JSON file that lives outside the packaged bundle, in a writable, well-known
directory that survives application updates.

Correct config file locations for packaged Windows apps:
- Next to the .exe: useful for portable/per-installation configs.
- %APPDATA%\\<AppName>\\config.json: per-user, survives reinstalls.
- %PROGRAMDATA%\\<AppName>\\config.json: machine-wide, writable by admins.

This implementation checks the directory next to the exe first, then falls
back to %APPDATA%, and exits with a clear error if neither exists.
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Optional


APP_NAME = "wc-summary"
CONFIG_FILENAME = "wc_config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "max_results": 10,
    "log_level": "INFO",
    "output_dir": "",          # Empty = print to stdout; set a path to write to file
    "app_title": "Word Count Summary",
}


def find_config_file() -> Optional[Path]:
    """
    Searches for the config file in two locations (in priority order):
    1. Beside the running executable (or this script in dev mode).
    2. %APPDATA%\\wc-summary\\wc_config.json
    Returns the Path if found, or None.
    """
    # 1. Beside the exe (packaged) or beside this script (development mode)
    if getattr(sys, "frozen", False):
        # Running inside a PyInstaller bundle
        exe_dir = Path(sys.executable).parent
    else:
        exe_dir = Path(__file__).parent

    beside_exe = exe_dir / CONFIG_FILENAME
    if beside_exe.exists():
        return beside_exe

    # 2. Per-user APPDATA location
    appdata = os.getenv("APPDATA")
    if appdata:
        appdata_config = Path(appdata) / APP_NAME / CONFIG_FILENAME
        if appdata_config.exists():
            return appdata_config

    return None


def load_config() -> Dict[str, Any]:
    """
    Loads and validates the external config file.
    Returns merged config (defaults + file overrides).
    Raises SystemExit with a clear message if the file is missing.
    """
    config_path = find_config_file()

    if config_path is None:
        appdata = os.getenv("APPDATA", "%APPDATA%")
        msg = (
            f"Configuration file '{CONFIG_FILENAME}' not found.\n"
            f"Expected in one of:\n"
            f"  - Next to the executable\n"
            f"  - {appdata}\\{APP_NAME}\\{CONFIG_FILENAME}\n\n"
            f"Create the file with at minimum an empty JSON object: {{}}\n"
        )
        print(f"Error: {msg}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Error: config file '{config_path}' contains invalid JSON: {exc}", file=sys.stderr)
        sys.exit(2)

    # Merge: defaults first, then user overrides
    merged = {**DEFAULT_CONFIG, **user_config}
    return merged


def run_external_config(filepath: str) -> None:
    """
    Runs the word-count tool using runtime-loaded external configuration.
    """
    config = load_config()

    path = Path(filepath)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    words = [w.strip(".,!?;:\"'()[]").lower() for w in content.split() if w.isalpha()]
    top = Counter(words).most_common(config["max_results"])

    output_lines = [
        config["app_title"],
        f"File  : {path}",
        f"Words : {len(content.split()):,}",
        "",
        f"Top {config['max_results']} words:",
    ]
    for rank, (word, count) in enumerate(top, 1):
        output_lines.append(f"  {rank:>3}. {word:<20} {count:>6}")

    report = "\n".join(output_lines)
    output_dir = config.get("output_dir", "")

    if output_dir:
        out_path = Path(output_dir) / f"{path.stem}_summary.txt"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report written to: {out_path}")
    else:
        print(report)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: app_with_external_config.py <filepath>", file=sys.stderr)
        sys.exit(1)
    run_external_config(sys.argv[1])

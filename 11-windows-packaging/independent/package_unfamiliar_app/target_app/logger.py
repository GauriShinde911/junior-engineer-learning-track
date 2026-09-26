"""
Logging configuration for target_app.
Ensures log files are written strictly to safe user directories.
"""

import logging
import os
import sys
from pathlib import Path


def get_log_dir() -> Path:
    """Return platform-safe directory for application logs."""
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata and sys.platform.startswith("win"):
        log_dir = Path(local_appdata) / "DataAuditor" / "logs"
    else:
        log_dir = Path.home() / ".data_auditor" / "logs"
    return log_dir


def setup_logger(log_level_str: str = "INFO", log_to_file: bool = True) -> logging.Logger:
    """Configure and return root logger for DataAuditor."""
    logger = logging.getLogger("DataAuditor")
    logger.setLevel(getattr(logging, log_level_str.upper(), logging.INFO))
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_to_file:
        try:
            log_dir = get_log_dir()
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "auditor.log"
            file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
            file_fmt = logging.Formatter("%(asctime)s [%(levelname)s] (%(name)s) %(message)s")
            file_handler.setFormatter(file_fmt)
            logger.addHandler(file_handler)
            logger.debug("Logging to file: %s", log_file)
        except Exception as e:
            # Never crash if log file path has permission issues
            logger.warning("Could not initialize file logging: %s. Using console only.", e)

    return logger

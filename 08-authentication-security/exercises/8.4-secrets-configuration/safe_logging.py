"""Safe logging utility preventing sensitive credential leaks in log outputs (CWE-532)."""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Set, Union


# Sensitive keys that must be scrubbed from structured dictionaries
SENSITIVE_KEY_SUBSTRINGS: Set[str] = {
    "password",
    "passwd",
    "pwd",
    "token",
    "secret",
    "api_key",
    "apikey",
    "authorization",
    "auth_header",
    "credit_card",
    "card_number",
    "cvv",
    "ssn",
    "private_key"
}

# Regex pattern to scrub Authorization: Bearer <token> from raw strings
BEARER_TOKEN_PATTERN = re.compile(r"(?i)(bearer\s+)[a-zA-Z0-9_\-\.]{10,}")
# Regex pattern to scrub connection strings containing user:pass@host
CONN_STRING_PATTERN = re.compile(r"(://[^:]+:)([^@]+)(@)")


def is_sensitive_key(key: str) -> bool:
    """Checks if a dictionary key name indicates sensitive credential data."""
    cleaned = key.lower().replace("-", "_").strip()
    return any(sens in cleaned for sens in SENSITIVE_KEY_SUBSTRINGS)


def redact_sensitive_data(data: Any, mask: str = "[REDACTED]") -> Any:
    """Recursively traverses and scrubs sensitive values from data structures."""
    if isinstance(data, dict):
        scrubbed_dict: Dict[str, Any] = {}
        for k, v in data.items():
            if isinstance(k, str) and is_sensitive_key(k):
                scrubbed_dict[k] = mask
            else:
                scrubbed_dict[k] = redact_sensitive_data(v, mask=mask)
        return scrubbed_dict

    elif isinstance(data, list):
        return [redact_sensitive_data(item, mask=mask) for item in data]

    elif isinstance(data, tuple):
        return tuple(redact_sensitive_data(item, mask=mask) for item in data)

    elif isinstance(data, str):
        # Redact bearer tokens in strings
        redacted_str = BEARER_TOKEN_PATTERN.sub(r"\1" + mask, data)
        # Redact passwords in connection URLs
        redacted_str = CONN_STRING_PATTERN.sub(r"\1" + mask + r"\3", redacted_str)
        return redacted_str

    return data


class SafeLogRecordFormatter(logging.Formatter):
    """Custom logging Formatter that automatically sanitizes log arguments and messages."""

    def format(self, record: logging.LogRecord) -> str:
        # Sanitize message string
        if isinstance(record.msg, str):
            record.msg = redact_sensitive_data(record.msg)
        elif isinstance(record.msg, (dict, list)):
            record.msg = json.dumps(redact_sensitive_data(record.msg))

        # Sanitize tuple args if provided
        if record.args:
            record.args = redact_sensitive_data(record.args)

        return super().format(record)


class SafeLogger:
    """Application logger wrapper ensuring all logged parameters are sanitized."""

    def __init__(self, name: str = "safe_logger") -> None:
        self.logger = logging.getLogger(name)
        self._captured_logs: List[str] = []

    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Sanitizes message and context payload, formats entry, and stores record."""
        sanitized_msg = redact_sensitive_data(message)
        sanitized_ctx = redact_sensitive_data(context) if context else None

        if sanitized_ctx:
            entry = f"[{level.upper()}] {sanitized_msg} | payload={json.dumps(sanitized_ctx, sort_keys=True)}"
        else:
            entry = f"[{level.upper()}] {sanitized_msg}"

        self._captured_logs.append(entry)
        return entry

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        return self.log("INFO", message, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        return self.log("WARNING", message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        return self.log("ERROR", message, context)

    def get_logs(self) -> List[str]:
        return list(self._captured_logs)


def demo_safe_logging() -> Dict[str, Any]:
    """Demonstrates how sensitive fields are stripped prior to logging."""
    raw_incoming_payload = {
        "event": "user_login_attempt",
        "username": "developer_sam",
        "password": "MySuperSecretPassword2026!",
        "auth_token": "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.fake_token",
        "session": {
            "api_key": "sk_live_9876543210abcdef",
            "device_id": "laptop-mac-01"
        }
    }

    sanitized = redact_sensitive_data(raw_incoming_payload)
    return {
        "raw_payload": raw_incoming_payload,
        "sanitized_payload": sanitized
    }

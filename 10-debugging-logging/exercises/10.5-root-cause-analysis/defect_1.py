"""
defect_1.py - Defect Scenario 1: Timezone Awareness Mismatch

Symptom:
Auth token expiration check intermittently fails or falsely marks active tokens as expired
when running across different server timezones.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any


def is_token_expired_buggy(token_payload: Dict[str, Any]) -> bool:
    """
    BUGGY IMPLEMENTATION:
    Compares local machine time (datetime.now()) directly with UTC timestamp.
    In timezones ahead of UTC, tokens appear expired instantly.
    In timezones behind UTC, expired tokens remain active for hours.
    """
    expires_at_utc = token_payload["expires_at"]  # UTC aware
    # BUG: datetime.now() produces timezone-naive local time!
    # Comparing aware with naive will either raise TypeError or compare mismatched offsets.
    now_naive = datetime.now()
    try:
        return now_naive >= expires_at_utc
    except TypeError:
        # Developers often add quick band-aids like stripping tzinfo without converting!
        return now_naive >= expires_at_utc.replace(tzinfo=None)


def is_token_expired_fixed(token_payload: Dict[str, Any]) -> bool:
    """
    CORRECTED IMPLEMENTATION:
    Always normalizes both current time and token timestamp to UTC-aware datetimes.
    """
    expires_at = token_payload["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = expires_at.astimezone(timezone.utc)

    now_utc = datetime.now(timezone.utc)
    return now_utc >= expires_at


if __name__ == "__main__":
    # Token valid for 10 minutes in UTC
    valid_token = {"expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)}
    print("Fixed check (should be False):", is_token_expired_fixed(valid_token))

"""
exercises/7.4-error-handling/failure_simulation.py
Demonstrates and exercises each failure mode handled by resilient_client.py:
  1. Timeout
  2. Connection refused / DNS failure
  3. Rate limit (HTTP 429) with automatic backoff retry
  4. Server error (HTTP 500)
  5. Client error (HTTP 404 / 401)

Runs without hitting real network endpoints by using unittest.mock to simulate
each failure scenario deterministically.
"""

from pathlib import Path
from typing import Any, List
from unittest.mock import Mock, patch
import sys

EXERCISE_DIR = Path(__file__).resolve().parent
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

API_CLIENT_DIR = EXERCISE_DIR.parent / "7.2-python-http-client"
if str(API_CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(API_CLIENT_DIR))

import requests
from api_client import ClientError, ConnectionFailureError, RequestTimeoutError, ServerError
from resilient_client import ResilientClient, UserFacingError

DEMO_URL = "https://api.demo-service.example.com/v1"

sleep_calls: List[float] = []


def _record_sleep(seconds: float) -> None:
    """Captures sleep durations instead of actually sleeping."""
    sleep_calls.append(seconds)


# ---------------------------------------------------------------------------
# Failure Mode 1: Request Timeout
# ---------------------------------------------------------------------------

def simulate_timeout() -> None:
    print("\n=== FAILURE MODE 1: Request Timeout ===")
    client = ResilientClient(
        base_url=DEMO_URL,
        max_retries=2,
        backoff_base=0.1,
        sleep_fn=_record_sleep,
    )

    with patch.object(
        client._client.session,
        "request",
        side_effect=requests.exceptions.Timeout("Read timeout after 10s"),
    ):
        try:
            client.get("/health", context="checking service health")
        except UserFacingError as err:
            print(f"[User-Safe Error] {err.user_message}")
            print(f"[Technical Detail] {err.technical_detail}")
            print(f"[Retry Sleep Calls] {sleep_calls} seconds ({len(sleep_calls)} retries before giving up)")


# ---------------------------------------------------------------------------
# Failure Mode 2: Connection Refused
# ---------------------------------------------------------------------------

def simulate_connection_failure() -> None:
    print("\n=== FAILURE MODE 2: Connection Failure ===")
    client = ResilientClient(
        base_url=DEMO_URL,
        max_retries=1,
        backoff_base=0.1,
        sleep_fn=_record_sleep,
    )

    with patch.object(
        client._client.session,
        "request",
        side_effect=requests.exceptions.ConnectionError("Connection refused: [Errno 111]"),
    ):
        try:
            client.post("/orders", json_data={"item_id": 99}, context="placing order")
        except UserFacingError as err:
            print(f"[User-Safe Error] {err.user_message}")
            print(f"[Technical Detail] {err.technical_detail}")


# ---------------------------------------------------------------------------
# Failure Mode 3: HTTP 429 Rate Limit
# ---------------------------------------------------------------------------

def simulate_rate_limit() -> None:
    print("\n=== FAILURE MODE 3: HTTP 429 Rate Limit ===")
    client = ResilientClient(
        base_url=DEMO_URL,
        max_retries=2,
        backoff_base=0.1,
        sleep_fn=_record_sleep,
    )

    mock_429 = Mock()
    mock_429.status_code = 429
    mock_429.content = b'{"error": "Too Many Requests"}'
    mock_429.json.return_value = {"error": "Too Many Requests"}
    mock_429.text = "Too Many Requests"

    with patch.object(client._client.session, "request", return_value=mock_429):
        try:
            client.get("/products", context="loading product catalog")
        except UserFacingError as err:
            print(f"[User-Safe Error] {err.user_message}")


# ---------------------------------------------------------------------------
# Failure Mode 4: HTTP 500 Server Error
# ---------------------------------------------------------------------------

def simulate_server_error() -> None:
    print("\n=== FAILURE MODE 4: HTTP 500 Internal Server Error ===")
    client = ResilientClient(
        base_url=DEMO_URL,
        max_retries=2,
        backoff_base=0.1,
        sleep_fn=_record_sleep,
    )

    mock_500 = Mock()
    mock_500.status_code = 500
    mock_500.content = b"Internal Server Error"
    mock_500.json.side_effect = ValueError("Not JSON")
    mock_500.text = "Internal Server Error"

    with patch.object(client._client.session, "request", return_value=mock_500):
        try:
            client.get("/users", context="loading users list")
        except UserFacingError as err:
            print(f"[User-Safe Error] {err.user_message}")
            print(f"[Technical Detail] {err.technical_detail}")


# ---------------------------------------------------------------------------
# Failure Mode 5: HTTP 401 Authentication Failure (non-retryable)
# ---------------------------------------------------------------------------

def simulate_auth_failure() -> None:
    print("\n=== FAILURE MODE 5: HTTP 401 Unauthorized (non-retryable) ===")
    client = ResilientClient(base_url=DEMO_URL, max_retries=3, sleep_fn=_record_sleep)

    retries_before_clear = len(sleep_calls)

    mock_401 = Mock()
    mock_401.status_code = 401
    mock_401.content = b'{"error": "Unauthorized"}'
    mock_401.json.return_value = {"error": "Unauthorized"}
    mock_401.text = "Unauthorized"

    with patch.object(client._client.session, "request", return_value=mock_401):
        try:
            client.get("/admin/users", context="accessing admin panel")
        except UserFacingError as err:
            print(f"[User-Safe Error] {err.user_message}")
            retries_after = len(sleep_calls) - retries_before_clear
            print(f"[Retry Count] {retries_after} (expected 0 — 401 is not retried)")


# ---------------------------------------------------------------------------
# Success scenario — no error
# ---------------------------------------------------------------------------

def simulate_success() -> None:
    print("\n=== SUCCESS SCENARIO: Normal Response ===")
    client = ResilientClient(base_url=DEMO_URL, sleep_fn=_record_sleep)

    mock_200 = Mock()
    mock_200.status_code = 200
    mock_200.content = b'{"id": 1, "status": "ok"}'
    mock_200.json.return_value = {"id": 1, "status": "ok"}

    with patch.object(client._client.session, "request", return_value=mock_200):
        result = client.get("/status", context="checking status")
        print(f"[Success] Response: {result}")


if __name__ == "__main__":
    simulate_success()
    simulate_timeout()
    simulate_connection_failure()
    simulate_rate_limit()
    simulate_server_error()
    simulate_auth_failure()
    print("\nAll failure simulations completed.")

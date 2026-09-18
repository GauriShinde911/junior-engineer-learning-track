"""
tests/test_7_4_error_handling.py
Tests for ResilientClient error handling and retry logic.
Uses pytest-mock / unittest.mock — no real network calls.
"""

from pathlib import Path
from typing import List
from unittest.mock import Mock, patch
import sys

import pytest
import requests

EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "7.4-error-handling"
API_CLIENT_DIR = Path(__file__).resolve().parent.parent / "exercises" / "7.2-python-http-client"

for d in (str(EXERCISE_DIR), str(API_CLIENT_DIR)):
    if d not in sys.path:
        sys.path.insert(0, d)

from api_client import ClientError, ConnectionFailureError, RequestTimeoutError, ServerError
from resilient_client import RateLimitError, ResilientClient, UserFacingError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_response(status_code: int, body: dict | str = "") -> Mock:
    m = Mock()
    m.status_code = status_code
    if isinstance(body, dict):
        m.json.return_value = body
        import json
        m.content = json.dumps(body).encode()
        m.text = json.dumps(body)
    else:
        m.json.side_effect = ValueError("not json")
        m.content = body.encode() if body else b""
        m.text = body
    return m


def _make_client(max_retries: int = 2, backoff_base: float = 0.001) -> tuple:
    """Return (client, recorded_sleeps_list)."""
    sleeps: List[float] = []
    client = ResilientClient(
        base_url="https://test.example.com",
        max_retries=max_retries,
        backoff_base=backoff_base,
        sleep_fn=sleeps.append,
    )
    return client, sleeps


# ---------------------------------------------------------------------------
# Retry Behaviour Tests
# ---------------------------------------------------------------------------

class TestRetryOnTransientErrors:

    def test_timeout_is_retried_then_raises_user_error(self):
        client, sleeps = _make_client(max_retries=2)
        with patch.object(
            client._client.session,
            "request",
            side_effect=requests.exceptions.Timeout("timed out"),
        ):
            with pytest.raises(UserFacingError) as exc_info:
                client.get("/data")
        assert "timed out" in exc_info.value.user_message.lower() or "try again" in exc_info.value.user_message.lower()
        assert len(sleeps) == 2, "Should sleep between each retry (2 retries = 2 sleeps)"

    def test_connection_error_is_retried_then_raises_user_error(self):
        client, sleeps = _make_client(max_retries=3)
        with patch.object(
            client._client.session,
            "request",
            side_effect=requests.exceptions.ConnectionError("connection refused"),
        ):
            with pytest.raises(UserFacingError) as exc_info:
                client.post("/submit", json_data={})
        assert "network" in exc_info.value.user_message.lower() or "reach" in exc_info.value.user_message.lower()
        assert len(sleeps) == 3

    def test_server_error_500_is_retried(self):
        client, sleeps = _make_client(max_retries=2)
        mock_resp = _make_mock_response(500, "Server blew up")
        with patch.object(client._client.session, "request", return_value=mock_resp):
            with pytest.raises(UserFacingError):
                client.get("/items")
        assert len(sleeps) == 2

    def test_rate_limit_429_is_retried_with_backoff(self):
        client, sleeps = _make_client(max_retries=2)
        mock_429 = _make_mock_response(429, {"error": "Too Many Requests"})
        with patch.object(client._client.session, "request", return_value=mock_429):
            with pytest.raises(UserFacingError) as exc_info:
                client.get("/search")
        assert "slow down" in exc_info.value.user_message.lower() or "too many" in exc_info.value.user_message.lower()
        assert len(sleeps) == 2


class TestNoRetryOnClientErrors:

    def test_401_not_retried(self):
        client, sleeps = _make_client(max_retries=3)
        mock_resp = _make_mock_response(401, {"error": "Unauthorized"})
        with patch.object(client._client.session, "request", return_value=mock_resp):
            with pytest.raises(UserFacingError) as exc_info:
                client.get("/admin")
        assert "authentication" in exc_info.value.user_message.lower() or "credential" in exc_info.value.user_message.lower()
        assert len(sleeps) == 0, "4xx errors must not trigger any retries"

    def test_403_not_retried(self):
        client, sleeps = _make_client(max_retries=3)
        mock_resp = _make_mock_response(403, {"error": "Forbidden"})
        with patch.object(client._client.session, "request", return_value=mock_resp):
            with pytest.raises(UserFacingError):
                client.delete("/resource/1")
        assert len(sleeps) == 0

    def test_404_not_retried(self):
        client, sleeps = _make_client(max_retries=3)
        mock_resp = _make_mock_response(404, {"error": "Not found"})
        with patch.object(client._client.session, "request", return_value=mock_resp):
            with pytest.raises(UserFacingError) as exc_info:
                client.get("/missing")
        assert "not found" in exc_info.value.user_message.lower()
        assert len(sleeps) == 0


# ---------------------------------------------------------------------------
# Backoff Tests
# ---------------------------------------------------------------------------

class TestBackoffTiming:

    def test_exponential_backoff_values(self):
        client, _ = _make_client()
        assert client._backoff_seconds(0) == pytest.approx(0.001)
        assert client._backoff_seconds(1) == pytest.approx(0.002)
        assert client._backoff_seconds(2) == pytest.approx(0.004)

    def test_backoff_is_capped_at_maximum(self):
        sleeps: List[float] = []
        client = ResilientClient(
            base_url="https://test.example.com",
            max_retries=10,
            backoff_base=5.0,
            backoff_max=10.0,
            sleep_fn=sleeps.append,
        )
        with patch.object(
            client._client.session,
            "request",
            side_effect=requests.exceptions.Timeout("t/o"),
        ):
            with pytest.raises(UserFacingError):
                client.get("/x")
        assert all(s <= 10.0 for s in sleeps), "No sleep should exceed backoff_max=10s"

    def test_success_on_third_attempt_after_two_timeouts(self):
        """Client should succeed when a transient failure clears after 2 retries."""
        client, sleeps = _make_client(max_retries=3)
        timeout_exc = requests.exceptions.Timeout("temp timeout")
        ok_response = _make_mock_response(200, {"ok": True})

        side_effects = [timeout_exc, timeout_exc, ok_response]
        with patch.object(client._client.session, "request", side_effect=side_effects):
            result = client.get("/flaky")

        assert result == {"ok": True}
        assert len(sleeps) == 2, "2 retries → 2 sleeps"


# ---------------------------------------------------------------------------
# UserFacingError message quality
# ---------------------------------------------------------------------------

class TestUserFacingErrorMessages:

    def test_technical_detail_is_preserved_in_exception(self):
        client, _ = _make_client()
        with patch.object(
            client._client.session,
            "request",
            side_effect=requests.exceptions.Timeout("raw internal timeout msg"),
        ):
            with pytest.raises(UserFacingError) as exc_info:
                client.get("/health")
        assert exc_info.value.technical_detail != "", "Technical detail must not be empty"

    def test_user_message_does_not_contain_stack_trace_keywords(self):
        client, _ = _make_client()
        with patch.object(
            client._client.session,
            "request",
            side_effect=requests.exceptions.Timeout(),
        ):
            with pytest.raises(UserFacingError) as exc_info:
                client.get("/health")
        forbidden_words = ["traceback", "exception", "errno", "socket", "urllib3", "requests"]
        msg_lower = exc_info.value.user_message.lower()
        for word in forbidden_words:
            assert word not in msg_lower, f"User message must not contain '{word}'"

    def test_success_returns_data_not_user_error(self):
        client, _ = _make_client()
        ok = _make_mock_response(200, {"result": "data"})
        with patch.object(client._client.session, "request", return_value=ok):
            result = client.get("/ok")
        assert result == {"result": "data"}

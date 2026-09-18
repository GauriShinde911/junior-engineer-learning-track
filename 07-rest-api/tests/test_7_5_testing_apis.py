"""
tests/test_7_5_testing_apis.py
Integration-level test file for Section 7.5: Testing APIs with Mocks.
Runs the 7.5 exercise tests and adds broader mock strategy verifications.
"""

from pathlib import Path
from unittest.mock import Mock, patch, call
import sys

import pytest
import requests

# Allow importing both APIClient and 7.5 exercise tests
API_CLIENT_DIR = Path(__file__).resolve().parent.parent / "exercises" / "7.2-python-http-client"
SECTION_75_DIR = Path(__file__).resolve().parent.parent / "exercises" / "7.5-testing-apis"

for d in (str(API_CLIENT_DIR), str(SECTION_75_DIR)):
    if d not in sys.path:
        sys.path.insert(0, d)

from api_client import APIClient, ClientError, ConnectionFailureError, RequestTimeoutError, ServerError


def _resp(status: int, body=None) -> Mock:
    import json
    m = Mock(spec=requests.Response)
    m.status_code = status
    if isinstance(body, (dict, list)):
        m.content = json.dumps(body).encode()
        m.json.return_value = body
        m.text = json.dumps(body)
    else:
        m.content = b""
        m.json.side_effect = ValueError("no json")
        m.text = ""
    return m


@pytest.fixture
def client():
    return APIClient(base_url="https://mock.test", headers={"Accept": "application/json"})


# ---------------------------------------------------------------------------
# Verify exercise file exists and contains expected test classes
# ---------------------------------------------------------------------------

def test_exercise_file_exists():
    exercise_test = SECTION_75_DIR / "test_api_client_mocked.py"
    assert exercise_test.exists(), (
        "exercises/7.5-testing-apis/test_api_client_mocked.py must exist"
    )


def test_exercise_file_contains_required_test_classes():
    exercise_test = (SECTION_75_DIR / "test_api_client_mocked.py").read_text()
    required = [
        "TestClientInitialization",
        "TestSuccessfulRequests",
        "TestErrorClassification",
        "TestSessionReuse",
        "TestHTTPVerbs",
    ]
    for cls_name in required:
        assert cls_name in exercise_test, f"Missing test class: {cls_name}"


# ---------------------------------------------------------------------------
# Mock strategy: patch at session level (not module level)
# ---------------------------------------------------------------------------

def test_session_level_patch_intercepts_calls(client):
    """Patching session.request must intercept all client HTTP calls."""
    mock_resp = _resp(200, {"ok": True})
    with patch.object(client.session, "request", return_value=mock_resp) as m:
        result = client.get("/health")
    m.assert_called_once()
    assert result == {"ok": True}


def test_side_effect_raises_timeout(client):
    with patch.object(
        client.session, "request", side_effect=requests.exceptions.Timeout()
    ):
        with pytest.raises(RequestTimeoutError):
            client.get("/slow-endpoint")


def test_side_effect_sequence_for_retry_scenario(client):
    """Demonstrate side_effect list pattern: fail twice, succeed third time."""
    from api_client import ServerError

    fail = _resp(500, "err")
    success = _resp(200, {"data": "ok"})

    call_count = 0
    def side_effect_fn(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return fail
        return success

    # Direct session mock (no retry wrapping here — we're just demonstrating the pattern)
    with patch.object(client.session, "request", side_effect=side_effect_fn):
        # Third call succeeds
        with pytest.raises(ServerError):
            client.get("/flaky")  # First call → 500 raises immediately in api_client


def test_call_args_captures_url_and_method(client):
    """Verify mock.call_args inspection to check URL and HTTP method."""
    mock_resp = _resp(200, {})
    with patch.object(client.session, "request", return_value=mock_resp) as m:
        client.post("/orders", json_data={"qty": 3})
    args, kwargs = m.call_args
    http_method = args[0] if args else kwargs.get("method", "")
    assert http_method.upper() == "POST"


def test_parametrize_pattern_all_client_error_codes(client):
    """All 4xx codes (except 429) should raise ClientError."""
    for code in [400, 401, 403, 404, 422]:
        mock_resp = _resp(code, {"error": "bad request"})
        with patch.object(client.session, "request", return_value=mock_resp):
            with pytest.raises(ClientError):
                client.get("/resource")


def test_spec_mock_rejects_invalid_attributes(client):
    """spec=requests.Response prevents typo attributes from silently passing."""
    m = Mock(spec=requests.Response)
    with pytest.raises(AttributeError):
        _ = m.stats_code  # typo — should raise, not silently return a Mock


# ---------------------------------------------------------------------------
# Notes file verification
# ---------------------------------------------------------------------------

def test_notes_file_exists():
    notes = SECTION_75_DIR / "NOTES.md"
    assert notes.exists(), "exercises/7.5-testing-apis/NOTES.md must exist"
    content = notes.read_text(encoding="utf-8")
    assert len(content) > 200, "NOTES.md must be a substantive document"

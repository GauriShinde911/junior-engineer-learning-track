"""
exercises/7.5-testing-apis/test_api_client_mocked.py
Comprehensive mock-based tests for api_client.APIClient (7.2).
Covers: happy paths, error classification, session reuse, headers, params,
JSON serialization, and all HTTP verbs (GET, POST, PUT, DELETE).
Uses only unittest.mock — no real network calls.
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock, call, patch
import sys

import pytest
import requests

EXERCISE_DIR = Path(__file__).resolve().parent.parent / "7.2-python-http-client"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from api_client import (
    APIClient,
    APIClientError,
    ClientError,
    ConnectionFailureError,
    HTTPStatusError,
    RequestTimeoutError,
    ServerError,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client() -> APIClient:
    return APIClient(
        base_url="https://api.example.com",
        headers={"X-App-Id": "test"},
    )


def _mock_response(status_code: int, body: Any = None, headers: dict | None = None) -> Mock:
    """Build a minimal mock requests.Response."""
    m = Mock(spec=requests.Response)
    m.status_code = status_code
    m.headers = headers or {}
    if body is None:
        m.content = b""
        m.json.side_effect = ValueError("No content")
        m.text = ""
    elif isinstance(body, dict) or isinstance(body, list):
        import json
        raw = json.dumps(body).encode()
        m.content = raw
        m.json.return_value = body
        m.text = raw.decode()
    else:
        m.content = str(body).encode()
        m.json.side_effect = ValueError("Not JSON")
        m.text = str(body)
    return m


# ---------------------------------------------------------------------------
# Session construction tests
# ---------------------------------------------------------------------------

class TestClientInitialization:

    def test_client_uses_requests_session(self, client: APIClient):
        assert hasattr(client, "session"), "APIClient must expose a .session attribute"
        assert isinstance(client.session, requests.Session)

    def test_custom_headers_are_merged_into_session(self, client: APIClient):
        assert client.session.headers.get("X-App-Id") == "test"

    def test_base_url_is_stored(self, client: APIClient):
        assert client.base_url == "https://api.example.com"


# ---------------------------------------------------------------------------
# Successful HTTP requests
# ---------------------------------------------------------------------------

class TestSuccessfulRequests:

    def test_get_returns_json_body(self, client: APIClient):
        mock_resp = _mock_response(200, {"id": 1, "name": "Widget"})
        with patch.object(client.session, "request", return_value=mock_resp):
            result = client.get("/products/1")
        assert result == {"id": 1, "name": "Widget"}

    def test_get_sends_correct_url(self, client: APIClient):
        mock_resp = _mock_response(200, {})
        with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
            client.get("/items")
        args, kwargs = mock_req.call_args
        url = args[1] if args else kwargs.get("url", "")
        assert url.endswith("/items") or "items" in url

    def test_get_passes_query_params(self, client: APIClient):
        mock_resp = _mock_response(200, [])
        with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
            client.get("/search", params={"q": "hello", "page": 2})
        _, kwargs = mock_req.call_args
        assert "params" in kwargs
        assert kwargs["params"]["q"] == "hello"

    def test_post_sends_json_body(self, client: APIClient):
        payload = {"name": "New Item", "price": 9.99}
        mock_resp = _mock_response(201, {"id": 42, **payload})
        with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
            result = client.post("/items", json_data=payload)
        _, kwargs = mock_req.call_args
        assert kwargs.get("json") == payload
        assert result["id"] == 42

    def test_put_sends_json_body(self, client: APIClient):
        payload = {"status": "archived"}
        mock_resp = _mock_response(200, {"id": 7, **payload})
        with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
            result = client.put("/items/7", json_data=payload)
        _, kwargs = mock_req.call_args
        assert kwargs.get("json") == payload
        assert result["status"] == "archived"

    def test_delete_succeeds_with_204_no_content(self, client: APIClient):
        mock_resp = _mock_response(204)
        with patch.object(client.session, "request", return_value=mock_resp):
            result = client.delete("/items/7")
        # 204 responses have no body; client may return None or empty dict
        assert result is None or result == {} or result == ""

    def test_get_list_returns_list(self, client: APIClient):
        items = [{"id": 1}, {"id": 2}]
        mock_resp = _mock_response(200, items)
        with patch.object(client.session, "request", return_value=mock_resp):
            result = client.get("/items")
        assert isinstance(result, list)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Error classification tests
# ---------------------------------------------------------------------------

class TestErrorClassification:

    @pytest.mark.parametrize("status_code", [400, 401, 403, 404, 422])
    def test_client_errors_raise_client_error(self, client: APIClient, status_code: int):
        mock_resp = _mock_response(status_code, {"error": "bad"})
        with patch.object(client.session, "request", return_value=mock_resp):
            with pytest.raises(ClientError) as exc_info:
                client.get("/resource")
        assert exc_info.value.status_code == status_code
        assert isinstance(exc_info.value, HTTPStatusError)

    @pytest.mark.parametrize("status_code", [500, 502, 503, 504])
    def test_server_errors_raise_server_error(self, client: APIClient, status_code: int):
        mock_resp = _mock_response(status_code, "Internal Server Error")
        with patch.object(client.session, "request", return_value=mock_resp):
            with pytest.raises(ServerError) as exc_info:
                client.get("/resource")
        assert exc_info.value.status_code == status_code
        assert isinstance(exc_info.value, HTTPStatusError)

    def test_timeout_raises_request_timeout_error(self, client: APIClient):
        with patch.object(
            client.session,
            "request",
            side_effect=requests.exceptions.Timeout("timed out"),
        ):
            with pytest.raises(RequestTimeoutError):
                client.get("/slow")

    def test_connection_error_raises_connection_failure_error(self, client: APIClient):
        with patch.object(
            client.session,
            "request",
            side_effect=requests.exceptions.ConnectionError("refused"),
        ):
            with pytest.raises(ConnectionFailureError):
                client.get("/down")

    def test_all_errors_are_api_client_error_subclasses(self, client: APIClient):
        for exc_class in (ClientError, ServerError, RequestTimeoutError, ConnectionFailureError):
            assert issubclass(exc_class, APIClientError)


# ---------------------------------------------------------------------------
# Session reuse tests
# ---------------------------------------------------------------------------

class TestSessionReuse:

    def test_same_session_used_across_multiple_requests(self, client: APIClient):
        """APIClient must reuse its session for connection pooling."""
        mock_resp = _mock_response(200, {})
        with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
            client.get("/a")
            client.get("/b")
            client.post("/c", json_data={})
        assert mock_req.call_count == 3

    def test_session_is_not_recreated_between_calls(self, client: APIClient):
        session_before = client.session
        mock_resp = _mock_response(200, {})
        with patch.object(client.session, "request", return_value=mock_resp):
            client.get("/x")
            client.get("/y")
        assert client.session is session_before


# ---------------------------------------------------------------------------
# HTTP verb mapping tests
# ---------------------------------------------------------------------------

class TestHTTPVerbs:

    @pytest.mark.parametrize("method,verb", [
        ("get", "GET"),
        ("post", "POST"),
        ("put", "PUT"),
        ("delete", "DELETE"),
    ])
    def test_correct_http_verb_is_used(self, client: APIClient, method: str, verb: str):
        mock_resp = _mock_response(200, {})
        with patch.object(client.session, "request", return_value=mock_resp) as mock_req:
            fn = getattr(client, method)
            fn("/endpoint")
        args, _ = mock_req.call_args
        http_method = args[0] if args else mock_req.call_args.kwargs.get("method", "")
        assert http_method.upper() == verb

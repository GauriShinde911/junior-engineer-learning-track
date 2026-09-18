"""
tests/test_7_2_python_http_client.py
Unit tests for the 7.2 APIClient module.
Verifies all REST verbs, timeout enforcement, error mapping, and JSON handling using mocks.
"""

from pathlib import Path
from unittest.mock import Mock
import sys
import pytest
import requests

EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "7.2-python-http-client"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from api_client import (
    APIClient,
    ClientError,
    ConnectionFailureError,
    RequestTimeoutError,
    ServerError,
    delete,
    get,
    post,
    put,
)


@pytest.fixture
def client() -> APIClient:
    return APIClient(base_url="https://api.testservice.com/v1", default_timeout=5.0)


def test_get_success(client: APIClient, mocker):
    """Verify GET request resolves relative path, passes params, and extracts JSON."""
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"items": [1, 2, 3]}'
    mock_resp.json.return_value = {"items": [1, 2, 3]}

    mock_req = mocker.patch.object(client.session, "request", return_value=mock_resp)

    data = client.get("users", params={"page": 2})

    mock_req.assert_called_once_with(
        "GET",
        "https://api.testservice.com/v1/users",
        params={"page": 2},
        timeout=5.0,
    )
    assert data == {"items": [1, 2, 3]}


def test_post_success(client: APIClient, mocker):
    """Verify POST request sends serialized JSON body."""
    mock_resp = Mock()
    mock_resp.status_code = 201
    mock_resp.content = b'{"id": 42, "name": "Created"}'
    mock_resp.json.return_value = {"id": 42, "name": "Created"}

    mock_req = mocker.patch.object(client.session, "request", return_value=mock_resp)

    payload = {"name": "Created"}
    result = client.post("users", json_data=payload)

    mock_req.assert_called_once_with(
        "POST",
        "https://api.testservice.com/v1/users",
        params=None,
        json=payload,
        timeout=5.0,
    )
    assert result["id"] == 42


def test_put_success(client: APIClient, mocker):
    """Verify PUT request updates resource."""
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"id": 42, "name": "Updated"}'
    mock_resp.json.return_value = {"id": 42, "name": "Updated"}

    mock_req = mocker.patch.object(client.session, "request", return_value=mock_resp)

    result = client.put("users/42", json_data={"name": "Updated"})

    mock_req.assert_called_once_with(
        "PUT",
        "https://api.testservice.com/v1/users/42",
        params=None,
        json={"name": "Updated"},
        timeout=5.0,
    )
    assert result["name"] == "Updated"


def test_delete_204_no_content_returns_none(client: APIClient, mocker):
    """Verify DELETE request with HTTP 204 returns None without trying to parse JSON."""
    mock_resp = Mock()
    mock_resp.status_code = 204
    mock_resp.content = b""

    mocker.patch.object(client.session, "request", return_value=mock_resp)

    result = client.delete("users/42")
    assert result is None


def test_client_error_raises_client_error_with_body(client: APIClient, mocker):
    """Verify 4xx status raises ClientError containing status code and error payload."""
    mock_resp = Mock()
    mock_resp.status_code = 404
    mock_resp.content = b'{"error": "User not found"}'
    mock_resp.json.return_value = {"error": "User not found"}

    mocker.patch.object(client.session, "request", return_value=mock_resp)

    with pytest.raises(ClientError) as exc_info:
        client.get("users/999")

    assert exc_info.value.status_code == 404
    assert exc_info.value.response_body == {"error": "User not found"}


def test_server_error_raises_server_error(client: APIClient, mocker):
    """Verify 5xx status raises ServerError."""
    mock_resp = Mock()
    mock_resp.status_code = 503
    mock_resp.content = b"Service Unavailable"
    mock_resp.json.side_effect = ValueError("Not JSON")
    mock_resp.text = "Service Unavailable"

    mocker.patch.object(client.session, "request", return_value=mock_resp)

    with pytest.raises(ServerError) as exc_info:
        client.get("health")

    assert exc_info.value.status_code == 503


def test_timeout_raises_request_timeout_error(client: APIClient, mocker):
    """Verify socket timeout maps to custom RequestTimeoutError."""
    mocker.patch.object(
        client.session,
        "request",
        side_effect=requests.exceptions.Timeout("Read timeout"),
    )

    with pytest.raises(RequestTimeoutError, match="timed out after 5.0s"):
        client.get("slow-endpoint")


def test_connection_error_raises_connection_failure_error(client: APIClient, mocker):
    """Verify connection error maps to ConnectionFailureError."""
    mocker.patch.object(
        client.session,
        "request",
        side_effect=requests.exceptions.ConnectionError("DNS failure"),
    )

    with pytest.raises(ConnectionFailureError, match="Failed to connect"):
        client.get("nonexistent-host")


def test_module_convenience_functions(mocker):
    """Verify top-level functional helpers get/post/put/delete work."""
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"ok": true}'
    mock_resp.json.return_value = {"ok": True}

    mock_req = mocker.patch("requests.Session.request", return_value=mock_resp)

    assert get("https://example.com/api") == {"ok": True}
    assert post("https://example.com/api", {"data": 1}) == {"ok": True}
    assert put("https://example.com/api", {"data": 2}) == {"ok": True}
    assert delete("https://example.com/api") == {"ok": True}

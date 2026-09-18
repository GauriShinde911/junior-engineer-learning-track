"""
tests/test_7_1_http_basics.py
Automated tests for 7.1 HTTP basics request inspection module.
Uses mocked HTTP responses to ensure deterministic, fast, offline execution.
"""

from pathlib import Path
from unittest.mock import Mock
import sys
import pytest
import requests

# Add 7.1 exercise directory to sys.path for direct module import
EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "7.1-http-basics"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from inspect_requests import (
    format_inspection,
    make_get_request,
    make_post_request,
)


def test_make_get_request_constructs_proper_query_and_parses_response(mocker):
    """Verify make_get_request sets headers, query params, and returns structured inspection."""
    mock_response = Mock()
    mock_response.url = "https://httpbin.org/get?topic=rest-api&step=7.1"
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "args": {"step": "7.1", "topic": "rest-api"},
        "headers": {"User-Agent": "JuniorEngineerLearningTrack/1.0"},
    }

    mock_request = Mock()
    mock_request.headers = {"User-Agent": "JuniorEngineerLearningTrack/1.0", "Accept": "application/json"}
    mock_response.request = mock_request

    mock_get = mocker.patch("requests.get", return_value=mock_response)

    result = make_get_request(
        "https://httpbin.org/get",
        params={"topic": "rest-api", "step": "7.1"},
    )

    mock_get.assert_called_once_with(
        "https://httpbin.org/get",
        params={"topic": "rest-api", "step": "7.1"},
        headers={"User-Agent": "JuniorEngineerLearningTrack/1.0", "Accept": "application/json"},
        timeout=5.0,
    )

    assert result["method"] == "GET"
    assert result["status_code"] == 200
    assert result["url"] == "https://httpbin.org/get?topic=rest-api&step=7.1"
    assert result["json_body"]["args"]["topic"] == "rest-api"


def test_make_get_request_raises_on_http_error(mocker):
    """Verify raise_for_status propagates HTTPError on 4xx/5xx."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(requests.exceptions.HTTPError, match="404 Not Found"):
        make_get_request("https://httpbin.org/status/404")


def test_make_post_request_serializes_json_and_headers(mocker):
    """Verify make_post_request adds Content-Type application/json and serializes body."""
    mock_response = Mock()
    mock_response.url = "https://httpbin.org/post"
    mock_response.status_code = 201
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"json": {"user": "Alice", "role": "dev"}}

    mock_request = Mock()
    mock_request.headers = {
        "User-Agent": "JuniorEngineerLearningTrack/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    mock_response.request = mock_request

    mock_post = mocker.patch("requests.post", return_value=mock_response)

    payload = {"user": "Alice", "role": "dev"}
    result = make_post_request("https://httpbin.org/post", json_data=payload)

    mock_post.assert_called_once_with(
        "https://httpbin.org/post",
        json=payload,
        headers={
            "User-Agent": "JuniorEngineerLearningTrack/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=5.0,
    )

    assert result["method"] == "POST"
    assert result["status_code"] == 201
    assert result["json_body"]["json"]["user"] == "Alice"


def test_format_inspection_renders_report():
    """Verify textual report formatting contains method, status, headers, and JSON."""
    inspection = {
        "method": "GET",
        "url": "https://api.example.com/items",
        "status_code": 200,
        "content_type": "application/json",
        "headers_sent": {"Authorization": "Bearer token123"},
        "json_body": {"count": 1, "items": ["item-1"]},
    }
    report = format_inspection(inspection)

    assert "=== HTTP GET Inspection ===" in report
    assert "https://api.example.com/items" in report
    assert "Status Code: 200" in report
    assert "Authorization: Bearer token123" in report
    assert '"count": 1' in report

"""
exercises/7.1-http-basics/inspect_requests.py
Inspects HTTP request/response cycles: methods, URLs, headers, status codes, and bodies.
"""

from typing import Any, Dict, Optional
import json
import requests

DEFAULT_HEADERS = {
    "User-Agent": "JuniorEngineerLearningTrack/1.0",
    "Accept": "application/json",
}


def make_get_request(
    url: str = "https://httpbin.org/get",
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """Execute an HTTP GET request and inspect request/response metadata.

    Args:
        url: Target HTTP endpoint.
        params: Optional query string parameters.
        timeout: Request timeout in seconds.

    Returns:
        Dictionary detailing method, URL, headers sent, status code, and response JSON.
    """
    response = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()

    return {
        "method": "GET",
        "url": response.url,
        "headers_sent": dict(response.request.headers),
        "status_code": response.status_code,
        "content_type": response.headers.get("Content-Type", ""),
        "json_body": response.json(),
    }


def make_post_request(
    url: str = "https://httpbin.org/post",
    json_data: Optional[Dict[str, Any]] = None,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """Execute an HTTP POST request and inspect transmission details.

    Args:
        url: Target HTTP endpoint.
        json_data: Dictionary payload to serialize as JSON body.
        timeout: Request timeout in seconds.

    Returns:
        Dictionary detailing method, URL, headers sent, status code, and parsed echo response.
    """
    headers = {**DEFAULT_HEADERS, "Content-Type": "application/json"}
    payload = json_data or {}
    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()

    return {
        "method": "POST",
        "url": response.url,
        "headers_sent": dict(response.request.headers),
        "status_code": response.status_code,
        "content_type": response.headers.get("Content-Type", ""),
        "json_body": response.json(),
    }


def format_inspection(inspection: Dict[str, Any]) -> str:
    """Format request/response cycle into a readable textual report."""
    lines = [
        f"=== HTTP {inspection['method']} Inspection ===",
        f"URL: {inspection['url']}",
        f"Status Code: {inspection['status_code']}",
        f"Content-Type: {inspection['content_type']}",
        "--- Headers Sent ---",
    ]
    for key, value in sorted(inspection["headers_sent"].items()):
        lines.append(f"  {key}: {value}")
    lines.append("--- Response Body (JSON) ---")
    lines.append(json.dumps(inspection["json_body"], indent=2))
    return "\n".join(lines)


def main() -> None:
    """Run live sample inspections against httpbin.org public test service."""
    print("Executing GET inspection...")
    get_result = make_get_request(
        "https://httpbin.org/get",
        params={"topic": "http-basics", "step": "7.1"},
    )
    print(format_inspection(get_result))
    print("\n" + "=" * 50 + "\n")

    print("Executing POST inspection...")
    post_result = make_post_request(
        "https://httpbin.org/post",
        json_data={"student": "Junior Engineer", "module": "07-rest-api"},
    )
    print(format_inspection(post_result))


if __name__ == "__main__":
    main()

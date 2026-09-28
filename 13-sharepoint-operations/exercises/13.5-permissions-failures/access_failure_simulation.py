"""
access_failure_simulation.py - SharePoint & Microsoft Graph Failure Simulator

Demonstrates and verifies client behavior under three realistic operational failure modes:
1. HTTP 403 Forbidden (Missing Graph API permissions or role assignment)
2. HTTP 429 Too Many Requests (Graph API rate limiting / throttling with Retry-After)
3. Network Disconnection / Connection Timeout
"""

import sys
from pathlib import Path
from unittest.mock import Mock
import requests

# Ensure 13.2 directory is in sys.path
curr_dir = Path(__file__).resolve().parent
sec2_dir = curr_dir.parent / "13.2-data-operations"
if str(sec2_dir) not in sys.path:
    sys.path.insert(0, str(sec2_dir))

from list_item_client import (
    SharePointAuthenticationError,
    SharePointClientError,
    SharePointListItemClient,
    SharePointThrottledError,
)


def simulate_permission_denied() -> dict:
    """
    Simulates a 403 Forbidden response caused by missing Microsoft Graph
    application permissions (e.g., app lacks Sites.ReadWrite.All).
    """
    client = SharePointListItemClient(access_token="fake-token")
    mock_resp = Mock(spec=requests.Response)
    mock_resp.status_code = 403
    mock_resp.text = (
        '{"error": {"code": "AccessDenied", "message": "Access was denied to this site resource.", '
        '"innerError": {"client-request-id": "sim-403-uuid"}}}'
    )
    client.session.get = Mock(return_value=mock_resp)

    try:
        client.get_item(site_id="corp-site", list_id="assets-list", item_id=101)
        return {"status": "UNEXPECTED_SUCCESS"}
    except SharePointAuthenticationError as e:
        return {
            "status": "CAUGHT_PERMISSION_DENIED",
            "error_type": type(e).__name__,
            "message": str(e),
            "http_code": 403,
        }


def simulate_throttling_429() -> dict:
    """
    Simulates a 429 Too Many Requests response caused by Graph API request rate limits.
    Verifies that Retry-After header is correctly extracted.
    """
    client = SharePointListItemClient(access_token="fake-token")
    mock_resp = Mock(spec=requests.Response)
    mock_resp.status_code = 429
    mock_resp.headers = {"Retry-After": "45"}
    mock_resp.text = (
        '{"error": {"code": "activityLimitReached", "message": "The application has exceeded '
        'its request rate limit.", "innerError": {"client-request-id": "sim-429-uuid"}}}'
    )
    client.session.get = Mock(return_value=mock_resp)

    try:
        client.get_item(site_id="corp-site", list_id="assets-list", item_id=101)
        return {"status": "UNEXPECTED_SUCCESS"}
    except SharePointThrottledError as e:
        return {
            "status": "CAUGHT_THROTTLED",
            "error_type": type(e).__name__,
            "retry_after_seconds": e.retry_after,
            "message": str(e),
            "http_code": 429,
        }


def simulate_network_failure() -> dict:
    """
    Simulates a low-level network connectivity loss or DNS resolution failure.
    """
    client = SharePointListItemClient(access_token="fake-token")
    client.session.get = Mock(
        side_effect=requests.exceptions.ConnectionError(
            "HTTPSConnectionPool(host='graph.microsoft.com', port=443): Max retries exceeded"
        )
    )

    try:
        client.get_item(site_id="corp-site", list_id="assets-list", item_id=101)
        return {"status": "UNEXPECTED_SUCCESS"}
    except requests.exceptions.ConnectionError as e:
        return {
            "status": "CAUGHT_NETWORK_FAILURE",
            "error_type": type(e).__name__,
            "message": str(e),
        }


def run_all_simulations():
    print("=== Microsoft Graph / SharePoint Failure Simulations ===\n")

    res_403 = simulate_permission_denied()
    print("[1] 403 Forbidden Simulation:")
    print(f"    Status: {res_403['status']}")
    print(f"    Exception: {res_403['error_type']} - {res_403['message']}\n")

    res_429 = simulate_throttling_429()
    print("[2] 429 Throttling Simulation:")
    print(f"    Status: {res_429['status']}")
    print(f"    Retry-After Extracted: {res_429['retry_after_seconds']} seconds\n")

    res_net = simulate_network_failure()
    print("[3] Network Disconnection Simulation:")
    print(f"    Status: {res_net['status']}")
    print(f"    Exception: {res_net['error_type']}\n")


if __name__ == "__main__":
    run_all_simulations()

"""
exercises/7.2-python-http-client/api_client.py
Reusable HTTP client wrapping the requests library with mandatory timeouts,
consistent JSON serialization/deserialization, and status error classification.
"""

from typing import Any, Dict, Optional, Union
import requests


class APIClientError(Exception):
    """Base exception for all HTTP client errors."""
    pass


class RequestTimeoutError(APIClientError):
    """Raised when an HTTP request exceeds the configured timeout."""
    pass


class ConnectionFailureError(APIClientError):
    """Raised when DNS lookup, connection establishment, or socket fails."""
    pass


class HTTPStatusError(APIClientError):
    """Raised when the server responds with an HTTP error status code (4xx or 5xx)."""

    def __init__(self, message: str, status_code: int, response_body: Any = None) -> None:
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.response_body = response_body


class ClientError(HTTPStatusError):
    """Raised on 4xx Client Error responses."""
    pass


class ServerError(HTTPStatusError):
    """Raised on 5xx Server Error responses."""
    pass


class APIClient:
    """Configurable HTTP client supporting REST verbs with safe defaults."""

    DEFAULT_TIMEOUT = 10.0

    def __init__(
        self,
        base_url: str = "",
        default_timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_timeout = default_timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "APIClient/1.0",
            "Accept": "application/json",
        })
        if headers:
            self.session.headers.update(headers)

    def _resolve_url(self, endpoint: str) -> str:
        """Combine base_url and endpoint path."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        clean_endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{clean_endpoint}" if self.base_url else endpoint

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Internal dispatch executing the HTTP request with standardized error handling."""
        url = self._resolve_url(endpoint)
        effective_timeout = timeout if timeout is not None else self.default_timeout

        request_kwargs: Dict[str, Any] = {
            "params": params,
            "timeout": effective_timeout,
        }
        if headers:
            request_kwargs["headers"] = headers
        if json_data is not None:
            request_kwargs["json"] = json_data

        try:
            response = self.session.request(method, url, **request_kwargs)
        except requests.exceptions.Timeout as exc:
            raise RequestTimeoutError(f"Request to {url} timed out after {effective_timeout}s") from exc
        except requests.exceptions.ConnectionError as exc:
            raise ConnectionFailureError(f"Failed to connect to {url}: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise APIClientError(f"Unexpected request failure for {url}: {exc}") from exc

        # Error status code handling
        if 400 <= response.status_code < 500:
            body = self._parse_json_safe(response)
            raise ClientError(f"Client error on {method} {url}", response.status_code, body)
        if response.status_code >= 500:
            body = self._parse_json_safe(response)
            raise ServerError(f"Server error on {method} {url}", response.status_code, body)

        # 204 No Content has no body
        if response.status_code == 204 or not response.content:
            return None

        return self._parse_json_safe(response)

    def _parse_json_safe(self, response: requests.Response) -> Any:
        """Safely parse JSON body or return raw text fallback."""
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Execute GET request."""
        return self._request("GET", endpoint, params=params, timeout=timeout, headers=headers)

    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Execute POST request."""
        return self._request("POST", endpoint, json_data=json_data, timeout=timeout, headers=headers)

    def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Execute PUT request."""
        return self._request("PUT", endpoint, json_data=json_data, timeout=timeout, headers=headers)

    def delete(
        self,
        endpoint: str,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Execute DELETE request."""
        return self._request("DELETE", endpoint, timeout=timeout, headers=headers)


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

_default_client = APIClient()


def get(url: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0) -> Any:
    return _default_client.get(url, params=params, timeout=timeout)


def post(url: str, json_data: Optional[Dict[str, Any]] = None, timeout: float = 10.0) -> Any:
    return _default_client.post(url, json_data=json_data, timeout=timeout)


def put(url: str, json_data: Optional[Dict[str, Any]] = None, timeout: float = 10.0) -> Any:
    return _default_client.put(url, json_data=json_data, timeout=timeout)


def delete(url: str, timeout: float = 10.0) -> Any:
    return _default_client.delete(url, timeout=timeout)

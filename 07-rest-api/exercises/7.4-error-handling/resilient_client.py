"""
exercises/7.4-error-handling/resilient_client.py
Wraps api_client.py with retry logic (exponential backoff), timeout and connection
handling, rate-limit detection, and user-safe error message translation.
"""

import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type
import sys

# Allow import from sibling 7.2 exercise directory
API_CLIENT_DIR = Path(__file__).resolve().parent.parent / "7.2-python-http-client"
if str(API_CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(API_CLIENT_DIR))

from api_client import (
    APIClient,
    APIClientError,
    ClientError,
    ConnectionFailureError,
    RequestTimeoutError,
    ServerError,
)


class RateLimitError(APIClientError):
    """Raised when the remote API returns HTTP 429 Too Many Requests."""

    def __init__(self, message: str, retry_after: Optional[int] = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class UserFacingError(Exception):
    """Safe, human-readable error shown to end users (no stack traces / internal paths)."""

    def __init__(self, user_message: str, technical_detail: str = "") -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.technical_detail = technical_detail


class ResilientClient:
    """API client wrapper with automatic retries, backoff, and user-safe error messages."""

    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BACKOFF_BASE = 0.5   # seconds
    DEFAULT_BACKOFF_MAX = 10.0   # seconds cap

    RETRYABLE_EXCEPTIONS: tuple = (RequestTimeoutError, ConnectionFailureError, ServerError)

    def __init__(
        self,
        base_url: str = "",
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        backoff_max: float = DEFAULT_BACKOFF_MAX,
        headers: Optional[Dict[str, str]] = None,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = APIClient(base_url=base_url, headers=headers)
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self._sleep = sleep_fn  # injectable for testing (avoids real sleeps)

    def _backoff_seconds(self, attempt: int) -> float:
        """Exponential backoff: base * 2^attempt, capped at backoff_max."""
        return min(self.backoff_base * (2 ** attempt), self.backoff_max)

    def _translate_to_user_error(self, exc: Exception, context: str) -> UserFacingError:
        """Convert raw client exceptions into safe, user-readable messages."""
        if isinstance(exc, RequestTimeoutError):
            return UserFacingError(
                f"The request timed out while {context}. Please try again in a moment.",
                technical_detail=str(exc),
            )
        if isinstance(exc, ConnectionFailureError):
            return UserFacingError(
                f"Could not reach the service while {context}. Check your network connection.",
                technical_detail=str(exc),
            )
        if isinstance(exc, RateLimitError):
            wait_msg = f" (retry after {exc.retry_after}s)" if exc.retry_after else ""
            return UserFacingError(
                f"Too many requests were sent{wait_msg}. Please slow down and try again.",
                technical_detail=str(exc),
            )
        if isinstance(exc, ClientError):
            if exc.status_code == 401:
                return UserFacingError(
                    "Authentication failed. Check your API credentials.",
                    technical_detail=str(exc),
                )
            if exc.status_code == 403:
                return UserFacingError(
                    "Access denied. You do not have permission to perform this action.",
                    technical_detail=str(exc),
                )
            if exc.status_code == 404:
                return UserFacingError(
                    "The requested resource was not found.",
                    technical_detail=str(exc),
                )
            return UserFacingError(
                f"The request was rejected by the server (error {exc.status_code}).",
                technical_detail=str(exc),
            )
        if isinstance(exc, ServerError):
            return UserFacingError(
                f"The service encountered an unexpected error while {context}. Please try again later.",
                technical_detail=str(exc),
            )
        return UserFacingError(
            f"An unexpected error occurred while {context}. Please contact support.",
            technical_detail=str(exc),
        )

    def _execute_with_retry(
        self,
        method: str,
        endpoint: str,
        context: str,
        **kwargs: Any,
    ) -> Any:
        """Dispatch HTTP method with retry loop and backoff."""
        last_exc: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                fn = getattr(self._client, method)
                result = fn(endpoint, **kwargs)
                return result

            except ClientError as exc:
                # Special-case 429 Rate Limit: retryable with optional Retry-After header
                if exc.status_code == 429:
                    rate_error = RateLimitError(
                        f"Rate limit exceeded on {endpoint}",
                        retry_after=None,
                    )
                    if attempt >= self.max_retries:
                        raise self._translate_to_user_error(rate_error, context) from exc
                    wait = self._backoff_seconds(attempt)
                    self._sleep(wait)
                    last_exc = exc
                    continue
                # Other 4xx errors are not retryable (caller error — not transient)
                raise self._translate_to_user_error(exc, context) from exc

            except self.RETRYABLE_EXCEPTIONS as exc:
                last_exc = exc
                if attempt >= self.max_retries:
                    break
                wait = self._backoff_seconds(attempt)
                self._sleep(wait)

        raise self._translate_to_user_error(last_exc, context)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, context: str = "fetching data") -> Any:
        return self._execute_with_retry("get", endpoint, context=context, params=params)

    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, context: str = "submitting data") -> Any:
        return self._execute_with_retry("post", endpoint, context=context, json_data=json_data)

    def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, context: str = "updating resource") -> Any:
        return self._execute_with_retry("put", endpoint, context=context, json_data=json_data)

    def delete(self, endpoint: str, context: str = "deleting resource") -> Any:
        return self._execute_with_retry("delete", endpoint, context=context)

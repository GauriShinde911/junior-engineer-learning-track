"""
independent/api_client_from_spec/client.py
Type-annotated Python client for the Weather Forecast API v1.
Implements every endpoint in SPECIFICATION.md:
  - GET  /locations
  - GET  /forecast/{location_id}
  - POST /alerts
  - DELETE /alerts/{alert_id}

Raises descriptive domain exceptions (not raw requests exceptions).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import requests


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class WeatherAPIError(Exception):
    """Base exception for all WeatherForecastClient errors."""


class AuthenticationError(WeatherAPIError):
    """Raised when the API key is missing or invalid (HTTP 401)."""


class ResourceNotFoundError(WeatherAPIError):
    """Raised when a requested resource does not exist (HTTP 404)."""

    def __init__(self, resource_type: str, resource_id: str) -> None:
        super().__init__(f"{resource_type} '{resource_id}' not found")
        self.resource_type = resource_type
        self.resource_id = resource_id


class ValidationError(WeatherAPIError):
    """Raised when the request parameters fail server-side validation (HTTP 400/422)."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class WeatherAPIServerError(WeatherAPIError):
    """Raised when the server returns a 5xx error."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"Server error {status_code}: {message}")
        self.status_code = status_code


class NetworkError(WeatherAPIError):
    """Raised when a network-level error occurs (timeout, DNS, connection refused)."""


# ---------------------------------------------------------------------------
# Response data models (dataclasses)
# ---------------------------------------------------------------------------

@dataclass
class Location:
    id: str
    name: str
    timezone: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Location:
        return cls(id=d["id"], name=d["name"], timezone=d["timezone"])


@dataclass
class ForecastDay:
    date: str
    high_temp: float
    low_temp: float
    condition: str
    precipitation_mm: float
    wind_kph: float

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ForecastDay:
        return cls(
            date=d["date"],
            high_temp=d["high_temp"],
            low_temp=d["low_temp"],
            condition=d["condition"],
            precipitation_mm=d["precipitation_mm"],
            wind_kph=d["wind_kph"],
        )


@dataclass
class Forecast:
    location: Location
    units: str
    days: List[ForecastDay]

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Forecast:
        return cls(
            location=Location.from_dict(d["location"]),
            units=d["units"],
            days=[ForecastDay.from_dict(day) for day in d["forecast"]],
        )


@dataclass
class WeatherAlert:
    id: str
    location_id: str
    condition: str
    threshold: float
    notify_email: str
    created_at: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> WeatherAlert:
        return cls(
            id=d["id"],
            location_id=d["location_id"],
            condition=d["condition"],
            threshold=d["threshold"],
            notify_email=d["notify_email"],
            created_at=d.get("created_at", ""),
        )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

VALID_UNITS = ("metric", "imperial")
VALID_CONDITIONS = ("precipitation_mm", "high_temp", "low_temp")


class WeatherForecastClient:
    """
    Client for Weather Forecast API v1.

    Usage:
        client = WeatherForecastClient(api_key="your-key")
        locations = client.list_locations()
        forecast = client.get_forecast("london-gb", days=5, units="metric")
    """

    BASE_URL = "https://api.weatherforecast.example.com/v1"

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: int = 10,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must not be empty")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _handle_response(self, response: requests.Response, resource_type: str = "", resource_id: str = "") -> Any:
        """Parse response and raise domain exceptions for error status codes."""
        status = response.status_code

        if status == 204:
            return None

        if status == 200 or status == 201:
            try:
                return response.json()
            except ValueError:
                return None

        try:
            error_body = response.json()
            server_message = error_body.get("message", response.text)
        except ValueError:
            server_message = response.text or f"HTTP {status}"

        if status == 401:
            raise AuthenticationError(f"Authentication failed: {server_message}")
        if status == 404:
            raise ResourceNotFoundError(resource_type or "Resource", resource_id or "unknown")
        if status in (400, 422):
            raise ValidationError(server_message, status_code=status)
        if status >= 500:
            raise WeatherAPIServerError(status, server_message)

        raise WeatherAPIError(f"Unexpected HTTP {status}: {server_message}")

    def _request(
        self,
        method: str,
        path: str,
        resource_type: str = "",
        resource_id: str = "",
        **kwargs: Any,
    ) -> Any:
        """Execute HTTP request with unified error handling."""
        url = self._url(path)
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request to {url} timed out after {self.timeout}s")
        except requests.exceptions.ConnectionError as exc:
            raise NetworkError(f"Failed to connect to {url}: {exc}")
        return self._handle_response(response, resource_type=resource_type, resource_id=resource_id)

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def list_locations(self) -> List[Location]:
        """Fetch all available weather tracking locations."""
        data = self._request("GET", "/locations", resource_type="Locations")
        return [Location.from_dict(loc) for loc in data.get("locations", [])]

    def get_forecast(
        self,
        location_id: str,
        days: int = 7,
        units: str = "metric",
    ) -> Forecast:
        """
        Retrieve weather forecast for a specific location.

        Args:
            location_id: Location identifier (from list_locations)
            days: Number of forecast days (1-14)
            units: Temperature units — "metric" (°C) or "imperial" (°F)

        Raises:
            ValidationError: if days is out of range or units is invalid
            ResourceNotFoundError: if location_id does not exist
        """
        if not 1 <= days <= 14:
            raise ValidationError(f"'days' must be between 1 and 14, got {days}", status_code=422)
        if units not in VALID_UNITS:
            raise ValidationError(
                f"'units' must be one of {VALID_UNITS}, got '{units}'", status_code=422
            )
        data = self._request(
            "GET",
            f"/forecast/{location_id}",
            resource_type="Location",
            resource_id=location_id,
            params={"days": days, "units": units},
        )
        return Forecast.from_dict(data)

    def create_alert(
        self,
        location_id: str,
        condition: str,
        threshold: float,
        notify_email: str,
    ) -> WeatherAlert:
        """
        Create a weather alert subscription.

        Args:
            location_id: Location to monitor
            condition: One of "precipitation_mm", "high_temp", "low_temp"
            threshold: Numeric value that triggers the alert
            notify_email: Email address to send alert notifications to

        Raises:
            ValidationError: if required fields are missing or invalid
            ResourceNotFoundError: if location_id does not exist
        """
        if condition not in VALID_CONDITIONS:
            raise ValidationError(
                f"'condition' must be one of {VALID_CONDITIONS}, got '{condition}'", status_code=400
            )
        if not notify_email or "@" not in notify_email:
            raise ValidationError("'notify_email' must be a valid email address", status_code=400)

        payload = {
            "location_id": location_id,
            "condition": condition,
            "threshold": float(threshold),
            "notify_email": notify_email,
        }
        data = self._request(
            "POST",
            "/alerts",
            resource_type="Location",
            resource_id=location_id,
            json=payload,
        )
        return WeatherAlert.from_dict(data)

    def delete_alert(self, alert_id: str) -> None:
        """
        Delete a weather alert by its ID.

        Raises:
            ResourceNotFoundError: if alert_id does not exist
        """
        self._request(
            "DELETE",
            f"/alerts/{alert_id}",
            resource_type="Alert",
            resource_id=alert_id,
        )

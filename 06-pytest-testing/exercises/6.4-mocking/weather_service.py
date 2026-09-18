"""
exercises/6.4-mocking/weather_service.py
Service that interacts with an external third-party HTTP API via requests.
In automated tests, this network boundary MUST be mocked to keep tests fast,
deterministic, and runnable offline.
"""

from typing import Any, Dict
import requests


class WeatherServiceError(Exception):
    """Base exception for weather service errors."""
    pass


class CityNotFoundError(WeatherServiceError):
    """Raised when the queried city cannot be found."""
    pass


class WeatherServiceTimeoutError(WeatherServiceError):
    """Raised when the external weather provider fails to respond in time."""
    pass


class WeatherService:
    """Client service for querying meteorological conditions."""

    def __init__(
        self,
        base_url: str = "https://api.weather-provider.com/v1",
        api_key: str = "demo-secret-key",
        timeout_seconds: float = 3.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Fetch current weather for a city from remote API.

        Args:
            city: City name.

        Returns:
            Dictionary containing city, temperature in Celsius, and weather condition.

        Raises:
            ValueError: If city is empty.
            CityNotFoundError: If upstream API returns HTTP 404.
            WeatherServiceTimeoutError: If HTTP request times out.
            WeatherServiceError: For any other upstream or transport failures.
        """
        if not city or not city.strip():
            raise ValueError("City name cannot be empty")

        url = f"{self.base_url}/current"
        params = {"q": city.strip(), "apikey": self.api_key}

        try:
            response = requests.get(url, params=params, timeout=self.timeout_seconds)
        except requests.exceptions.Timeout as exc:
            raise WeatherServiceTimeoutError(f"Weather API request timed out for city: {city}") from exc
        except requests.exceptions.RequestException as exc:
            raise WeatherServiceError(f"Network transport failure connecting to weather API: {exc}") from exc

        if response.status_code == 404:
            raise CityNotFoundError(f"City '{city}' was not found by the weather service")
        if response.status_code != 200:
            raise WeatherServiceError(f"Upstream weather provider returned error status {response.status_code}")

        try:
            payload = response.json()
            return {
                "city": payload["location"]["name"],
                "temp_c": float(payload["current"]["temp_c"]),
                "condition": payload["current"]["condition"]["text"],
                "humidity": int(payload["current"]["humidity"]),
            }
        except (KeyError, ValueError, TypeError) as exc:
            raise WeatherServiceError(f"Malformed JSON schema received from weather API: {exc}") from exc

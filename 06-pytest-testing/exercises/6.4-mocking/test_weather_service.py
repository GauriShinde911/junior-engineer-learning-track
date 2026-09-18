"""
exercises/6.4-mocking/test_weather_service.py
Demonstrating HTTP boundary mocking with pytest-mock.

WHAT IS MOCKED & WHY:
- We mock `requests.get` because it represents an external network boundary outside
  our process. Real HTTP calls are slow, require network connectivity, cost API credits,
  and introduce flaky non-determinism (remote downtime, rate limits).
- WHAT IS NOT MOCKED:
  We do NOT mock `WeatherService.get_current_weather`, the URL construction, query
  parameter formatting, status-code dispatch logic, or JSON parsing. The service
  implementation remains 100% REAL so we verify our exact business code.
"""

from unittest.mock import Mock
import pytest
import requests

from weather_service import (
    CityNotFoundError,
    WeatherService,
    WeatherServiceError,
    WeatherServiceTimeoutError,
)


@pytest.fixture
def weather_client() -> WeatherService:
    """Instantiate a real WeatherService client pointing at a dummy base URL."""
    return WeatherService(base_url="https://api.weather-mock.com/v1", api_key="secret-key")


def test_get_current_weather_success(weather_client: WeatherService, mocker):
    """Verify successful parsing when upstream API returns HTTP 200 with valid JSON."""
    mock_payload = {
        "location": {"name": "San Francisco"},
        "current": {
            "temp_c": 18.5,
            "condition": {"text": "Partly Cloudy"},
            "humidity": 65,
        },
    }

    # Setup mock HTTP response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_payload

    # Patch requests.get at the exact point of consumption
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    result = weather_client.get_current_weather("San Francisco")

    # Assert outbound HTTP request was formulated with exact parameters
    mock_get.assert_called_once_with(
        "https://api.weather-mock.com/v1/current",
        params={"q": "San Francisco", "apikey": "secret-key"},
        timeout=3.0,
    )

    # Assert the internal parsing extracted the contract dictionary cleanly
    assert result == {
        "city": "San Francisco",
        "temp_c": 18.5,
        "condition": "Partly Cloudy",
        "humidity": 65,
    }


def test_get_current_weather_city_not_found(weather_client: WeatherService, mocker):
    """Verify HTTP 404 is mapped to custom CityNotFoundError domain exception."""
    mock_response = Mock()
    mock_response.status_code = 404
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(CityNotFoundError, match="City 'Atlantis' was not found"):
        weather_client.get_current_weather("Atlantis")


def test_get_current_weather_timeout_mapped_to_domain_error(weather_client: WeatherService, mocker):
    """Verify socket timeout exception is caught and re-raised as WeatherServiceTimeoutError."""
    # Simulate network timeout using side_effect
    mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.Timeout("Connection timed out after 3000ms"),
    )

    with pytest.raises(WeatherServiceTimeoutError, match="Weather API request timed out"):
        weather_client.get_current_weather("Chicago")


def test_get_current_weather_upstream_500_error(weather_client: WeatherService, mocker):
    """Verify HTTP 500 server error raises WeatherServiceError."""
    mock_response = Mock()
    mock_response.status_code = 500
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(WeatherServiceError, match="returned error status 500"):
        weather_client.get_current_weather("London")


def test_get_current_weather_empty_city_validation():
    """Verify local input validation executes without invoking any network call."""
    service = WeatherService()
    with pytest.raises(ValueError, match="City name cannot be empty"):
        service.get_current_weather("   ")

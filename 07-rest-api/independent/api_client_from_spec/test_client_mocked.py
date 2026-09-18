"""
independent/api_client_from_spec/test_client_mocked.py
Comprehensive mock-based tests for WeatherForecastClient.
Covers all four endpoints, all error cases, and client-side validation.
No real network calls.
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch
import sys
import json

import pytest
import requests

CLIENT_DIR = Path(__file__).resolve().parent
if str(CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(CLIENT_DIR))

from client import (
    AuthenticationError,
    Forecast,
    ForecastDay,
    Location,
    NetworkError,
    ResourceNotFoundError,
    ValidationError,
    WeatherAlert,
    WeatherAPIError,
    WeatherAPIServerError,
    WeatherForecastClient,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resp(status: int, body: Any = None) -> Mock:
    m = Mock(spec=requests.Response)
    m.status_code = status
    if body is None:
        m.content = b""
        m.json.side_effect = ValueError("no content")
        m.text = ""
    elif isinstance(body, (dict, list)):
        raw = json.dumps(body).encode()
        m.content = raw
        m.json.return_value = body
        m.text = raw.decode()
    else:
        m.content = str(body).encode()
        m.json.side_effect = ValueError("not json")
        m.text = str(body)
    return m


LOCATION_DATA = {
    "locations": [
        {"id": "london-gb", "name": "London, UK", "timezone": "Europe/London"},
        {"id": "nyc-us", "name": "New York City, US", "timezone": "America/New_York"},
    ]
}

FORECAST_DATA = {
    "location": {"id": "london-gb", "name": "London, UK", "timezone": "Europe/London"},
    "units": "metric",
    "forecast": [
        {
            "date": "2024-03-01",
            "high_temp": 14,
            "low_temp": 8,
            "condition": "Partly Cloudy",
            "precipitation_mm": 2.1,
            "wind_kph": 20,
        },
        {
            "date": "2024-03-02",
            "high_temp": 12,
            "low_temp": 6,
            "condition": "Rainy",
            "precipitation_mm": 15.3,
            "wind_kph": 35,
        },
    ],
}

ALERT_DATA = {
    "id": "alert-abc-123",
    "location_id": "london-gb",
    "condition": "precipitation_mm",
    "threshold": 10.0,
    "notify_email": "user@example.com",
    "created_at": "2024-03-01T09:00:00Z",
}


@pytest.fixture
def client() -> WeatherForecastClient:
    return WeatherForecastClient(api_key="test-api-key")


# ---------------------------------------------------------------------------
# Client initialization
# ---------------------------------------------------------------------------

class TestClientInitialization:

    def test_requires_non_empty_api_key(self):
        with pytest.raises(ValueError, match="api_key"):
            WeatherForecastClient(api_key="")

    def test_auth_header_set_on_session(self, client: WeatherForecastClient):
        assert "Bearer test-api-key" in client.session.headers.get("Authorization", "")

    def test_accept_json_header_set(self, client: WeatherForecastClient):
        assert client.session.headers.get("Accept") == "application/json"

    def test_custom_base_url(self):
        c = WeatherForecastClient(api_key="key", base_url="https://my-server.test/v2")
        assert "my-server.test" in c.base_url


# ---------------------------------------------------------------------------
# GET /locations
# ---------------------------------------------------------------------------

class TestListLocations:

    def test_returns_list_of_location_objects(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(200, LOCATION_DATA)):
            locations = client.list_locations()
        assert len(locations) == 2
        assert all(isinstance(loc, Location) for loc in locations)

    def test_location_fields_parsed_correctly(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(200, LOCATION_DATA)):
            locations = client.list_locations()
        assert locations[0].id == "london-gb"
        assert locations[0].name == "London, UK"
        assert locations[0].timezone == "Europe/London"

    def test_uses_get_method(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(200, LOCATION_DATA)) as m:
            client.list_locations()
        args, _ = m.call_args
        assert args[0].upper() == "GET"

    def test_401_raises_authentication_error(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(401, {"error": "Unauthorized", "message": "Bad token"})):
            with pytest.raises(AuthenticationError):
                client.list_locations()

    def test_500_raises_server_error(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(500, "Server Error")):
            with pytest.raises(WeatherAPIServerError):
                client.list_locations()


# ---------------------------------------------------------------------------
# GET /forecast/{location_id}
# ---------------------------------------------------------------------------

class TestGetForecast:

    def test_returns_forecast_object(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(200, FORECAST_DATA)):
            forecast = client.get_forecast("london-gb")
        assert isinstance(forecast, Forecast)
        assert forecast.units == "metric"
        assert len(forecast.days) == 2

    def test_forecast_days_parsed(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(200, FORECAST_DATA)):
            forecast = client.get_forecast("london-gb")
        day = forecast.days[0]
        assert isinstance(day, ForecastDay)
        assert day.date == "2024-03-01"
        assert day.high_temp == 14
        assert day.condition == "Partly Cloudy"

    def test_query_params_forwarded(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(200, FORECAST_DATA)) as m:
            client.get_forecast("london-gb", days=5, units="imperial")
        _, kwargs = m.call_args
        assert kwargs.get("params", {}).get("days") == 5
        assert kwargs.get("params", {}).get("units") == "imperial"

    def test_client_validates_days_range(self, client: WeatherForecastClient):
        with pytest.raises(ValidationError, match="days"):
            client.get_forecast("london-gb", days=0)
        with pytest.raises(ValidationError, match="days"):
            client.get_forecast("london-gb", days=15)

    def test_client_validates_units_value(self, client: WeatherForecastClient):
        with pytest.raises(ValidationError, match="units"):
            client.get_forecast("london-gb", units="kelvin")

    def test_404_raises_resource_not_found(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(404, {"error": "Not Found", "message": "Unknown location"})):
            with pytest.raises(ResourceNotFoundError) as exc_info:
                client.get_forecast("unknown-city")
        assert exc_info.value.resource_type == "Location"
        assert exc_info.value.resource_id == "unknown-city"

    def test_422_raises_validation_error(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(422, {"error": "Validation Error", "message": "Invalid days"})):
            with pytest.raises(ValidationError):
                client.get_forecast("london-gb", days=5)  # Valid locally but "server rejects"


# ---------------------------------------------------------------------------
# POST /alerts
# ---------------------------------------------------------------------------

class TestCreateAlert:

    def test_returns_weather_alert_object(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(201, ALERT_DATA)):
            alert = client.create_alert(
                location_id="london-gb",
                condition="precipitation_mm",
                threshold=10.0,
                notify_email="user@example.com",
            )
        assert isinstance(alert, WeatherAlert)
        assert alert.id == "alert-abc-123"
        assert alert.threshold == 10.0

    def test_post_method_used(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(201, ALERT_DATA)) as m:
            client.create_alert("london-gb", "high_temp", 35.0, "a@b.com")
        args, _ = m.call_args
        assert args[0].upper() == "POST"

    def test_json_body_sent(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(201, ALERT_DATA)) as m:
            client.create_alert("london-gb", "high_temp", 35.0, "a@b.com")
        _, kwargs = m.call_args
        body = kwargs.get("json", {})
        assert body["location_id"] == "london-gb"
        assert body["condition"] == "high_temp"
        assert body["threshold"] == 35.0

    def test_invalid_condition_raises_validation_error(self, client: WeatherForecastClient):
        with pytest.raises(ValidationError, match="condition"):
            client.create_alert("london-gb", "wind_speed", 50.0, "a@b.com")

    def test_invalid_email_raises_validation_error(self, client: WeatherForecastClient):
        with pytest.raises(ValidationError, match="email"):
            client.create_alert("london-gb", "high_temp", 35.0, "not-an-email")

    def test_404_location_not_found(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(404, {"error": "Not Found", "message": "Location not found"})):
            with pytest.raises(ResourceNotFoundError):
                client.create_alert("fake-city", "high_temp", 35.0, "a@b.com")


# ---------------------------------------------------------------------------
# DELETE /alerts/{alert_id}
# ---------------------------------------------------------------------------

class TestDeleteAlert:

    def test_delete_returns_none_on_204(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(204)):
            result = client.delete_alert("alert-abc-123")
        assert result is None

    def test_delete_method_used(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(204)) as m:
            client.delete_alert("alert-abc-123")
        args, _ = m.call_args
        assert args[0].upper() == "DELETE"

    def test_url_contains_alert_id(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(204)) as m:
            client.delete_alert("alert-abc-123")
        args, _ = m.call_args
        url = args[1]
        assert "alert-abc-123" in url

    def test_404_raises_resource_not_found(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", return_value=_resp(404, {"error": "Not Found", "message": "Alert not found"})):
            with pytest.raises(ResourceNotFoundError) as exc_info:
                client.delete_alert("nonexistent-id")
        assert exc_info.value.resource_type == "Alert"


# ---------------------------------------------------------------------------
# Network error handling
# ---------------------------------------------------------------------------

class TestNetworkErrors:

    def test_timeout_raises_network_error(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", side_effect=requests.exceptions.Timeout()):
            with pytest.raises(NetworkError, match="timed out"):
                client.list_locations()

    def test_connection_error_raises_network_error(self, client: WeatherForecastClient):
        with patch.object(client.session, "request", side_effect=requests.exceptions.ConnectionError("refused")):
            with pytest.raises(NetworkError, match="connect"):
                client.get_forecast("london-gb")

    def test_all_domain_exceptions_inherit_weather_api_error(self):
        assert issubclass(AuthenticationError, WeatherAPIError)
        assert issubclass(ResourceNotFoundError, WeatherAPIError)
        assert issubclass(ValidationError, WeatherAPIError)
        assert issubclass(WeatherAPIServerError, WeatherAPIError)
        assert issubclass(NetworkError, WeatherAPIError)

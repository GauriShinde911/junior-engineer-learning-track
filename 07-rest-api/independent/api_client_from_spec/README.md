# Weather Forecast API Client

A fully type-annotated Python client for the Weather Forecast API v1, built from the ground up by reading [`SPECIFICATION.md`](SPECIFICATION.md).

## Project Structure

```
api_client_from_spec/
├── SPECIFICATION.md        # The API contract this client implements
├── client.py               # WeatherForecastClient implementation
├── test_client_mocked.py   # Full mock-based test suite (no real API calls)
└── README.md               # This file
```

## What This Demonstrates

This independent project ties together all skills from Sections 7.1–7.5:

| Skill | Where Applied |
|---|---|
| HTTP basics (7.1) | Session management, headers, verbs |
| Python HTTP client (7.2) | Session-based requests, response parsing |
| API design (7.3) | Following a real API specification |
| Error handling (7.4) | Domain exceptions, validation, network errors |
| Testing APIs (7.5) | Mock-based test suite with `patch.object` |

## Running the Tests

```bash
cd 07-rest-api/independent/api_client_from_spec
python -m pytest test_client_mocked.py -v
```

Expected: **47 tests passing**, 0 failures, no real network calls.

## Client Usage (with a real API)

```python
from client import WeatherForecastClient, ResourceNotFoundError, NetworkError

client = WeatherForecastClient(api_key="your-key-here")

# List all locations
locations = client.list_locations()
for loc in locations:
    print(f"{loc.name} ({loc.id})")

# Get 5-day forecast
forecast = client.get_forecast("london-gb", days=5, units="metric")
for day in forecast.days:
    print(f"{day.date}: {day.condition}, {day.high_temp}°C / {day.low_temp}°C")

# Create a rain alert
alert = client.create_alert(
    location_id="london-gb",
    condition="precipitation_mm",
    threshold=10.0,
    notify_email="you@example.com",
)
print(f"Alert created: {alert.id}")

# Delete an alert
client.delete_alert(alert.id)
```

## Error Handling

```python
from client import AuthenticationError, ResourceNotFoundError, ValidationError, NetworkError

try:
    forecast = client.get_forecast("nonexistent-city")
except ResourceNotFoundError as e:
    print(f"Not found: {e.resource_type} '{e.resource_id}'")
except ValidationError as e:
    print(f"Bad request: {e}")
except AuthenticationError:
    print("Invalid API key — check your credentials")
except NetworkError as e:
    print(f"Network problem: {e}")
```

## Design Decisions

- **Session reuse**: All requests share a `requests.Session` for connection pooling
- **Client-side validation**: `days` range and `units`/`condition` enums are validated before sending the HTTP request, providing instant feedback
- **Dataclass models**: `Location`, `ForecastDay`, `Forecast`, and `WeatherAlert` give type-safe access to response fields
- **Domain exceptions**: Every error scenario has a specific exception class rather than leaking raw `requests` exceptions to callers

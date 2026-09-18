# API Specification: Weather Forecast API v1

## Base URL
`https://api.weatherforecast.example.com/v1`

## Authentication
All endpoints require a Bearer token in the `Authorization` header:
```
Authorization: Bearer <your-api-key>
```
Missing or invalid tokens return `401 Unauthorized`.

---

## Endpoints

### GET /locations
Returns a list of all tracked location IDs.

**Response `200 OK`:**
```json
{
  "locations": [
    {"id": "london-gb", "name": "London, UK", "timezone": "Europe/London"},
    {"id": "nyc-us", "name": "New York City, US", "timezone": "America/New_York"}
  ]
}
```

---

### GET /forecast/{location_id}
Returns the 7-day weather forecast for a given location.

**Path parameter:** `location_id` — string ID from `/locations`

**Query parameters:**
| Name | Type | Default | Description |
|---|---|---|---|
| `days` | integer | 7 | Number of forecast days (1–14) |
| `units` | string | `"metric"` | `"metric"` (°C) or `"imperial"` (°F) |

**Response `200 OK`:**
```json
{
  "location": {"id": "london-gb", "name": "London, UK", "timezone": "Europe/London"},
  "units": "metric",
  "forecast": [
    {
      "date": "2024-03-01",
      "high_temp": 14,
      "low_temp": 8,
      "condition": "Partly Cloudy",
      "precipitation_mm": 2.1,
      "wind_kph": 20
    }
  ]
}
```

**Errors:**
- `404 Not Found` — location ID does not exist
- `422 Unprocessable Entity` — `days` out of range (1–14) or `units` invalid

---

### POST /alerts
Create a weather alert subscription for a location.

**Request body:**
```json
{
  "location_id": "london-gb",
  "condition": "precipitation_mm",
  "threshold": 10.0,
  "notify_email": "user@example.com"
}
```

**Fields:**
| Field | Required | Description |
|---|---|---|
| `location_id` | ✅ | Location to monitor |
| `condition` | ✅ | `"precipitation_mm"`, `"high_temp"`, or `"low_temp"` |
| `threshold` | ✅ | Numeric threshold to trigger alert |
| `notify_email` | ✅ | Email address to notify |

**Response `201 Created`:**
```json
{
  "id": "alert-abc-123",
  "location_id": "london-gb",
  "condition": "precipitation_mm",
  "threshold": 10.0,
  "notify_email": "user@example.com",
  "created_at": "2024-03-01T09:00:00Z"
}
```

**Errors:**
- `400 Bad Request` — missing required fields
- `404 Not Found` — `location_id` does not exist

---

### DELETE /alerts/{alert_id}
Delete an existing weather alert.

**Path parameter:** `alert_id` — string

**Response:** `204 No Content`

**Errors:**
- `404 Not Found` — alert ID does not exist

---

## Error Format
All errors return a consistent JSON body:
```json
{
  "error": "<short error type>",
  "message": "<human-readable explanation>"
}
```

# 7.2 Python HTTP Client

## Core Concepts
Production services rarely make raw, ad-hoc HTTP calls scattered throughout application logic. Instead, they encapsulate networking behind reusable client classes that enforce uniform connection pooling, sensible timeouts, payload serialization, and structured exception translation.

## Key Requests Features
- `requests.Session()`: Maintains connection pooling via urllib3, reuses TCP connections across requests to the same host, and shares default headers (like authentication or content negotiation).
- `timeout=10.0` or `timeout=(connect_sec, read_sec)`: Enforces socket timeouts. Without this, requests will wait indefinitely on unresponsive sockets, exhausting process threads.
- `response.json()`: Deserializes JSON response text into native Python dicts/lists, raising `ValueError` on malformed payloads.

## Engineering Rules of Thumb
- **The Mandatory Timeout Rule**: By default, `requests` has NO timeout. If a remote firewall drops packets silently, your thread blocks forever. Always supply a default timeout in your client constructor.
- **Differentiating 4xx from 5xx**: Client errors (4xx) denote caller mistakes (bad payload, missing credentials, resource not found) that should not be retried without modification. Server errors (5xx) indicate upstream infrastructure distress and may be transient.

## Connection to Exercises
In `api_client.py`, the `APIClient` class wraps GET, POST, PUT, and DELETE with a managed `requests.Session`. It resolves relative URLs, sets JSON content headers, guards against connection hangs with a strict 10s default timeout, and translates HTTP 4xx/5xx responses into typed exceptions (`ClientError`, `ServerError`).

# 7.4 Error Handling & Resilience

## Why This Matters

Real APIs fail — networks time out, servers crash, and rate limits get hit. A **resilient client**
handles these failures gracefully so the application can recover automatically (where possible) and
show users clear, actionable messages (always).

---

## Key Concepts

### 1. Failure Categories

| Category | HTTP Status | Retryable? | Example |
|---|---|---|---|
| Timeout | N/A | ✅ Yes | `requests.exceptions.Timeout` |
| Connection Error | N/A | ✅ Yes | Server down, DNS failure |
| Server Error | 5xx | ✅ Yes | 500 Internal Server Error |
| Rate Limit | 429 | ✅ Yes (with delay) | Too many requests |
| Client Error | 4xx (not 429) | ❌ No | 401, 403, 404, 422 |

> **Critical rule**: Never retry 4xx client errors (except 429). The client sent a bad request —
> retrying it won't help and wastes resources.

---

### 2. Exponential Backoff

Retrying immediately after a failure usually hits the same broken state. Exponential backoff
increases wait time between each attempt:

```
attempt 0 → wait 0.5s
attempt 1 → wait 1.0s
attempt 2 → wait 2.0s (capped at backoff_max)
```

Formula: `min(base * 2^attempt, max_cap)`

In production you add **jitter** (random ±20%) to prevent multiple clients from hammering a
recovering server in lockstep ("thundering herd").

---

### 3. User-Safe Error Messages

Never expose internal errors to end users:
- Stack traces leak implementation details
- Raw exception messages are meaningless to users
- Technical details can be logged server-side for engineers

Pattern used in `resilient_client.py`:

```python
class UserFacingError(Exception):
    def __init__(self, user_message: str, technical_detail: str = "") -> None:
        self.user_message = user_message  # shown to user
        self.technical_detail = technical_detail  # logged, never displayed
```

---

### 4. Dependency Injection for Testability

`ResilientClient` accepts a `sleep_fn` parameter (defaults to `time.sleep`). Tests inject a no-op
or recording function so they don't actually wait:

```python
# production
client = ResilientClient(base_url=url)  # uses real time.sleep

# in tests
sleep_calls = []
client = ResilientClient(base_url=url, sleep_fn=sleep_calls.append)
```

This makes tests fast and the backoff logic still exercised without sleeping.

---

## Code Pattern: The Retry Loop

```python
for attempt in range(max_retries + 1):
    try:
        return make_request()
    except RetryableError as exc:
        if attempt >= max_retries:
            raise translate_to_user_error(exc)
        sleep(backoff_seconds(attempt))
```

**Note**: The loop runs `max_retries + 1` times — the initial attempt plus `max_retries` retries.

---

## Running the Simulation

```bash
cd 07-rest-api/exercises/7.4-error-handling
python failure_simulation.py
```

Expected output shows each failure mode, the user-safe message, and (for retryable errors) the
sleep calls that would have occurred between retries.

---

## Common Interview Questions

- **"What is exponential backoff?"** — Doubling wait time between retries to ease pressure on a
  struggling server.
- **"When should you NOT retry?"** — On 4xx errors (except 429): the request itself is wrong.
- **"What is circuit breaking?"** — An advanced pattern where the client "opens" and stops
  retrying entirely after a threshold of failures, preventing resource exhaustion.

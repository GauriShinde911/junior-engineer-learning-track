# Skill 07: REST APIs with Python

## What This Skill Covers

By completing this module you can build production-grade HTTP API clients in Python —
reading API specifications, writing clean request/response code, handling every failure
mode, and testing all of it without making a single real network call.

---

## Conceptual Map

```
HTTP Protocol  →  requests library  →  APIClient  →  ResilientClient
    (7.1)              (7.2)              (7.2)           (7.4)

API design / contract (7.3)  →  Testing with mocks (7.5)  →  Independent project
```

---

## Section-by-Section Summary

### 7.1 — HTTP Basics
- HTTP is a stateless request/response protocol over TCP
- **Verbs**: GET (read), POST (create), PUT/PATCH (update), DELETE (remove)
- **Status codes**: 2xx success, 3xx redirect, 4xx client error, 5xx server error
- Every HTTP message has: start line | headers | blank line | optional body
- `requests.get(url)` wraps raw socket + TCP; always check `.status_code`

### 7.2 — Python HTTP Client
- Use `requests.Session` (not module-level `requests.get`) for connection pooling and shared headers
- Set default headers (`Authorization`, `Accept`, `Content-Type`) once on the session
- Build a custom exception hierarchy: `APIClientError > HTTPStatusError > ClientError / ServerError`
- Classify errors at the HTTP status layer, not in caller code
- Key `session.request()` kwargs: `json=`, `params=`, `headers=`, `timeout=`

### 7.3 — API Design Concepts
- REST resources are nouns: `/v1/tasks`, `/v1/tasks/{id}`
- CRUD → HTTP verbs: Create=POST, Read=GET, Update=PUT/PATCH, Delete=DELETE
- Request/response contracts should be documented (OpenAPI, markdown) before coding
- In-memory stores (`TaskStore`) must use `threading.RLock` (not `Lock`) if the same thread can re-enter while holding the lock
- `Connection: close` headers are essential for `http.server` on Windows to release sockets between requests

### 7.4 — Error Handling & Resilience
| Error type | Retryable? | HTTP Status |
|---|---|---|
| Timeout | ✅ | N/A |
| Connection failure | ✅ | N/A |
| Server Error | ✅ | 5xx |
| Rate Limit | ✅ (with delay) | 429 |
| Client Error | ❌ | 4xx (except 429) |

- **Exponential backoff**: `min(base × 2^attempt, cap)` — add jitter in production
- **Dependency injection**: accept `sleep_fn` so tests don't wait real seconds
- **User-safe messages**: Never expose `traceback`, `socket`, or `urllib3` details to users
- Circuit breaking (not implemented here): stop retrying entirely after N consecutive failures

### 7.5 — Testing APIs with Mocks
- **Always patch at `session.request`**, not `requests.get` — the Session is what your client actually calls
- Use `spec=requests.Response` on mocks so typos raise `AttributeError` instead of silently passing
- Use `side_effect=exception` to test network errors; use `side_effect=[resp1, resp2, exc]` for sequences
- `@pytest.mark.parametrize` covers multiple status codes with a single test function
- `mock.call_args.args[0]` = HTTP method; `mock.call_args.kwargs["params"]` = query params

---

## Key APIs to Remember

```python
# Session-based client
session = requests.Session()
session.headers.update({"Authorization": "Bearer token"})
resp = session.request("GET", url, params={...}, json={...}, timeout=10)

# Response inspection
resp.status_code    # int
resp.json()         # dict/list (raises ValueError if not JSON)
resp.text           # raw string
resp.content        # raw bytes

# Common exceptions
requests.exceptions.Timeout          # → RequestTimeoutError
requests.exceptions.ConnectionError  # → ConnectionFailureError
```

---

## Design Checklist for Any API Client

- [ ] Use `requests.Session` — never bare `requests.get()`
- [ ] Set `Authorization`, `Accept`, `Content-Type` as default session headers
- [ ] Build a custom exception hierarchy — callers should never catch `requests.*`
- [ ] Validate input before sending (save a round-trip for obviously bad params)
- [ ] Handle `200`, `201`, `204`, `4xx`, `5xx`, `Timeout`, and `ConnectionError`
- [ ] Inject `sleep_fn` or equivalent to make retry logic testable
- [ ] Keep user-facing error messages free of internal details

---

## Common Interview Questions

**"Why use a Session instead of `requests.get`?"**
→ Sessions reuse TCP connections (connection pooling) and share headers/cookies across requests — dramatically faster for multiple calls to the same host.

**"How do you test code that makes HTTP calls?"**
→ Mock at `session.request` level with `patch.object`; never hit real APIs in unit tests.

**"When should you NOT retry a request?"**
→ On 4xx errors (except 429) — the request is wrong; retrying it won't help.

**"What is exponential backoff and why?"**
→ Doubling wait time between retries prevents a struggling server from being overwhelmed by clients hammering it simultaneously.

**"What's the difference between REST and HTTP?"**
→ HTTP is the transport protocol. REST is an architectural style using HTTP conventions (verbs, status codes, resource URLs) consistently.

---

## Running the Full Test Suite

```bash
cd 07-rest-api
python -m pytest tests/ -v        # Run all section tests
python -m pytest independent/ -v  # Run independent project tests
python -m pytest -v               # Run everything
```

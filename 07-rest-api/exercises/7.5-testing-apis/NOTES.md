# 7.5 Testing APIs with Mocks

## Why Mock API Calls in Tests?

Tests that hit real APIs are:
- **Slow** — network round-trips add 100ms–10s per call
- **Flaky** — fail on rate limits, outages, or credential changes
- **Expensive** — API calls may cost money or mutate real data
- **Hard to trigger** — can't easily force a 500, timeout, or 404 on demand

Mocking replaces the real HTTP transport with a controlled fake, so you can
test every branch of your client code fast and deterministically.

---

## The Mocking Target: Patch at the Right Level

For a `requests.Session`-based client, patch `session.request` (the method
that ultimately sends every HTTP call), NOT the high-level functions like
`requests.get`:

```python
# ✅ Correct — patches exactly what APIClient calls
with patch.object(client.session, "request", return_value=mock_response):
    result = client.get("/items")

# ❌ Wrong — APIClient uses its own Session object, not the module-level function
with patch("requests.get", return_value=mock_response):
    ...
```

**Key rule**: Patch where the code looks up the function, not where it is defined.

---

## Building a Useful Mock Response

```python
from unittest.mock import Mock
import requests

def mock_response(status_code: int, body: dict) -> Mock:
    m = Mock(spec=requests.Response)
    m.status_code = status_code
    m.json.return_value = body
    import json
    m.content = json.dumps(body).encode()
    return m
```

Using `spec=requests.Response` ensures the mock only exposes attributes that
the real `Response` object has — typos like `m.stats_code` will raise an
`AttributeError` instead of silently passing.

---

## Test Strategy: What to Verify

| What | How |
|---|---|
| Happy path → returns parsed body | assert `result == expected_dict` |
| 4xx → raises `ClientError` | `pytest.raises(ClientError)` |
| 5xx → raises `ServerError` | `pytest.raises(ServerError)` |
| Network timeout → raises `RequestTimeoutError` | `side_effect=requests.exceptions.Timeout()` |
| Correct HTTP verb sent | inspect `mock.call_args.args[0]` |
| Query params forwarded | inspect `mock.call_args.kwargs["params"]` |
| Session reused | same mock called N times across N client calls |

---

## Parametrize for Coverage Efficiency

Use `@pytest.mark.parametrize` to test multiple status codes with one test:

```python
@pytest.mark.parametrize("code", [400, 401, 403, 404, 422])
def test_client_error_codes_raise_client_error(client, code):
    resp = mock_response(code, {"error": "bad"})
    with patch.object(client.session, "request", return_value=resp):
        with pytest.raises(ClientError):
            client.get("/resource")
```

---

## `side_effect` vs `return_value`

| Use case | Syntax |
|---|---|
| Return a fixed response | `patch(..., return_value=mock_resp)` |
| Simulate an exception | `patch(..., side_effect=requests.exceptions.Timeout())` |
| Return different values on successive calls | `patch(..., side_effect=[resp1, resp2, exc])` |
| Inspect what was called | `mock_fn.call_args` or `mock_fn.call_args_list` |

---

## Running the Tests

```bash
# Run only 7.5 mocked tests
cd 07-rest-api
python -m pytest exercises/7.5-testing-apis/test_api_client_mocked.py -v

# Or via the main test runner
python -m pytest tests/test_7_5_testing_apis.py -v
```

---

## Common Pitfalls

- **Forgetting `spec=`**: Mock will accept any attribute access without
  `spec`, masking bugs from typos.
- **Patching the wrong namespace**: If `api_client.py` does
  `import requests; requests.get(...)`, patch `api_client.requests.get`, not
  `requests.get`.
- **Not asserting call args**: Testing that the mock was called is not enough —
  also verify the URL, method, and params were correct.
- **Mocking too deep**: Mocking at the `socket` level is fragile; prefer
  mocking at the library level (`session.request`).

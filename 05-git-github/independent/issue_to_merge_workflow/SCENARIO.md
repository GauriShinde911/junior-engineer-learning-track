# GitHub Issue #87: [Feature] Implement Sliding Window Rate Limiter

## Metadata
- **Issue ID**: #87
- **Labels**: `enhancement`, `backend`, `security`
- **Assignee**: `@you`
- **Milestone**: v1.2 Core Security

---

## User Story
**As an** API Gateway engineer  
**I want** an in-memory sliding-window rate limiter  
**So that** abusive clients cannot overwhelm our backend services with unbounded request spikes.

---

## Problem Statement
Our authentication and search endpoints currently lack client throttling. Malicious or misconfigured clients can trigger excessive compute cycles. We need a clean, zero-dependency Python rate limiter class ready for integration into our request processing pipeline.

---

## Acceptance Criteria
- [ ] Implement class `RateLimiter(max_requests: int, window_seconds: float)` in `rate_limiter.py`.
- [ ] Implement method `is_allowed(client_id: str, current_time: float | None = None) -> bool`:
  - Returns `True` if the client has sent fewer than `max_requests` in the trailing `window_seconds`.
  - Returns `False` if the limit is exceeded.
  - Cleans up / evicts timestamps older than `window_seconds`.
- [ ] Thread-safe or memory-safe eviction: avoids unbounded memory leaks for stale client IDs.
- [ ] Comprehensive unit tests in `test_rate_limiter.py` covering:
  - Allowing requests below threshold.
  - Blocking requests exceeding `max_requests`.
  - Allowing new requests once the sliding time window elapses.
  - Independent tracking across distinct client IDs.
- [ ] All tests pass via `python test_rate_limiter.py`.

---

## Technical Specifications & Tips
- Store timestamps in a `collections.deque` or `list` keyed by `client_id` in a dictionary.
- Allow injecting `current_time` as a parameter to simplify deterministic unit testing without requiring real-time `time.sleep()` delays.
- Follow PEP 8 and conventional commit guidelines (`feat:`, `test:`, `docs:`).

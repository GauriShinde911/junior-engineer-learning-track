# 7.3 API Design Concepts

## Core Concepts
REST (Representational State Transfer) is an architectural style emphasizing resource-oriented URIs, stateless communication, standard HTTP methods, and uniform interfaces. High-quality API design decouples client implementations from server internals.

## Key REST Architectural Guidelines
- **Nouns, Not Verbs**: Use plural nouns to model resources (`/v1/tasks`), never RPC-style action verbs (`/v1/createTask` or `/v1/deleteTaskById`). The HTTP verb already expresses the action.
- **Idempotency**:
  - `GET`, `PUT`, `DELETE`: Idempotent (calling them multiple times with identical arguments results in the exact same server resource state).
  - `POST`: Non-idempotent (calling it 3 times creates 3 separate resources).
- **Versioning**: Prefix endpoints with major versions (e.g., `/v1/`) to enable breaking schema changes without disrupting legacy consumers.
- **Pagination & Filtering**: Avoid returning unbounded collections. Provide standard query parameters (`limit`, `offset`, or cursor tokens) and resource filters (`?status=pending`).
- **Standard Header Conventions**:
  - Request: `Authorization: Bearer <token>`, `Content-Type: application/json`
  - Response: `Location: /v1/tasks/42` when returning `201 Created`.

## Connection to Exercises
In `api_contract.md`, we design a complete REST specification for `/v1/tasks` encompassing auth gates, pagination metadata, and status validation. In `mock_server.py`, a standard library `http.server` implementation enforces this contract, returning appropriate status codes (`200`, `201`, `204`, `400`, `401`, `404`).

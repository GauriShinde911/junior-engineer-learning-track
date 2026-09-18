# 7.1 HTTP Basics

## Core Concepts
Hypertext Transfer Protocol (HTTP) is the stateless, client-server application-layer protocol powering the web and REST APIs. Every interaction follows a discrete request-response cycle consisting of an HTTP verb, target URI, request headers, an optional payload body, and a structured server response.

## Key HTTP Components
- **Methods (Verbs)**: `GET` (retrieve resource, safe & idempotent), `POST` (create resource, non-idempotent), `PUT` (full resource replacement, idempotent), `DELETE` (remove resource, idempotent), `PATCH` (partial resource modification).
- **URLs & Parameters**: Scheme (`https://`), host (`api.service.com`), path (`/v1/users/42`), and query parameters (`?limit=10&status=active`) used for filtering, searching, and pagination.
- **Headers**: Key-value pairs transmitting protocol metadata. E.g., `Content-Type: application/json` describes request payload format, while `Accept: application/json` declares desired response format.
- **Status Code Classes**:
  - `2xx Success`: `200 OK`, `201 Created`, `204 No Content`
  - `3xx Redirection`: `301 Moved Permanently`, `304 Not Modified`
  - `4xx Client Error`: `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`
  - `5xx Server Error`: `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout`

## Connection to Exercises
In `inspect_requests.py`, `make_get_request` and `make_post_request` issue live calls against HTTP echo endpoints. By inspecting `response.request.headers`, `response.url`, and `response.status_code`, we observe firsthand how query parameters append to URLs and how JSON dictionaries serialize over wire transmissions.

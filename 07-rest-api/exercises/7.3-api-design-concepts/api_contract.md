# API Specification Contract: Task Management Service (v1)

## Base URL & Versioning
- **Base URI**: `https://api.example.com/v1`
- **Versioning Strategy**: URI Path Versioning (`/v1/`), ensuring backward compatibility when major schemas change.

---

## Authentication & Security
All endpoints require a valid Bearer token in the `Authorization` request header:
```http
Authorization: Bearer test-token-123
```
- Missing or invalid token responses:
  - **Status Code**: `401 Unauthorized`
  - **Body**: `{"error": "Unauthorized", "message": "Valid Bearer token required"}`

---

## Resource Schema: Task

```json
{
  "id": 1,
  "title": "Implement API Rate Limiting",
  "status": "pending",
  "priority": "high",
  "created_at": "2026-09-18T10:00:00Z"
}
```

- `id`: integer (read-only, auto-generated)
- `title`: string, required, non-empty
- `status`: string, enum: `["pending", "in_progress", "completed"]` (default: `"pending"`)
- `priority`: string, enum: `["low", "medium", "high"]` (default: `"medium"`)
- `created_at`: ISO 8601 UTC timestamp string (read-only)

---

## Endpoints Specification

### 1. List Tasks (with Filtering & Pagination)
- **Method / Path**: `GET /v1/tasks`
- **Query Parameters**:
  - `status` (optional): Filter tasks by exact status (`pending`, `in_progress`, `completed`).
  - `limit` (optional, default: `10`, max: `100`): Maximum items to return.
  - `offset` (optional, default: `0`): Number of items to skip.
- **Success Response**: `200 OK`
```json
{
  "items": [ ... ],
  "pagination": {
    "total": 45,
    "limit": 10,
    "offset": 0
  }
}
```

### 2. Create Task
- **Method / Path**: `POST /v1/tasks`
- **Request Body**:
```json
{
  "title": "Build integration tests",
  "priority": "high"
}
```
- **Success Response**: `201 Created`
  - Headers: `Location: /v1/tasks/2`
  - Body: Complete created Task resource.
- **Validation Failure**: `400 Bad Request` if `title` is missing or invalid enum passed.

### 3. Retrieve Task by ID
- **Method / Path**: `GET /v1/tasks/{id}`
- **Success Response**: `200 OK` (returns Task JSON).
- **Error Response**: `404 Not Found` if `id` does not exist.

### 4. Update Task (Full Replacement / Idempotent)
- **Method / Path**: `PUT /v1/tasks/{id}`
- **Request Body**:
```json
{
  "title": "Updated Task Title",
  "status": "completed",
  "priority": "low"
}
```
- **Success Response**: `200 OK` (returns updated Task JSON).
- **Error Response**: `404 Not Found` if `id` does not exist; `400 Bad Request` on invalid payload.

### 5. Delete Task (Idempotent)
- **Method / Path**: `DELETE /v1/tasks/{id}`
- **Success Response**: `204 No Content` (empty body).
- **Error Response**: `404 Not Found` if `id` does not exist.

---

## Idempotency Matrix
| Method | Idempotent? | Safe? | Description |
|---|---|---|---|
| `GET` | Yes | Yes | Read-only; leaves server state unmodified. |
| `POST` | No | No | Multiple identical calls create multiple distinct resources. |
| `PUT` | Yes | No | Repeating identical update produces identical end state. |
| `DELETE`| Yes | No | Subsequent deletes on already deleted resource result in same end state. |

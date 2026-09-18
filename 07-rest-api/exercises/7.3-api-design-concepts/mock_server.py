"""
exercises/7.3-api-design-concepts/mock_server.py
Minimal, zero-dependency reference implementation of api_contract.md using Python's http.server.
Provides a realistic local test server supporting CRUD, query pagination, filtering, and auth.
"""

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse
import json
import re
import threading

EXPECTED_BEARER_TOKEN = "test-token-123"


class TaskStore:
    """Thread-safe in-memory store for Task resources."""

    def __init__(self) -> None:
        self._lock = threading.RLock()  # RLock allows re-entrant acquisition within the same thread
        self._counter = 0
        self._tasks: Dict[int, Dict[str, Any]] = {}
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._counter = 0
            self._tasks.clear()
            # Seed with 2 default tasks
            self.create({"title": "Initial Task A", "status": "pending", "priority": "medium"})
            self.create({"title": "Initial Task B", "status": "completed", "priority": "high"})

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            self._counter += 1
            task_id = self._counter
            task = {
                "id": task_id,
                "title": data["title"],
                "status": data.get("status", "pending"),
                "priority": data.get("priority", "medium"),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._tasks[task_id] = task
            return dict(task)

    def get(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._lock:
            task = self._tasks.get(task_id)
            return dict(task) if task else None

    def list_all(
        self,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list, int]:
        with self._lock:
            items = list(self._tasks.values())
            if status:
                items = [t for t in items if t["status"].lower() == status.lower()]
            total = len(items)
            paginated = items[offset : offset + limit]
            return [dict(t) for t in paginated], total

    def update(self, task_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self._lock:
            if task_id not in self._tasks:
                return None
            task = self._tasks[task_id]
            task["title"] = data.get("title", task["title"])
            task["status"] = data.get("status", task["status"])
            task["priority"] = data.get("priority", task["priority"])
            return dict(task)

    def delete(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None


_store = TaskStore()


class TaskRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler implementing the api_contract.md endpoints."""

    def log_message(self, format: str, *args: Any) -> None:
        """Silence standard console logging during automated tests."""
        pass

    def _send_json(self, status_code: int, data: Any = None, headers: Optional[Dict[str, str]] = None) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Connection", "close")
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        if data is not None:
            payload = json.dumps(data).encode("utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_header("Content-Length", "0")
            self.end_headers()
        self.close_connection = True

    def _authenticate(self) -> bool:
        auth_header = self.headers.get("Authorization", "")
        if auth_header != f"Bearer {EXPECTED_BEARER_TOKEN}":
            self._send_json(401, {"error": "Unauthorized", "message": "Valid Bearer token required"})
            return False
        return True

    def _read_json_body(self) -> Optional[Dict[str, Any]]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return None
        raw_body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw_body)
        except ValueError:
            return None

    def do_GET(self) -> None:
        if not self._authenticate():
            return

        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)

        # 1. GET /v1/tasks (collection)
        if path == "/v1/tasks":
            status_filter = query_params.get("status", [None])[0]
            try:
                limit = int(query_params.get("limit", [10])[0])
                offset = int(query_params.get("offset", [0])[0])
            except ValueError:
                self._send_json(400, {"error": "Bad Request", "message": "limit and offset must be integers"})
                return

            items, total = _store.list_all(status=status_filter, limit=limit, offset=offset)
            self._send_json(200, {"items": items, "pagination": {"total": total, "limit": limit, "offset": offset}})
            return

        # 2. GET /v1/tasks/{id} (single item)
        match = re.match(r"^/v1/tasks/(\d+)$", path)
        if match:
            task_id = int(match.group(1))
            task = _store.get(task_id)
            if task:
                self._send_json(200, task)
            else:
                self._send_json(404, {"error": "Not Found", "message": f"Task {task_id} not found"})
            return

        self._send_json(404, {"error": "Not Found", "message": "Endpoint does not exist"})

    def do_POST(self) -> None:
        if not self._authenticate():
            return

        if self.path != "/v1/tasks":
            self._send_json(404, {"error": "Not Found", "message": "Endpoint does not exist"})
            return

        body = self._read_json_body()
        if not body or "title" not in body or not str(body["title"]).strip():
            self._send_json(400, {"error": "Bad Request", "message": "Field 'title' is required and non-empty"})
            return

        created = _store.create(body)
        self._send_json(201, created, headers={"Location": f"/v1/tasks/{created['id']}"})

    def do_PUT(self) -> None:
        if not self._authenticate():
            return

        match = re.match(r"^/v1/tasks/(\d+)$", self.path)
        if not match:
            self._send_json(404, {"error": "Not Found", "message": "Endpoint does not exist"})
            return

        task_id = int(match.group(1))
        body = self._read_json_body()
        if not body:
            self._send_json(400, {"error": "Bad Request", "message": "Request body must be valid JSON"})
            return

        updated = _store.update(task_id, body)
        if updated:
            self._send_json(200, updated)
        else:
            self._send_json(404, {"error": "Not Found", "message": f"Task {task_id} not found"})

    def do_DELETE(self) -> None:
        if not self._authenticate():
            return

        match = re.match(r"^/v1/tasks/(\d+)$", self.path)
        if not match:
            self._send_json(404, {"error": "Not Found", "message": "Endpoint does not exist"})
            return

        task_id = int(match.group(1))
        deleted = _store.delete(task_id)
        if deleted:
            self._send_json(204)
        else:
            self._send_json(404, {"error": "Not Found", "message": f"Task {task_id} not found"})


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run standalone server for manual exploration."""
    server = HTTPServer((host, port), TaskRequestHandler)
    print(f"Starting Mock Task API server on http://{host}:{port}/v1/tasks")
    print(f"Authorization: Bearer {EXPECTED_BEARER_TOKEN}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()


if __name__ == "__main__":
    run_server()

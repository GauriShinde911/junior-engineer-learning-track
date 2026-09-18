"""
exercises/6.5-integration-tests/db_repository.py
Self-contained SQLite-backed repository demonstrating real database persistence.
Used to showcase true integration testing against an actual relational database engine.
"""

from typing import Any, Dict, List, Optional
import sqlite3


class TaskRepository:
    """Repository handling persistence of task records in SQLite."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Establish connection with row factory enabled."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            # Enforce foreign keys and integrity constraints
            self._connection.execute("PRAGMA foreign_keys = ON;")
        return self._connection

    def close(self) -> None:
        """Close connection if open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def init_schema(self) -> None:
        """Initialize database table schema."""
        conn = self.connect()
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority TEXT CHECK(priority IN ('low', 'normal', 'high', 'critical')) DEFAULT 'normal',
                    is_completed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def create_task(self, title: str, description: str = "", priority: str = "normal") -> int:
        """Insert a new task into the database."""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        valid_priorities = {"low", "normal", "high", "critical"}
        if priority not in valid_priorities:
            raise ValueError(f"Invalid priority '{priority}', must be one of {valid_priorities}")

        conn = self.connect()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (title, description, priority, is_completed)
                VALUES (?, ?, ?, 0);
                """,
                (title.strip(), description.strip(), priority),
            )
            return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve task by primary key."""
        conn = self.connect()
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ?;", (task_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def list_tasks(
        self,
        include_completed: bool = True,
        priority: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query tasks with optional filtering."""
        conn = self.connect()
        query = "SELECT * FROM tasks WHERE 1=1"
        params: List[Any] = []

        if not include_completed:
            query += " AND is_completed = 0"
        if priority is not None:
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY id ASC;"
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def mark_completed(self, task_id: int) -> bool:
        """Mark a task as completed."""
        conn = self.connect()
        with conn:
            cursor = conn.execute(
                "UPDATE tasks SET is_completed = 1 WHERE id = ?;",
                (task_id,),
            )
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        conn = self.connect()
        with conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
            return cursor.rowcount > 0

    def count(self) -> int:
        """Return total count of tasks."""
        conn = self.connect()
        cursor = conn.execute("SELECT COUNT(*) FROM tasks;")
        return cursor.fetchone()[0]

"""
exercises/6.5-integration-tests/test_db_repository_integration.py
Genuine integration test exercising a real SQLite database on temporary disk.

WHY THIS IS AN INTEGRATION TEST (NOT A UNIT TEST):
--------------------------------------------------
1. Real Boundary Interaction:
   Unlike the mocked tests in 6.4 which replace dependencies with Fake/Mock objects,
   these tests interact with a real SQLite relational database engine operating on
   actual disk files managed by pytest's `tmp_path`.

2. Verifying Real System Contracts:
   Unit test mocks only verify what you program them to return. They CANNOT detect:
   - SQL syntax errors in queries or DDL schema.
   - Relational constraint violations (CHECK constraints, NOT NULL constraints, AUTOINCREMENT).
   - Real type conversions between Python types and SQLite storage classes.
   - Transaction commit and rollback behavior.

By using a real temporary database, we test the true integration between our Python
data-access code and the underlying storage system while preserving test isolation.
"""

from pathlib import Path
import sqlite3
from typing import Generator
import pytest

from db_repository import TaskRepository


@pytest.fixture
def temp_repo(tmp_path: Path) -> Generator[TaskRepository, None, None]:
    """Integration fixture provisioning a fresh SQLite database on disk for each test."""
    db_file = tmp_path / "test_tasks.db"
    repo = TaskRepository(str(db_file))
    repo.init_schema()

    yield repo

    # Teardown: ensure connections are closed cleanly to release file locks on Windows
    repo.close()


def test_create_and_retrieve_task(temp_repo: TaskRepository):
    """Verify task insertion generates real auto-incremented primary key and persists to SQLite."""
    task_id = temp_repo.create_task(
        title="Deploy CI Pipeline",
        description="Configure GitHub Actions test runner",
        priority="high",
    )

    assert task_id == 1

    fetched = temp_repo.get_task(task_id)
    assert fetched is not None
    assert fetched["id"] == 1
    assert fetched["title"] == "Deploy CI Pipeline"
    assert fetched["description"] == "Configure GitHub Actions test runner"
    assert fetched["priority"] == "high"
    assert fetched["is_completed"] == 0


def test_mark_completed_lifecycle(temp_repo: TaskRepository):
    """Verify state transition persists across SQL update statements."""
    task_id = temp_repo.create_task("Fix Flaky Test")

    initial = temp_repo.get_task(task_id)
    assert initial["is_completed"] == 0

    updated = temp_repo.mark_completed(task_id)
    assert updated is True

    persisted = temp_repo.get_task(task_id)
    assert persisted["is_completed"] == 1


def test_list_tasks_with_filtering(temp_repo: TaskRepository):
    """Verify SQL WHERE filtering on priority and completion state."""
    temp_repo.create_task("Task A", priority="critical")
    temp_repo.create_task("Task B", priority="low")
    task_c_id = temp_repo.create_task("Task C", priority="critical")
    temp_repo.mark_completed(task_c_id)

    # Filter by priority
    critical_tasks = temp_repo.list_tasks(priority="critical")
    assert len(critical_tasks) == 2
    assert {t["title"] for t in critical_tasks} == {"Task A", "Task C"}

    # Filter out completed tasks
    active_tasks = temp_repo.list_tasks(include_completed=False)
    assert len(active_tasks) == 2
    assert {t["title"] for t in active_tasks} == {"Task A", "Task B"}

    # Combined filter
    active_critical = temp_repo.list_tasks(include_completed=False, priority="critical")
    assert len(active_critical) == 1
    assert active_critical[0]["title"] == "Task A"


def test_delete_task_removes_record(temp_repo: TaskRepository):
    """Verify deletion removes record and decreases total row count."""
    task_id = temp_repo.create_task("Ephemeral task")
    assert temp_repo.count() == 1

    deleted = temp_repo.delete_task(task_id)
    assert deleted is True
    assert temp_repo.count() == 0
    assert temp_repo.get_task(task_id) is None


def test_sqlite_check_constraint_enforced_by_engine(temp_repo: TaskRepository):
    """Verify SQLite's native CHECK constraint rejects invalid priorities.

    Mocks cannot verify this behavior; only a real database engine can enforce it.
    """
    conn = temp_repo.connect()
    with pytest.raises(sqlite3.IntegrityError):
        with conn:
            # Bypass application-level validation to test database-level schema constraints
            conn.execute(
                "INSERT INTO tasks (title, priority) VALUES (?, ?);",
                ("Raw SQL task", "invalid_priority_tier"),
            )

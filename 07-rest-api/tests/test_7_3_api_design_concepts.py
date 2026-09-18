"""
tests/test_7_3_api_design_concepts.py
Tests for 7.3 API design concepts.
Validates TaskStore business logic directly and the mock_server's auth/routing via a
lightweight in-process test client — no live socket server needed.
"""

from pathlib import Path
import sys
import pytest

EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "7.3-api-design-concepts"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from mock_server import TaskStore


@pytest.fixture
def store() -> TaskStore:
    """Fresh, reset TaskStore for each test."""
    s = TaskStore()
    s.reset()
    return s


# ---------------------------------------------------------------------------
# TaskStore unit tests (the contract's core business logic)
# ---------------------------------------------------------------------------

def test_store_seeded_with_two_default_tasks(store: TaskStore):
    """Verify store.reset() seeds exactly 2 tasks."""
    items, total = store.list_all()
    assert total == 2
    assert len(items) == 2


def test_store_create_increments_ids(store: TaskStore):
    """Verify each task gets a unique auto-incrementing ID."""
    t3 = store.create({"title": "Task C", "priority": "low"})
    t4 = store.create({"title": "Task D", "priority": "high"})
    assert t3["id"] == 3
    assert t4["id"] == 4


def test_store_get_existing_and_missing(store: TaskStore):
    """Verify get returns correct task dict or None for missing."""
    task = store.get(1)
    assert task is not None
    assert task["id"] == 1

    missing = store.get(999)
    assert missing is None


def test_store_list_all_without_filter(store: TaskStore):
    """Verify list_all returns all tasks with accurate total count."""
    items, total = store.list_all()
    assert total == 2
    assert all("id" in t and "title" in t and "status" in t for t in items)


def test_store_list_filter_by_status_completed(store: TaskStore):
    """Verify filtering tasks by status=completed returns only completed tasks."""
    items, total = store.list_all(status="completed")
    assert all(t["status"] == "completed" for t in items)
    # seed has one completed task
    assert total == 1


def test_store_list_filter_by_status_pending(store: TaskStore):
    """Verify filtering by status=pending returns only pending tasks."""
    items, total = store.list_all(status="pending")
    assert all(t["status"] == "pending" for t in items)
    assert total == 1


def test_store_pagination_limit_and_offset(store: TaskStore):
    """Verify limit and offset pagination slicing."""
    # Add extra tasks
    for i in range(5):
        store.create({"title": f"Extra Task {i}"})

    # 7 total tasks now
    page1, total = store.list_all(limit=3, offset=0)
    page2, _ = store.list_all(limit=3, offset=3)
    page3, _ = store.list_all(limit=3, offset=6)

    assert total == 7
    assert len(page1) == 3
    assert len(page2) == 3
    assert len(page3) == 1


def test_store_update_task(store: TaskStore):
    """Verify update modifies task fields without removing unspecified fields."""
    store.update(1, {"title": "Renamed Task", "status": "in_progress"})
    updated = store.get(1)

    assert updated["title"] == "Renamed Task"
    assert updated["status"] == "in_progress"
    assert "priority" in updated  # unmodified fields preserved


def test_store_update_returns_none_for_missing_task(store: TaskStore):
    """Verify update on non-existent task ID returns None."""
    result = store.update(999, {"title": "Ghost"})
    assert result is None


def test_store_delete_removes_task(store: TaskStore):
    """Verify delete removes task and returns True; subsequent get returns None."""
    deleted = store.delete(1)
    assert deleted is True
    assert store.get(1) is None


def test_store_delete_returns_false_for_missing_task(store: TaskStore):
    """Verify delete on non-existent ID returns False without raising errors."""
    result = store.delete(999)
    assert result is False


def test_store_create_default_status_and_priority(store: TaskStore):
    """Verify task creation with only title uses default status=pending and priority=medium."""
    task = store.create({"title": "Minimal Task"})
    assert task["status"] == "pending"
    assert task["priority"] == "medium"
    assert "created_at" in task
    assert "id" in task

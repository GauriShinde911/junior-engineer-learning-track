"""Unit tests for Exercise 9.3 TaskStore and shared components logic.

================================================================================
TESTING NOTE: STREAMLIT UI vs. DATA & COMPONENT LOGIC
Streamlit multi-page routing is orchestrated by the Streamlit runner at runtime.
However, the shared backend data model and business logic governing Create, View,
and Delete operations reside in `TaskStore` within `components.py` and are 100%
unit testable without Streamlit.
- COVERED: Task creation with ID assignment, priority validation, retrieval,
  deletion, and DataFrame serialization.
- NOT COVERED: Visual sidebar page switching and page rendering.
================================================================================
"""

import sys
from pathlib import Path
import pytest

exercise_dir = Path(__file__).resolve().parent.parent / "exercises" / "9.3-multi-page-apps"
sys.path.insert(0, str(exercise_dir))

from components import TaskStore, TaskItem


@pytest.fixture
def store():
    return TaskStore()


def test_task_store_initialization_seed(store):
    """Verifies that store initializes with default seed tasks."""
    tasks = store.get_all_tasks()
    assert len(tasks) == 3
    assert any(t.title == "Deploy v2.4 to Staging" for t in tasks)


def test_add_task_validates_and_creates(store):
    """Verifies adding a task creates an incremented ID and valid TaskItem."""
    item = store.add_task(
        title="Setup CI/CD Pipeline",
        priority="High",
        assignee="David",
        status="Pending"
    )
    assert item.id.startswith("TSK-")
    assert item.title == "Setup CI/CD Pipeline"
    assert item.priority == "High"
    assert item.assignee == "David"

    retrieved = store.get_task(item.id)
    assert retrieved is not None
    assert retrieved.title == "Setup CI/CD Pipeline"


def test_add_task_rejects_invalid_inputs(store):
    """Verifies validation errors on title length and invalid priority."""
    with pytest.raises(ValueError) as exc:
        store.add_task("", "High", "Alice")
    assert "at least 3 characters" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        store.add_task("Valid Title", "SuperUrgent", "Alice")
    assert "Invalid priority" in str(exc.value)


def test_delete_task_success_and_missing(store):
    """Verifies deleting an existing task removes it, while non-existent returns False."""
    item = store.add_task("Temporary Task", "Low", "Bob")
    assert store.get_task(item.id) is not None

    deleted = store.delete_task(item.id)
    assert deleted is True
    assert store.get_task(item.id) is None

    # Deleting non-existent task returns False
    assert store.delete_task("TSK-9999") is False


def test_task_store_to_dataframe(store):
    """Verifies DataFrame conversion format."""
    df = store.to_dataframe()
    assert not df.empty
    assert list(df.columns) == ["id", "title", "priority", "assignee", "status"]
    assert len(df) == len(store.get_all_tasks())

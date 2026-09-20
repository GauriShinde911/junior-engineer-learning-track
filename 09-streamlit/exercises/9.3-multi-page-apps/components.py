"""Shared reusable UI components and in-memory store for 9.3 Multi-page App."""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import pandas as pd
import streamlit as st


@dataclass
class TaskItem:
    id: str
    title: str
    priority: str
    assignee: str
    status: str = "Pending"


class TaskStore:
    """In-memory data store for the multi-page task manager."""

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskItem] = {}
        self._next_id: int = 1
        self._seed_initial_data()

    def _seed_initial_data(self) -> None:
        self.add_task("Deploy v2.4 to Staging", "High", "Alice", "In Progress")
        self.add_task("Review IAM Security Policies", "Critical", "Carol", "Pending")
        self.add_task("Update Documentation & Diagrams", "Low", "Bob", "Completed")

    def add_task(self, title: str, priority: str, assignee: str, status: str = "Pending") -> TaskItem:
        if not title or len(title.strip()) < 3:
            raise ValueError("Task title must be at least 3 characters.")
        if priority not in {"Low", "Medium", "High", "Critical"}:
            raise ValueError(f"Invalid priority: {priority}")

        task_id = f"TSK-{self._next_id:04d}"
        self._next_id += 1
        item = TaskItem(
            id=task_id,
            title=title.strip(),
            priority=priority,
            assignee=assignee.strip(),
            status=status
        )
        self._tasks[task_id] = item
        return item

    def get_all_tasks(self) -> List[TaskItem]:
        return list(self._tasks.values())

    def get_task(self, task_id: str) -> Optional[TaskItem]:
        return self._tasks.get(task_id)

    def delete_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def to_dataframe(self) -> pd.DataFrame:
        if not self._tasks:
            return pd.DataFrame(columns=["id", "title", "priority", "assignee", "status"])
        return pd.DataFrame([asdict(t) for t in self._tasks.values()])


def get_or_create_store() -> TaskStore:
    """Retrieves or creates TaskStore in st.session_state so data is shared across pages."""
    if "task_store" not in st.session_state:
        st.session_state.task_store = TaskStore()
    return st.session_state.task_store


# ==============================================================================
# Reusable Streamlit UI Components
# ==============================================================================

def render_page_header(title: str, subtitle: str) -> None:
    """Renders standardized header across all sub-pages."""
    st.title(title)
    st.caption(subtitle)
    st.divider()


def render_task_summary_metrics(store: TaskStore) -> None:
    """Renders reusable KPI summary cards."""
    tasks = store.get_all_tasks()
    total = len(tasks)
    critical_count = sum(1 for t in tasks if t.priority == "Critical")
    completed_count = sum(1 for t in tasks if t.status == "Completed")
    in_progress_count = sum(1 for t in tasks if t.status == "In Progress")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", total)
    col2.metric("In Progress", in_progress_count)
    col3.metric("Critical Priority", critical_count)
    col4.metric("Completed", completed_count)


def render_styled_table(df: pd.DataFrame) -> None:
    """Renders reusable sortable data table."""
    if df.empty:
        st.info("No records to display.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

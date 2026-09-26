"""
Daily Task Tracker CLI (sample_app)
A lightweight command-line tool for logging, listing, and tracking daily tasks.
Stores data locally in JSON format.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_DATA_FILE = "tasks.json"


def get_storage_path() -> Path:
    """Resolve storage path from environment variable or default local file."""
    env_path = os.environ.get("TASK_TRACKER_DATA")
    if env_path:
        return Path(env_path)
    return Path(DEFAULT_DATA_FILE)


def load_tasks(filepath: Path) -> list:
    """Load task list from JSON file."""
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(filepath: Path, tasks: list) -> None:
    """Save task list to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def add_task(title: str, priority: str = "medium") -> dict:
    """Add a new task and save to storage."""
    filepath = get_storage_path()
    tasks = load_tasks(filepath)
    new_id = (max([t.get("id", 0) for t in tasks], default=0)) + 1
    task = {
        "id": new_id,
        "title": title.strip(),
        "priority": priority.lower(),
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tasks.append(task)
    save_tasks(filepath, tasks)
    return task


def list_tasks(show_all: bool = False) -> list:
    """Return tasks, filtering out completed tasks unless show_all is True."""
    filepath = get_storage_path()
    tasks = load_tasks(filepath)
    if show_all:
        return tasks
    return [t for t in tasks if not t.get("completed", False)]


def complete_task(task_id: int) -> bool:
    """Mark a task as completed."""
    filepath = get_storage_path()
    tasks = load_tasks(filepath)
    updated = False
    for t in tasks:
        if t.get("id") == task_id:
            t["completed"] = True
            updated = True
            break
    if updated:
        save_tasks(filepath, tasks)
    return updated


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="task-tracker",
        description="Daily Task Tracker - Manage and record personal tasks from the command line."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title or description")
    add_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        default="medium",
        help="Task priority level (default: medium)"
    )

    # list
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Include completed tasks in the output"
    )

    # complete
    comp_parser = subparsers.add_parser("complete", help="Mark a task as completed")
    comp_parser.add_argument("id", type=int, help="ID of task to complete")

    return parser.parse_args(args)


def main(args=None) -> int:
    parsed = parse_args(args)
    if not parsed.command:
        print("Daily Task Tracker CLI. Use --help to view available commands.")
        return 0

    if parsed.command == "add":
        task = add_task(parsed.title, parsed.priority)
        print(f"[OK] Added task #{task['id']}: '{task['title']}' (priority: {task['priority']})")
        return 0

    if parsed.command == "list":
        tasks = list_tasks(show_all=parsed.all)
        if not tasks:
            print("No tasks found.")
            return 0
        print(f"{'ID':<4} {'Status':<10} {'Priority':<10} {'Title':<30} {'Created'}")
        print("-" * 75)
        for t in tasks:
            status = "Done" if t.get("completed") else "Pending"
            print(f"{t['id']:<4} {status:<10} {t.get('priority', 'medium'):<10} {t['title']:<30} {t.get('created_at', '')}")
        return 0

    if parsed.command == "complete":
        success = complete_task(parsed.id)
        if success:
            print(f"[OK] Task #{parsed.id} marked as completed.")
            return 0
        else:
            print(f"[ERROR] Task #{parsed.id} not found.", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

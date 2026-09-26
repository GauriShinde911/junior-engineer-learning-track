"""
defect_2.py - Defect Scenario 2: Lexicographical vs Numerical Sorting

Symptom:
Pagination and priority queues order items unpredictably: priority score "100" is placed
behind "20", and chapter "10" appears before chapter "2".
"""

from typing import List, Dict, Any


def sort_by_priority_buggy(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    BUGGY IMPLEMENTATION:
    Sorts dictionary records by the 'priority' key directly.
    When priority values are strings (e.g. from JSON/CSV), Python sorts lexicographically:
    '10' < '2' < '20' < '3'.
    """
    return sorted(items, key=lambda x: x["priority"])


def sort_by_priority_fixed(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    CORRECTED IMPLEMENTATION:
    Converts priority values to integer before comparison.
    Handles string or integer inputs safely.
    """
    return sorted(items, key=lambda x: int(x["priority"]))


if __name__ == "__main__":
    records = [
        {"task": "Database Backup", "priority": "100"},
        {"task": "Fix Typo", "priority": "20"},
        {"task": "Security Patch", "priority": "5"},
    ]
    print("Buggy order:", [r["task"] for r in sort_by_priority_buggy(records)])
    print("Fixed order:", [r["task"] for r in sort_by_priority_fixed(records)])

"""
traceback_exercises.py - Real Exception Call Stacks for Traceback Analysis

This module defines 5 realistic multi-frame functions that each raise a distinct
Python exception when invoked with invalid arguments or unexpected runtime states:
1. KeyError (missing nested dictionary key)
2. ZeroDivisionError (empty list denominator in calculation)
3. TypeError (invalid type concatenation in string formatting)
4. IndexError (out-of-bounds list access in workflow pipeline)
5. AttributeError (method access on a None object)
"""

import traceback
from typing import Dict, List, Any, Optional


# ---------------------------------------------------------------------
# 1. KeyError: Missing nested dictionary key
# ---------------------------------------------------------------------
def _extract_email_field(profile: Dict[str, Any]) -> str:
    # Frame 2: Raises KeyError when 'email' is missing from profile['contact']
    return profile["contact"]["email"]

def get_user_primary_email(user_record: Dict[str, Any]) -> str:
    """
    Retrieves the primary email address from a nested user profile.
    Raises KeyError if 'email' is not present in user_record['contact'].
    """
    # Frame 1
    return _extract_email_field(user_record)


# ---------------------------------------------------------------------
# 2. ZeroDivisionError: Empty dataset division
# ---------------------------------------------------------------------
def _calculate_mean(samples: List[float]) -> float:
    # Frame 2: Raises ZeroDivisionError if len(samples) is 0
    return sum(samples) / len(samples)

def compute_average_metric(metric_name: str, values: List[float]) -> float:
    """
    Computes the arithmetic mean of telemetry samples.
    Raises ZeroDivisionError if values is empty.
    """
    # Frame 1
    return _calculate_mean(values)


# ---------------------------------------------------------------------
# 3. TypeError: Type mismatch concatenation
# ---------------------------------------------------------------------
def _compose_header(prefix: str, count: int) -> str:
    # Frame 2: Raises TypeError: can only concatenate str (not "int") to str
    return prefix + count

def format_order_summary(order_id: str, item_count: int, prefix: str = "Order Items: ") -> str:
    """
    Formats a user-facing order summary line.
    Raises TypeError due to un-stringified integer concatenation.
    """
    # Frame 1
    header = _compose_header(prefix, item_count)
    return f"[{order_id}] {header}"


# ---------------------------------------------------------------------
# 4. IndexError: Out-of-bounds sequence indexing
# ---------------------------------------------------------------------
def _resolve_stage(stages: List[str], index: int) -> str:
    # Frame 2: Raises IndexError when index >= len(stages)
    return stages[index]

def get_pipeline_stage(stages: List[str], stage_index: int) -> str:
    """
    Retrieves the name of a CI/CD pipeline stage by zero-based index.
    Raises IndexError if stage_index is out of range.
    """
    # Frame 1
    return _resolve_stage(stages, stage_index)


# ---------------------------------------------------------------------
# 5. AttributeError: Method call on NoneType
# ---------------------------------------------------------------------
def _execute_send(notifier: Any, recipient_name: str) -> bool:
    # Frame 2: Raises AttributeError when notifier is None
    return notifier.send(f"Hello, {recipient_name}")

def dispatch_notification(recipient: Dict[str, str], notifier: Optional[Any]) -> bool:
    """
    Dispatches an alert to a recipient using a provided notifier client.
    Raises AttributeError if notifier client is None.
    """
    # Frame 1
    return _execute_send(notifier, recipient["name"])


if __name__ == "__main__":
    exercises = [
        ("KeyError", lambda: get_user_primary_email({"name": "Alex", "contact": {"phone": "555-0100"}})),
        ("ZeroDivisionError", lambda: compute_average_metric("latency_ms", [])),
        ("TypeError", lambda: format_order_summary("ORD-9821", 5)),
        ("IndexError", lambda: get_pipeline_stage(["lint", "test", "build"], 10)),
        ("AttributeError", lambda: dispatch_notification({"name": "Sam"}, None)),
    ]

    for name, func in exercises:
        print(f"\n{'='*70}\nTRIGGERING EXCEPTION: {name}\n{'='*70}")
        try:
            func()
        except Exception:
            traceback.print_exc()

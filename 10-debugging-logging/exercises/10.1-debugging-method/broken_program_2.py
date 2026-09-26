"""
broken_program_2.py - User Audit and Event Tagging Service

Problem Description:
The telemetry service collects user audit events and attaches categorisation tags.
In the buggy implementation, a mutable default argument (`tags=[]`) causes tags
from previous function calls to leak into subsequent requests for completely different users.
"""

from typing import List, Dict, Any, Optional


def register_user_event_buggy(user_id: str, action: str, tags: List[str] = []) -> Dict[str, Any]:
    """
    BUGGY IMPLEMENTATION:
    Registers a user action and tags it.
    Bug: Uses a mutable default list (`tags=[]`) which persists across invocations.
    """
    tags.append(f"source:api")
    tags.append(f"action:{action}")
    return {
        "user_id": user_id,
        "action": action,
        "tags": tags
    }


def register_user_event_fixed(user_id: str, action: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    CORRECTED IMPLEMENTATION:
    Uses `None` as default sentinel and creates a fresh list per call when None.
    """
    if tags is None:
        user_tags = []
    else:
        # Create a shallow copy so caller's passed list is not unintentionally mutated
        user_tags = list(tags)
    
    user_tags.append("source:api")
    user_tags.append(f"action:{action}")
    return {
        "user_id": user_id,
        "action": action,
        "tags": user_tags
    }


if __name__ == "__main__":
    # Demonstration of state pollution across users in buggy version:
    print("--- Buggy Output ---")
    event1 = register_user_event_buggy("user_101", "login")
    print("User 101 event:", event1)
    event2 = register_user_event_buggy("user_202", "view_profile")
    print("User 202 event (tags leaked!):", event2)

    print("\n--- Fixed Output ---")
    fixed_event1 = register_user_event_fixed("user_101", "login")
    print("Fixed User 101 event:", fixed_event1)
    fixed_event2 = register_user_event_fixed("user_202", "view_profile")
    print("Fixed User 202 event (clean tags):", fixed_event2)

"""
defect_3.py - Defect Scenario 3: Shallow Copy in Nested State Mutation

Symptom:
Customizing settings for one user unintentionally changes settings for all subsequent users.
"""

import copy
from typing import Dict, Any


DEFAULT_PROFILE_TEMPLATE: Dict[str, Any] = {
    "theme": "dark",
    "preferences": {
        "email_alerts": True,
        "sms_alerts": False,
    }
}


def create_user_profile_buggy(user_id: str, custom_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    BUGGY IMPLEMENTATION:
    Uses dict.copy() to duplicate template.
    Bug: dict.copy() is shallow; nested dict 'preferences' references the exact same dictionary in memory!
    """
    profile = DEFAULT_PROFILE_TEMPLATE.copy()
    profile["user_id"] = user_id
    # Mutates the shared preferences dictionary directly
    profile["preferences"].update(custom_preferences)
    return profile


def create_user_profile_fixed(user_id: str, custom_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    CORRECTED IMPLEMENTATION:
    Uses copy.deepcopy() to ensure nested dictionary structures are completely detached.
    """
    profile = copy.deepcopy(DEFAULT_PROFILE_TEMPLATE)
    profile["user_id"] = user_id
    profile["preferences"].update(custom_preferences)
    return profile


if __name__ == "__main__":
    u1 = create_user_profile_fixed("user_1", {"email_alerts": False})
    u2 = create_user_profile_fixed("user_2", {})
    print("User 1 email alerts:", u1["preferences"]["email_alerts"])
    print("User 2 email alerts (should still be True):", u2["preferences"]["email_alerts"])

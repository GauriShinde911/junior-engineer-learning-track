"""
defect_5.py - Defect Scenario 5: Greedy Regular Expression Over-Matching

Symptom:
Template engine fails to interpolate multiple placeholders in a string, replacing
everything from the start of the first tag to the end of the last tag with a single token.
"""

import re
from typing import List


def extract_template_variables_buggy(template_text: str) -> List[str]:
    r"""
    BUGGY IMPLEMENTATION:
    Uses greedy pattern `r"\{\{(.*)\}\}"`.
    In "Hello {{first_name}}, welcome to {{city}}!", greedy `.*` matches
    "first_name}}, welcome to {{city", capturing one corrupt token.
    """
    return re.findall(r"\{\{(.*)\}\}", template_text)


def extract_template_variables_fixed(template_text: str) -> List[str]:
    r"""
    CORRECTED IMPLEMENTATION:
    Uses non-greedy pattern `r"\{\{(.*?)\}\}"` or negated set `r"\{\{([^}]+)\}\}"`.
    Captures each discrete placeholder independently.
    """
    return re.findall(r"\{\{(.*?)\}\}", template_text)


if __name__ == "__main__":
    template = "Invoice for {{customer_name}}: Your total is {{amount_due}} due on {{due_date}}."
    print("Buggy tags extracted:", extract_template_variables_buggy(template))
    print("Fixed tags extracted:", extract_template_variables_fixed(template))

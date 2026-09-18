"""
exercises/6.1-test-basics/string_utils.py
String manipulation utilities designed for automated unit testing.
"""

import re
from typing import List


def reverse_string(text: str) -> str:
    """Reverse a given string.

    Args:
        text: Input string.

    Returns:
        Reversed string.
    """
    return text[::-1]


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length including suffix if it exceeds length.

    Args:
        text: Input string to truncate.
        max_length: Maximum allowed string length (must be positive).
        suffix: Ellipsis or suffix appended when truncated.

    Returns:
        Truncated or original string.

    Raises:
        ValueError: If max_length is less than or equal to 0.
    """
    if max_length <= 0:
        raise ValueError("max_length must be greater than zero")
    if len(text) <= max_length:
        return text
    if max_length <= len(suffix):
        return suffix[:max_length]
    return text[: max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """Convert text into an SEO-friendly URL slug.

    Replaces non-alphanumeric characters with dashes, converts to lowercase,
    and removes leading/trailing dashes.

    Args:
        text: Input text.

    Returns:
        Clean slugified string.
    """
    normalized = re.sub(r"[^\w\s-]", "", text.strip().lower())
    slug = re.sub(r"[-\s]+", "-", normalized)
    return slug.strip("-")


def split_words(text: str) -> List[str]:
    """Split text into words, stripping punctuation and extra whitespace.

    Args:
        text: Input string.

    Returns:
        List of non-empty cleaned words.
    """
    if not text:
        return []
    words = re.findall(r"\b\w+\b", text)
    return words

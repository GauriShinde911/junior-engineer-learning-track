"""
exercises/6.1-test-basics/test_string_utils.py
Tests demonstrating test discovery, clear naming, assertion patterns, and setup/teardown.
"""

from typing import Generator
import pytest
from string_utils import reverse_string, truncate, slugify, split_words


@pytest.fixture
def sample_text_corpus() -> Generator[dict, None, None]:
    """Setup & teardown fixture providing sample strings for test execution."""
    # Setup phase: prepare clean data resource
    corpus = {
        "greeting": "Hello, World!",
        "long_bio": "Junior software engineer building robust testing foundations in Python.",
        "headline": "Modern DevOps & CI/CD Pipelines for 2026!",
    }
    yield corpus
    # Teardown phase: cleanup or state reset verification
    corpus.clear()


def test_reverse_string_with_alphanumeric():
    """Verify reverse_string inverts character order properly."""
    result = reverse_string("Python3")
    assert result == "3nohtyP"


def test_reverse_string_with_empty_string():
    """Verify reversing an empty string safely returns an empty string."""
    assert reverse_string("") == ""


def test_reverse_string_with_palindrome():
    """Verify reversing a palindrome yields an identical string."""
    assert reverse_string("racecar") == "racecar"


def test_truncate_short_text_remains_unchanged(sample_text_corpus):
    """Verify text shorter than max_length is not truncated."""
    short_text = sample_text_corpus["greeting"]
    assert truncate(short_text, max_length=50) == short_text


def test_truncate_long_text_appends_ellipsis(sample_text_corpus):
    """Verify text longer than max_length is sliced and gets suffix appended."""
    text = sample_text_corpus["long_bio"]
    truncated = truncate(text, max_length=20, suffix="...")
    assert len(truncated) == 20
    assert truncated.endswith("...")


def test_truncate_with_zero_or_negative_length_raises_value_error():
    """Verify truncate raises ValueError when invalid max_length is passed."""
    with pytest.raises(ValueError, match="must be greater than zero"):
        truncate("Hello", max_length=0)


def test_slugify_converts_spaces_and_special_chars(sample_text_corpus):
    """Verify slugify transforms spaces and special symbols into lowercase hyphenated slug."""
    text = sample_text_corpus["headline"]
    expected = "modern-devops-cicd-pipelines-for-2026"
    assert slugify(text) == expected


def test_slugify_strips_outer_hyphens():
    """Verify leading and trailing dashes are trimmed from the slug."""
    assert slugify("---Leading and trailing---") == "leading-and-trailing"


def test_split_words_extracts_clean_token_list():
    """Verify split_words ignores punctuation marks and extracts clean words."""
    sentence = "Clean code, readable tests; reliable software!"
    assert split_words(sentence) == ["Clean", "code", "readable", "tests", "reliable", "software"]


def test_split_words_handles_empty_string():
    """Verify empty string returns an empty list without error."""
    assert split_words("") == []

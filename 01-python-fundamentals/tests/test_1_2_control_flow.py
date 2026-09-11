"""
Tests for 1.2 Control Flow
Covers: number_analysis, pattern_generation, search_filter, menu_loop.
"""

import sys
from pathlib import Path
import pytest

MODULE_ROOT = Path(__file__).resolve().parent.parent
SUBSECTION_DIR = MODULE_ROOT / "exercises" / "1.2-control-flow"
if str(SUBSECTION_DIR) not in sys.path:
    sys.path.insert(0, str(SUBSECTION_DIR))

from number_analysis import analyze_numbers, is_prime
from pattern_generation import (
    generate_centered_pyramid,
    generate_number_staircase,
    generate_right_triangle
)
from search_filter import filter_by_category, filter_by_price_range, search_by_name
from menu_loop import execute_action, run_menu


# =====================================================================
# Number Analysis Tests
# =====================================================================
def test_is_prime():
    assert is_prime(2) is True
    assert is_prime(7) is True
    assert is_prime(11) is True
    assert is_prime(4) is False
    assert is_prime(1) is False
    assert is_prime(-7) is False


def test_analyze_numbers():
    data = [2, 3, 4, 5, "skip_me", 6]
    stats = analyze_numbers(data)
    assert stats["count"] == 6
    assert stats["sum"] == 20
    assert stats["even_count"] == 3
    assert stats["odd_count"] == 2
    assert stats["primes"] == [2, 3, 5]


def test_analyze_numbers_empty():
    stats = analyze_numbers([])
    assert stats["count"] == 0
    assert stats["max"] is None


# =====================================================================
# Pattern Generation Tests
# =====================================================================
def test_pattern_generators():
    triangle = generate_right_triangle(3, "*")
    assert triangle == ["*", "**", "***"]

    pyramid = generate_centered_pyramid(3, "*")
    assert len(pyramid) == 3
    assert pyramid[-1] == "*****"

    staircase = generate_number_staircase(3)
    assert staircase == ["1", "12", "123"]


def test_pattern_generators_zero_or_negative():
    assert generate_right_triangle(0) == []
    assert generate_centered_pyramid(-2) == []
    assert generate_number_staircase(0) == []


# =====================================================================
# Search & Filter Tests
# =====================================================================
def test_search_and_filter():
    items = [
        {"name": "Book", "category": "Media", "price": 15.0},
        {"name": "Laptop", "category": "Tech", "price": 999.0},
        {"name": "Pen", "category": "Media", "price": 2.5}
    ]

    assert search_by_name(items, "laptop")["price"] == 999.0
    assert search_by_name(items, "missing") is None

    media = filter_by_category(items, "media")
    assert len(media) == 2

    affordable = filter_by_price_range(items, 1.0, 20.0)
    assert len(affordable) == 2


def test_filter_price_range_invalid():
    with pytest.raises(ValueError, match="cannot exceed max_price"):
        filter_by_price_range([], min_price=50.0, max_price=10.0)


# =====================================================================
# Menu Loop Tests
# =====================================================================
def test_menu_loop_actions():
    state = {"counter": 0, "iterations": 0}
    assert execute_action("1", state) is True
    assert state["counter"] == 1
    assert execute_action("2", state) is True
    assert state["counter"] == 0
    assert execute_action("5", state) is False  # Exit signal


def test_run_menu_simulated():
    # Sequence: Increment (1), Increment (1), View (4), Exit (5)
    final_state = run_menu(simulated_inputs=["1", "1", "4", "5"])
    assert final_state["counter"] == 2
    assert final_state["iterations"] == 4

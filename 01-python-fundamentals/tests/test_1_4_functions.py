"""
Tests for 1.4 Functions
Covers: utility_library (*args, **kwargs, defaults, keyword-only, pure functions).
"""

import sys
from pathlib import Path
import pytest

MODULE_ROOT = Path(__file__).resolve().parent.parent
SUBSECTION_DIR = MODULE_ROOT / "exercises" / "1.4-functions"
if str(SUBSECTION_DIR) not in sys.path:
    sys.path.insert(0, str(SUBSECTION_DIR))

from utility_library import (
    aggregate_by_key,
    calculate_statistics,
    clamp,
    clean_string,
    convert_temperature,
    filter_records,
    format_currency,
    safe_divide
)


# =====================================================================
# Math & Statistical Functions Tests
# =====================================================================
def test_safe_divide():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) is None
    assert safe_divide(10, 0, default=-1.0) == -1.0


def test_calculate_statistics_args():
    stats = calculate_statistics(10, 20, 30)
    assert stats["count"] == 3
    assert stats["sum"] == 60.0
    assert stats["mean"] == 20.0
    assert stats["min"] == 10
    assert stats["max"] == 30


def test_calculate_statistics_empty():
    stats = calculate_statistics()
    assert stats["count"] == 0
    assert stats["mean"] is None


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-5, 0, 10) == 0
    assert clamp(15, 0, 10) == 10

    with pytest.raises(ValueError, match="cannot be greater than max_val"):
        clamp(5, 10, 0)


# =====================================================================
# Conversion Functions Tests
# =====================================================================
def test_convert_temperature_keyword_only():
    assert convert_temperature(0, from_unit="C", to_unit="F") == 32.0
    assert convert_temperature(212, from_unit="F", to_unit="C") == 100.0
    assert convert_temperature(0, from_unit="C", to_unit="K") == 273.15


def test_convert_temperature_errors():
    with pytest.raises(ValueError, match="Unsupported input unit"):
        convert_temperature(100, from_unit="X", to_unit="C")

    with pytest.raises(ValueError, match="absolute zero"):
        convert_temperature(-500, from_unit="C", to_unit="F")


# =====================================================================
# String & Formatting Tests
# =====================================================================
def test_format_currency():
    assert format_currency(1250.5) == "$1,250.50"
    assert format_currency(99.9, symbol="€", decimals=1) == "€99.9"


def test_clean_string():
    assert clean_string("   Hello World   ", lowercase=True) == "hello world"
    assert clean_string("Keep Case", lowercase=False) == "Keep Case"


# =====================================================================
# Collection Helpers Tests (**kwargs)
# =====================================================================
def test_filter_records_kwargs():
    records = [
        {"name": "Alice", "dept": "Engineering", "active": True},
        {"name": "Bob", "dept": "Marketing", "active": False},
        {"name": "Charlie", "dept": "Engineering", "active": False}
    ]

    active_eng = filter_records(records, dept="engineering", active=True)
    assert len(active_eng) == 1
    assert active_eng[0]["name"] == "Alice"

    all_eng = filter_records(records, dept="engineering")
    assert len(all_eng) == 2


def test_aggregate_by_key():
    items = [
        {"cat": "Groceries", "price": 10.5},
        {"cat": "Groceries", "price": 4.5},
        {"cat": "Books", "price": 20.0}
    ]
    totals = aggregate_by_key(items, "cat", "price")
    assert totals["Groceries"] == 15.0
    assert totals["Books"] == 20.0

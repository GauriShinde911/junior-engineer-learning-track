"""
Tests for 1.1 Syntax & Execution
Covers: calculator, unit_converter, grade_calculator, menu_driven_cli, text_formatter.
Each module is tested with happy-path and negative/error cases.
"""

import sys
from pathlib import Path
import pytest

MODULE_ROOT = Path(__file__).resolve().parent.parent
SUBSECTION_DIR = MODULE_ROOT / "exercises" / "1.1-syntax-execution"
if str(SUBSECTION_DIR) not in sys.path:
    sys.path.insert(0, str(SUBSECTION_DIR))

from calculator import calculate
from unit_converter import (
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    km_to_miles,
    miles_to_km
)
from grade_calculator import get_letter_grade
from menu_driven_cli import add_note, delete_note, view_notes
from text_formatter import (
    count_words,
    reverse_text,
    to_lower,
    to_title,
    to_upper
)


# =====================================================================
# Calculator Tests
# =====================================================================
def test_calculator_operations():
    assert calculate(10, 5, "+") == 15
    assert calculate(10, 5, "-") == 5
    assert calculate(10, 5, "*") == 50
    assert calculate(10, 2, "/") == 5.0
    assert calculate(10, 3, "%") == 1


def test_calculator_division_and_modulo_by_zero():
    assert "Cannot divide by zero" in calculate(10, 0, "/")
    assert "undefined" in calculate(10, 0, "%")


def test_calculator_invalid_operation():
    assert "Invalid operation" in calculate(10, 5, "^")


# =====================================================================
# Unit Converter Tests
# =====================================================================
def test_unit_converter_valid_conversions():
    assert round(km_to_miles(10), 2) == 6.21
    assert round(miles_to_km(6.21371), 2) == 10.00
    assert celsius_to_fahrenheit(0) == 32.0
    assert round(fahrenheit_to_celsius(212), 2) == 100.0


def test_unit_converter_negative_boundaries():
    with pytest.raises(ValueError, match="cannot be negative"):
        km_to_miles(-5)

    with pytest.raises(ValueError, match="absolute zero"):
        celsius_to_fahrenheit(-300)


# =====================================================================
# Grade Calculator Tests
# =====================================================================
def test_grade_calculator_valid_grades():
    assert get_letter_grade(95) == "A"
    assert get_letter_grade(85) == "B"
    assert get_letter_grade(75) == "C"
    assert get_letter_grade(65) == "D"
    assert get_letter_grade(45) == "F"


def test_grade_calculator_invalid_score():
    with pytest.raises(ValueError, match="Score must be between 0 and 100"):
        get_letter_grade(-1)

    with pytest.raises(ValueError, match="Score must be between 0 and 100"):
        get_letter_grade(105)


# =====================================================================
# Menu-Driven CLI Logic Tests
# =====================================================================
def test_notes_manager_lifecycle():
    notes = []
    assert add_note(notes, "First test note") is True
    assert add_note(notes, "Second test note") is True
    assert len(view_notes(notes)) == 2

    removed = delete_note(notes, 1)
    assert removed == "First test note"
    assert len(notes) == 1


def test_notes_manager_errors():
    notes = ["Existing note"]
    with pytest.raises(ValueError, match="Cannot add an empty note"):
        add_note(notes, "   ")

    with pytest.raises(IndexError, match="Invalid note index"):
        delete_note(notes, 5)


# =====================================================================
# Text Formatter Tests
# =====================================================================
def test_text_formatter_transformations():
    text = "hello World"
    assert to_upper(text) == "HELLO WORLD"
    assert to_lower(text) == "hello world"
    assert to_title(text) == "Hello World"
    assert reverse_text("Python") == "nohtyP"
    assert count_words("Quick brown fox jumps") == 4

"""
exercises/6.2-unit-tests/test_calculator_core.py
Unit tests verifying pure functional behavior, edge boundaries, and invalid input enforcement.
Tests assert against input-output contracts rather than internal implementation mechanics.
"""

import pytest
from calculator_core import (
    divide,
    calculate_percentage,
    apply_discount,
    calculate_moving_average,
)


# ---------------------------------------------------------------------------
# divide() tests
# ---------------------------------------------------------------------------

def test_divide_standard_integers():
    """Verify clean integer division without truncation."""
    assert divide(10, 2) == 5.0


def test_divide_periodic_float_respects_precision():
    """Verify recurring decimal results round strictly to specified precision."""
    assert divide(1, 3, precision=2) == 0.33
    assert divide(1, 3, precision=4) == 0.3333


def test_divide_with_negative_operands():
    """Verify arithmetic sign rules: positive/negative and negative/negative."""
    assert divide(-15, 3) == -5.0
    assert divide(15, -3) == -5.0
    assert divide(-15, -3) == 5.0


def test_divide_zero_numerator_returns_zero():
    """Verify zero divided by any valid non-zero denominator is zero."""
    assert divide(0, 100) == 0.0


def test_divide_by_zero_raises_zero_division_error():
    """Verify division by zero raises ZeroDivisionError boundary exception."""
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        divide(10, 0)


def test_divide_negative_precision_raises_value_error():
    """Verify negative rounding precision is rejected with ValueError."""
    with pytest.raises(ValueError, match="Precision cannot be negative"):
        divide(10, 2, precision=-1)


# ---------------------------------------------------------------------------
# calculate_percentage() tests
# ---------------------------------------------------------------------------

def test_calculate_percentage_typical_values():
    """Verify standard proportional ratio calculation."""
    assert calculate_percentage(25, 100) == 25.0
    assert calculate_percentage(1, 3, precision=2) == 33.33


def test_calculate_percentage_boundaries():
    """Verify boundary conditions: 0% and 100%."""
    assert calculate_percentage(0, 200) == 0.0
    assert calculate_percentage(200, 200) == 100.0


def test_calculate_percentage_exceeding_total():
    """Verify part greater than total computes over-100 percentage."""
    assert calculate_percentage(150, 100) == 150.0


def test_calculate_percentage_invalid_total_raises_value_error():
    """Verify non-positive denominator totals raise ValueError."""
    with pytest.raises(ValueError, match="Total must be strictly positive"):
        calculate_percentage(10, 0)

    with pytest.raises(ValueError, match="Total must be strictly positive"):
        calculate_percentage(10, -50)


def test_calculate_percentage_negative_part_raises_value_error():
    """Verify negative part amounts are rejected."""
    with pytest.raises(ValueError, match="Part cannot be negative"):
        calculate_percentage(-5, 100)


# ---------------------------------------------------------------------------
# apply_discount() tests
# ---------------------------------------------------------------------------

def test_apply_discount_typical_rate():
    """Verify standard discount rate reduction."""
    assert apply_discount(100.0, 20.0) == 80.0


def test_apply_discount_boundary_zero_and_hundred():
    """Verify 0% discount preserves price and 100% reduces to zero."""
    assert apply_discount(50.0, 0.0) == 50.0
    assert apply_discount(50.0, 100.0) == 0.0


def test_apply_discount_minimum_charge_clamping():
    """Verify that when discounted price drops below minimum charge, floor is enforced."""
    # 90% off $100 is $10, but minimum charge is $25 -> should clamp to 25.0
    assert apply_discount(100.0, 90.0, minimum_charge=25.0) == 25.0


def test_apply_discount_invalid_percentage_bounds():
    """Verify discount percentages below 0 or above 100 raise ValueError."""
    with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100"):
        apply_discount(100.0, -5.0)

    with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100"):
        apply_discount(100.0, 105.0)


def test_apply_discount_invalid_price_or_minimum_charge():
    """Verify negative price or negative minimum charge are rejected."""
    with pytest.raises(ValueError, match="Price cannot be negative"):
        apply_discount(-10.0, 10.0)

    with pytest.raises(ValueError, match="Minimum charge cannot be negative"):
        apply_discount(100.0, 10.0, minimum_charge=-5.0)


# ---------------------------------------------------------------------------
# calculate_moving_average() tests
# ---------------------------------------------------------------------------

def test_calculate_moving_average_standard_window():
    """Verify rolling average calculation across a series."""
    data = [10.0, 20.0, 30.0, 40.0, 50.0]
    expected = [20.0, 30.0, 40.0]  # windows: [10,20,30]->20, [20,30,40]->30, [30,40,50]->40
    assert calculate_moving_average(data, window_size=3) == expected


def test_calculate_moving_average_window_equal_to_data_length():
    """Verify single-element result when window equals array length."""
    data = [2.0, 4.0, 6.0]
    assert calculate_moving_average(data, window_size=3) == [4.0]


def test_calculate_moving_average_window_of_one():
    """Verify window of 1 produces exact original elements."""
    data = [5.5, 12.0, 8.5]
    assert calculate_moving_average(data, window_size=1) == data


def test_calculate_moving_average_empty_data_raises_value_error():
    """Verify empty sequence raises ValueError."""
    with pytest.raises(ValueError, match="Data sequence cannot be empty"):
        calculate_moving_average([], window_size=2)


def test_calculate_moving_average_window_exceeding_length_raises_value_error():
    """Verify window size greater than dataset size raises ValueError."""
    with pytest.raises(ValueError, match="Window size cannot exceed data sequence length"):
        calculate_moving_average([1.0, 2.0], window_size=5)


def test_calculate_moving_average_invalid_window_size_raises_value_error():
    """Verify zero or negative window size raises ValueError."""
    with pytest.raises(ValueError, match="Window size must be greater than zero"):
        calculate_moving_average([1.0, 2.0, 3.0], window_size=0)

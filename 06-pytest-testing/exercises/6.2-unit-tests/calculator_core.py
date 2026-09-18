"""
exercises/6.2-unit-tests/calculator_core.py
Pure functional core arithmetic and boundary-sensitive numerical routines.
No I/O, no state, 100% deterministic functions.
"""

from typing import List, Sequence


def divide(numerator: float, denominator: float, precision: int = 4) -> float:
    """Safely divide numerator by denominator rounded to precision decimal places.

    Args:
        numerator: Dividend.
        denominator: Divisor.
        precision: Number of decimal digits to round output to.

    Returns:
        Quotient rounded to precision.

    Raises:
        ZeroDivisionError: If denominator is 0.
        ValueError: If precision is negative.
    """
    if denominator == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    if precision < 0:
        raise ValueError("Precision cannot be negative")
    return round(numerator / denominator, precision)


def calculate_percentage(part: float, total: float, precision: int = 2) -> float:
    """Calculate percentage of part relative to total.

    Args:
        part: Sub-amount (can be zero or greater than total).
        total: Baseline amount (must be strictly positive).
        precision: Decimal rounding precision.

    Returns:
        Percentage value (e.g. 50.0 for half).

    Raises:
        ValueError: If total <= 0 or part < 0.
    """
    if total <= 0:
        raise ValueError("Total must be strictly positive")
    if part < 0:
        raise ValueError("Part cannot be negative")
    return round((part / total) * 100.0, precision)


def apply_discount(
    price: float,
    discount_percent: float,
    minimum_charge: float = 0.0,
) -> float:
    """Calculate discounted price with bounds checking and floor clamping.

    Args:
        price: Original price (must be non-negative).
        discount_percent: Percentage discount between 0.0 and 100.0 inclusive.
        minimum_charge: Floor price below which final price cannot fall.

    Returns:
        Final discounted price.

    Raises:
        ValueError: If price < 0, discount_percent not in [0, 100], or minimum_charge < 0.
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not (0.0 <= discount_percent <= 100.0):
        raise ValueError("Discount percentage must be between 0 and 100")
    if minimum_charge < 0:
        raise ValueError("Minimum charge cannot be negative")

    discount_amount = price * (discount_percent / 100.0)
    discounted = price - discount_amount
    return round(max(discounted, minimum_charge), 2)


def calculate_moving_average(data: Sequence[float], window_size: int) -> List[float]:
    """Compute rolling simple moving average across a series of numbers.

    Args:
        data: Sequence of numerical values.
        window_size: Number of consecutive elements in the moving window.

    Returns:
        List of moving averages of length (len(data) - window_size + 1).

    Raises:
        ValueError: If data is empty, window_size <= 0, or window_size > len(data).
    """
    if not data:
        raise ValueError("Data sequence cannot be empty")
    if window_size <= 0:
        raise ValueError("Window size must be greater than zero")
    if window_size > len(data):
        raise ValueError("Window size cannot exceed data sequence length")

    averages: List[float] = []
    current_window_sum = sum(data[:window_size])
    averages.append(round(current_window_sum / window_size, 4))

    for i in range(window_size, len(data)):
        current_window_sum += data[i] - data[i - window_size]
        averages.append(round(current_window_sum / window_size, 4))

    return averages

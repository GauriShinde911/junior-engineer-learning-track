"""
1.4 Functions: Reusable Utility Library
Refactors common routines from 1.1-1.3 into modular, well-documented, pure functions.
Demonstrates:
- Explicit type hints, docstrings, parameters, and return values
- Default parameter values and keyword-only arguments
- Variable positional arguments (*args) and variable keyword arguments (**kwargs)
- Pure functions (deterministic outputs, no side effects, no mutation of inputs)
"""

from typing import Any, Dict, List, Optional, Tuple, Union


# =====================================================================
# 1. Math & Statistical Functions (*args, defaults)
# =====================================================================
def safe_divide(numerator: float, denominator: float, default: Optional[float] = None) -> Optional[float]:
    """
    Safely divides numerator by denominator.
    Returns default if denominator is zero.
    """
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_statistics(*numbers: float) -> Dict[str, Optional[float]]:
    """
    Accepts arbitrary positional numbers (*args) and computes summary metrics.
    Pure function with no global state mutation.
    """
    valid_nums = [n for n in numbers if isinstance(n, (int, float))]
    if not valid_nums:
        return {"count": 0, "sum": 0.0, "mean": None, "min": None, "max": None}

    total = sum(valid_nums)
    count = len(valid_nums)
    return {
        "count": count,
        "sum": round(total, 4),
        "mean": round(total / count, 4),
        "min": min(valid_nums),
        "max": max(valid_nums)
    }


def clamp(val: float, min_val: float, max_val: float) -> float:
    """Clamps a value within [min_val, max_val]."""
    if min_val > max_val:
        raise ValueError(f"min_val ({min_val}) cannot be greater than max_val ({max_val})")
    return max(min_val, min(val, max_val))


# =====================================================================
# 2. Conversion Utilities (keyword arguments, defaults)
# =====================================================================
def convert_temperature(value: float, *, from_unit: str = "C", to_unit: str = "F") -> float:
    """
    Keyword-only parameters (*,) force callers to be explicit.
    Converts between Celsius ('C'), Fahrenheit ('F'), and Kelvin ('K').
    """
    unit_in = from_unit.strip().upper()
    unit_out = to_unit.strip().upper()

    # Step 1: Normalize to Celsius
    if unit_in == "C":
        celsius = value
    elif unit_in == "F":
        celsius = (value - 32) * 5 / 9
    elif unit_in == "K":
        celsius = value - 273.15
    else:
        raise ValueError(f"Unsupported input unit: {from_unit}")

    if celsius < -273.15:
        raise ValueError("Temperature cannot be below absolute zero.")

    # Step 2: Convert from Celsius to target
    if unit_out == "C":
        return round(celsius, 2)
    elif unit_out == "F":
        return round((celsius * 9 / 5) + 32, 2)
    elif unit_out == "K":
        return round(celsius + 273.15, 2)
    else:
        raise ValueError(f"Unsupported output unit: {to_unit}")


# =====================================================================
# 3. String & Formatting Utilities (pure functions)
# =====================================================================
def format_currency(amount: float, symbol: str = "$", decimals: int = 2) -> str:
    """Formats a float as a human-readable currency string."""
    return f"{symbol}{amount:,.{decimals}f}"


def clean_string(text: str, *, lowercase: bool = False, strip_whitespace: bool = True) -> str:
    """Sanitizes text without mutating the original variable."""
    result = text
    if strip_whitespace:
        result = result.strip()
    if lowercase:
        result = result.lower()
    return result


# =====================================================================
# 4. Collection Utilities (**kwargs multi-criteria filtering)
# =====================================================================
def filter_records(records: List[Dict[str, Any]], **criteria: Any) -> List[Dict[str, Any]]:
    """
    Filters a list of dictionaries using arbitrary keyword criteria (**kwargs).
    Example: filter_records(data, dept="Engineering", status="Active")
    """
    matched = []
    for item in records:
        matches_all = True
        for key, expected in criteria.items():
            val = item.get(key)
            # Case-insensitive comparison if both are strings
            if isinstance(val, str) and isinstance(expected, str):
                if val.strip().lower() != expected.strip().lower():
                    matches_all = False
                    break
            elif val != expected:
                matches_all = False
                break
        if matches_all:
            matched.append(item)
    return matched


def aggregate_by_key(records: List[Dict[str, Any]], group_key: str, sum_key: str) -> Dict[str, float]:
    """Pure grouping function summing sum_key values grouped by group_key."""
    totals: Dict[str, float] = {}
    for item in records:
        group = str(item.get(group_key, "Unknown"))
        val = item.get(sum_key, 0.0)
        if isinstance(val, (int, float)):
            totals[group] = round(totals.get(group, 0.0) + val, 2)
    return totals


# =====================================================================
# Demonstration & Verification
# =====================================================================
if __name__ == "__main__":
    print("=== Utility Library Verification ===")

    # 1. *args stats demo
    stats = calculate_statistics(10, 20, 30, 40, 50, 100)
    print("calculate_statistics:", stats)

    # 2. Keyword-only conversion
    f_temp = convert_temperature(100, from_unit="C", to_unit="F")
    print(f"100°C in Fahrenheit: {f_temp}°F")

    # 3. Currency formatting
    print("format_currency:", format_currency(1234567.89))

    # 4. **kwargs multi-filter
    test_users = [
        {"name": "Alice", "role": "Dev", "active": True},
        {"name": "Bob", "role": "Dev", "active": False},
        {"name": "Charlie", "role": "PM", "active": True}
    ]
    active_devs = filter_records(test_users, role="dev", active=True)
    print("Filtered Active Devs:", active_devs)

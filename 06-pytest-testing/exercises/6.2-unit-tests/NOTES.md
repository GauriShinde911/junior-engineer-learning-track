# 6.2 Unit Tests

## Core Concepts
Unit testing focuses on the smallest testable units of an application in strict isolation. Pure functions—functions that depend solely on their inputs and cause zero side effects—are the ideal candidates for unit testing because they are 100% deterministic: given identical arguments, they always yield identical outcomes.

## Key Pytest Features
- `pytest.raises(ExceptionType, match="...")`: Verifies both the exact exception class and regex matching against the exception message string.
- `assert result == expected`: Direct scalar comparison for exact boundary values (0%, 100%, clamped minimums).
- `round(val, precision)` / `pytest.approx()`: Compares floating-point outputs to prevent false negatives caused by binary IEEE 754 precision limits.

## Testing Theory: Behavior vs Implementation
- **Test Behavior, Not Implementation**: Write assertions against public inputs and outputs (the contract), never against private variables or line execution sequence. If you rewrite an internal algorithm from iterative to list-comprehension, every test should still pass untouched.
- **Boundary Value Analysis (BVA)**: Defects cluster at edges (off-by-one, zero values, max capacity, negatives). Testing `0`, `-1`, `100%`, and window edges uncovers subtle flaws that passing standard mid-range values will miss.

## Connection to Exercises
In `calculator_core.py`, functions like `divide`, `calculate_percentage`, `apply_discount`, and `calculate_moving_average` carry strict numerical contracts. `test_calculator_core.py` exercises both normal values and critical edge boundaries (zero division, floor price clamping, window size limits), asserting reliable behavior without coupling to internal logic.

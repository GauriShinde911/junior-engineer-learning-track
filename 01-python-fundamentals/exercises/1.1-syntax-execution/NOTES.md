# 1.1 Syntax & Execution — Quick Reference

## Core Concepts
Python is an interpreted, dynamically-typed language where code is parsed and executed line-by-line by the CPython interpreter. Variables do not have declared types; rather, names reference objects in memory. Programs begin execution at line 1 and evaluate expressions using standard operator precedence (PEMDAS).

## Key Keywords & Syntax
- `if`, `elif`, `else`: Branching execution based on boolean truthiness.
- `while`, `break`: Loop constructs for repeated execution and early termination.
- `try`, `except`: Defensive blocks to intercept runtime errors (e.g. `ValueError` on bad casts).
- `if __name__ == "__main__":`: Idiomatic guard ensuring code only executes when run directly as a script, not when imported as a module.

## Built-in Functions & Types
- `int()`, `float()`, `str()`: Explicit type casting functions to convert between numbers and strings.
- `input()`, `print()`: Basic console I/O; `input()` always returns a string.
- `round(val, n)`: Rounds numbers using bankers' rounding (round half to even).

## Theory to Know
- **Strong, Dynamic Typing**: Types are checked at runtime, and Python will not automatically coerce incompatible types (e.g. `'5' + 2` raises a `TypeError`).
- **Truthiness**: Empty collections (`""`, `[]`, `{}`), numeric zeroes (`0`, `0.0`), and `None` evaluate to `False` in conditional contexts.

## Connection to What Was Built
In this section, five standalone CLI scripts (`calculator.py`, `unit_converter.py`, `grade_calculator.py`, `menu_driven_cli.py`, and `text_formatter.py`) apply basic operator arithmetic, input sanitization, string manipulation, and graceful handling of invalid numeric inputs.

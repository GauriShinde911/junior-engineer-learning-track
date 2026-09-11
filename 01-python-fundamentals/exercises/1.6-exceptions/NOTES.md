# 1.6 Exceptions — Quick Reference

## Core Concepts
Exceptions provide a structured mechanism for handling runtime errors without crashing the process. Python uses the EAFP paradigm ("Easier to Ask for Forgiveness than Permission") where operations are attempted inside `try` blocks and anticipated failure modes are intercepted in `except` clauses.

## Key Keywords & Syntax
- `try`: Encloses code that may raise an exception.
- `except SpecificError as err`: Intercepts and binds specific exception instances.
- `else`: Executes code only if the `try` block completed without raising any exception.
- `finally`: Guaranteed execution block for resource cleanup (closing handles, audit logs), regardless of whether an exception occurred or was handled.
- `raise ExceptionClass("message")`: Triggers an exception explicitly.

## Theory to Know
- **Custom Exception Hierarchies**: Subclassing `Exception` (e.g. `class ValidationError(Exception): pass`) lets your application distinguish expected user errors from unhandled bugs.
- **Never Bare Except**: Avoid `except:` or `except Exception:` without re-raising or logging; doing so swallows critical signals like `KeyboardInterrupt`, `SystemExit`, or unexpected syntax errors.
- **Fail Fast & Explicit**: Validate inputs at system boundaries and raise specific domain errors immediately.

## Connection to What Was Built
- `validation_utils.py`: Defines a custom `BaseValidationError` tree (`EmailValidationError`, `NumericRangeError`, `MissingFieldError`) and strict data checkers.
- `failure_handling.py`: Demonstrates the full `try/except/else/finally` pattern, routing domain validation errors to client guidance while logging unexpected system defects and guaranteeing audit logging.

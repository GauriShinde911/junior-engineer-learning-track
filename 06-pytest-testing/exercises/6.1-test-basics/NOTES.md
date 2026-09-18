# 6.1 Test Basics

## Core Concepts
Automated testing verifies code correctness by running small, reproducible checks. Pytest removes the ceremonial boilerplate of standard unittest classes by turning plain Python functions into discovered tests using standard Python language constructs.

## Key Pytest Features
- `assert <condition>`: Evaluates boolean expressions; pytest inspects AST to print detailed intermediate values when an assertion fails.
- `pytest.raises(ExpectedException, match=...)`: Context manager verifying that a specific exception type and error message pattern are raised.
- `@pytest.fixture` with `yield`: Decorator declaring setup code before the `yield` statement and teardown cleanup code immediately following it.

## Testing Theory & Rules of Thumb
- **Test Discovery**: Pytest searches recursively for files matching `test_*.py` or `*_test.py`, running functions prefixed with `test_*`.
- **One Assertion Focus**: Each test should verify one logical condition or behavior. If a test fails, you should immediately know what broke without stepping through multiple assertions.
- **Assertion Rewriting**: Unlike `self.assertEqual(a, b)` in unittest, pytest rewrites the bytecode of `assert a == b`, displaying exact diffs for strings, lists, and dicts on failure.

## Connection to Exercises
In `test_string_utils.py` and `test_validators.py`, we test pure transformation and validation functions (`reverse_string`, `truncate`, `slugify`, `is_valid_email`, `validate_age`). A fixture with `yield` manages test corpus lifecycle, and `pytest.raises` validates error scenarios (`ValueError`, `TypeError`) at boundary conditions.

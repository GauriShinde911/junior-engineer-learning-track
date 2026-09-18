# 06. Pytest & Automated Testing — Module Overview & Index

This skill folder establishes automated testing as a continuous, everyday engineering discipline rather than an afterthought or a final verification phase. Through practical exercises, it builds muscle memory for test discovery, pure function validation, fixtures, parameterization, architectural mocking, and real database integration testing.

---

## Curriculum Index & Subsection Overviews

1. [**6.1 Test Basics**](exercises/6.1-test-basics/NOTES.md)
   Explores test discovery conventions, pytest assertion rewriting, exception testing with `pytest.raises`, and setup/teardown fixture lifecycles.

2. [**6.2 Unit Tests**](exercises/6.2-unit-tests/NOTES.md)
   Focuses on testing pure functions, boundary value analysis (zero, negatives, off-by-one), and validating behavioral contracts over internal implementation mechanics.

3. [**6.3 Fixtures & Parametrization**](exercises/6.3-fixtures-parametrization/NOTES.md)
   Teaches modular dependency injection via `conftest.py` fixtures, test data factories, and collapsing repetitive test functions into `@pytest.mark.parametrize` matrices.

4. [**6.4 Mocking**](exercises/6.4-mocking/NOTES.md)
   Covers replacing slow, non-deterministic boundaries (HTTP APIs, persistence repositories) with test doubles using `pytest-mock` without over-mocking internal domain logic.

5. [**6.5 Integration Tests**](exercises/6.5-integration-tests/NOTES.md)
   Exercises real SQLite database boundaries using `tmp_path`, verifying actual SQL queries, constraints, schema rules, and transactional persistence without mocks.

- [**Independent Challenge: Unfamiliar Codebase Bug Fix**](independent/unfamiliar_codebase_fix/README.md)
  Demonstrates inheriting legacy code, reading a feature specification, writing failing reproduction and regression tests first, and fixing the defects with full test coverage.

---

## Core Testing Philosophy

- **Test Behavior, Not Implementation**: Verify inputs and outputs against public interfaces so internal refactoring never breaks tests.
- **Mock at the Seams**: Mock external network and vendor boundaries; keep business logic and domain entities real.
- **Red-Green-Refactor**: Write failing tests that pinpoint requirements and bug tickets before modifying production code.

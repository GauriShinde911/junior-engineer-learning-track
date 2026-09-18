# 6.3 Fixtures & Parametrization

## Core Concepts
Fixtures provide a clean, declarative dependency injection system for test environments, while parametrization collapses repetitive tests with different inputs into a single concise test definition. Together, they eliminate duplicate setup code and ensure consistent test data.

## Key Pytest Features
- `@pytest.fixture(scope="function")`: Declares a callable dependency injected into tests by parameter name. Scopes control lifetime: `function` (default, fresh per test), `class`, `module`, or `session`.
- `@pytest.mark.parametrize("arg1,arg2", [(val1, val2), ...], ids=[...])`: Runs the test function once for each tuple in the dataset, displaying custom test identifiers in the test output.
- `conftest.py`: Root or directory-level configuration file whose fixtures are discovered automatically by pytest without explicit imports.
- `tmp_path`: Pytest built-in fixture supplying a clean, temporary `pathlib.Path` directory unique to the test.

## Testing Theory: DRY Tests & Fixture Lifecycle
- **Anti-pattern: Duplicate Test Functions**: Writing `test_tax_ca`, `test_tax_ny`, and `test_tax_tx` duplicates assertion logic. If the tax calculation signature changes, you must update dozens of tests. Parametrization tests N inputs with 1 maintenance point.
- **Test Data Factories**: Hardcoding ad-hoc dictionaries directly inside test bodies leads to brittle tests when schemas evolve. Factory functions (`make_user`, `make_order`) provide sensible defaults while allowing test cases to override only the fields relevant to their assertions.

## Connection to Exercises
In `conftest.py`, shared fixtures provide configuration dictionaries, user profiles, and file paths via `tmp_path`. In `test_data.py`, factory functions create consistent test models. In `test_parametrized_examples.py`, `@pytest.mark.parametrize` tests 7 state sales tax rules and order state machine transitions in compact, expressive matrices.

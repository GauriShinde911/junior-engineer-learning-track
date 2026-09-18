# 6.5 Integration Tests

## Core Concepts
Integration testing verifies how multiple software components, modules, or subsystems interact when wired together with real boundaries (such as a database, filesystem, or service layer). Rather than mocking dependencies, integration tests execute real business operations against genuine, isolated resources.

## Key Pytest Features
- `tmp_path`: Supplies an ephemeral, filesystem-isolated directory for creating disposable SQLite database files per test run.
- `@pytest.fixture` with `yield`: Provisions fresh schemas, establishes connections, and handles teardown by closing database handles to release OS file locks.
- `pytest.raises(sqlite3.IntegrityError)`: Asserts database-level engine constraints directly.

## Testing Theory: Unit vs Integration Boundaries
- **Unit Tests (Fast & Narrow)**: Run in-memory in microseconds, mocking network and database boundaries. Ideal for testing combinatorial logic and branch paths, but unable to detect schema bugs or SQL typos.
- **Integration Tests (Slower & Comprehensive)**: Execute against real engines (SQLite, Postgres test containers). Catch dialect incompatibilities, NULL constraints, unique index violations, and transaction rollbacks that unit test mocks fail to model accurately.
- **Test Pyramid Balance**: Maintain a large foundation of unit tests for fast feedback and a targeted layer of integration tests verifying critical persistence and contract seams.

## Connection to Exercises
In `db_repository.py`, `TaskRepository` executes real SQL DDL and CRUD operations. `test_db_repository_integration.py` runs against a genuine temporary SQLite database created via `tmp_path`, verifying auto-increment primary keys, SQL filtering, and SQLite engine-level CHECK constraints without mocks.

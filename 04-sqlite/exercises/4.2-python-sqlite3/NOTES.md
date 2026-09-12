# 4.2 Python sqlite3

The `sqlite3` standard library module provides a DB-API 2.0 compliant interface to embed a transactional relational database engine directly within a Python application.

## Key Functions & Methods

- `sqlite3.connect(path)`: Opens or creates an SQLite database file (or `:memory:`).
- `conn.cursor()`: Creates a cursor object to execute SQL commands and traverse query result sets.
- `cursor.execute(sql, params)`: Runs a query with parameter binding using `?` place-markers.
- `cursor.executemany(sql, seq_of_params)`: Executes the same SQL statement repeatedly for a list of tuples.
- `cursor.fetchone()` / `cursor.fetchall()`: Retrieves one or all remaining rows of a query result.
- `conn.commit()` / `conn.rollback()`: Saves current pending changes or reverts them to the last savepoint.
- `conn.row_factory = sqlite3.Row`: Configures cursors to return dictionary-like row objects with name-based column access.

## Core Theory: Parameterized Queries & SQL Injection

Never construct SQL queries with f-strings or string concatenation (`f"SELECT * FROM users WHERE name = '{name}'"`). An attacker supplying `' OR '1'='1` can alter query logic or drop tables. Parameterized queries (`cursor.execute("SELECT ... WHERE name = ?", (name,))`) pass user input separately to the database query engine. The engine parses query structure first and treats parameters strictly as literal values, rendering SQL injection impossible.

## Practical Implementation

In this folder, `db_connection.py` provides Python context managers that guarantee connection closure, automatic transaction rollback on exceptions, and `PRAGMA foreign_keys = ON;` configuration. `inventory_repository.py` implements the Data Access Object / Repository pattern with an `InventoryItem` dataclass, mapping raw SQLite rows to typed Python objects across all CRUD operations.

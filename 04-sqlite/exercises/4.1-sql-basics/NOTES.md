# 4.1 SQL Basics

Relational databases store structured data across tables linked by keys. SQL (Structured Query Language) is the declarative language used to define schemas (DDL) and query or modify stored data (DML).

## Key Concepts & Syntax

- `CREATE TABLE`: Defines a new table with named columns, storage data types, and structural rules.
- `PRIMARY KEY`: Uniquely identifies each row in a table and automatically creates an index.
- `FOREIGN KEY`: Establishes a reference relationship to a primary key in another table to guarantee referential integrity.
- `NOT NULL` & `CHECK`: Enforces data integrity at the database engine level (e.g., non-negative prices).
- `SELECT ... WHERE`: Retrieves rows filtering by conditions with comparison operators.
- `INNER JOIN`: Combines rows from two tables where specified linking column values match.
- `GROUP BY & HAVING`: Aggregates multiple rows into summary metrics (COUNT, SUM, AVG) per distinct group.
- `INSERT`, `UPDATE`, `DELETE`: The fundamental write operations modifying database table rows.

## Core Theory: Relational Modeling & Constraints

Instead of duplicating category descriptions across hundreds of products, relational modeling normalizes data into separate `categories` and `products` tables. A foreign key links each product to its category ID. SQLite requires `PRAGMA foreign_keys = ON;` per connection to enforce referential constraints, blocking orphan records or accidental category deletions.

## Practical Implementation

In this folder, `create_inventory_manual.sql` and `create_inventory_python.py` create a normalized inventory schema with product categories and check constraints. `queries.py` implements filtered inventory alerts, relational joins linking products to categories, and category-level stock and valuation aggregations using Python's `sqlite3` driver.

# 4.3 Schema Design

Schema design defines the relational blueprint of an application, balancing integrity, normalization, and query performance through constraints and indexes.

## Key Syntax & Directives

- `CHECK (expression)`: Validates that column values satisfy boolean business rules on every insert and update.
- `FOREIGN KEY (...) REFERENCES ... ON DELETE CASCADE / RESTRICT`: Controls relational referential integrity when parent rows are deleted.
- `CREATE INDEX idx_name ON table(col)`: Constructs an auxiliary B-Tree structure enabling rapid search without scanning entire tables.
- `DEFAULT CURRENT_TIMESTAMP`: Automatically records row creation and modification times in UTC.
- `GENERATED ALWAYS AS (...) STORED`: Computes and persists deterministic derived fields directly inside the database engine.

## Core Theory: Normalization & Indexing Tradeoffs

- **Normalization (1NF -> 3NF)**: Organizes tables so each fact is stored exactly once. 1NF eliminates repeating groups; 2NF ensures all non-key columns depend on the full primary key; 3NF removes transitive dependencies (non-key columns depending on other non-key columns). This eliminates update anomalies.
- **Indexes**: An index speeds up `WHERE`, `JOIN`, and `ORDER BY` operations from $O(N)$ linear scans to $O(\log N)$ B-Tree traversals. However, every index incurs a storage cost and slows down `INSERT`, `UPDATE`, and `DELETE` statements because the index must be kept synchronized.

## Practical Implementation

In this folder, `schema.sql` models a production-grade e-commerce relational schema across `customers`, `orders`, and `order_items` with cascading constraints, generated totals, and status checks. `schema_builder.py` provides Python automation to deploy the schema, and `DESIGN_NOTES.md` documents the design rationale.

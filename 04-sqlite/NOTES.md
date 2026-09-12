# 04. SQLite Database Management — Module Overview & Index

This skill folder covers reliable local relational persistence using Python's standard library `sqlite3` module. The curriculum progresses from raw SQL primitives to object-mapped repository patterns, multi-table schema normalization, atomic transactions, and a full standalone records management project.

---

## Curriculum Index & Subsection Overviews

1. [**4.1 SQL Basics**](exercises/4.1-sql-basics/NOTES.md)
   Fundamental DDL and DML operations: table definitions, primary/foreign keys, check constraints, filtered queries, inner joins, and aggregate groupings.

2. [**4.2 Python sqlite3**](exercises/4.2-python-sqlite3/NOTES.md)
   Standard library connection management, context managers, preventing SQL injection via parameterized queries, and typed dataclass row mapping.

3. [**4.3 Schema Design**](exercises/4.3-schema-design/NOTES.md)
   Relational database normalization (1NF–3NF), primary/foreign key cascading behaviors, performance indexing strategies, and audit timestamps.

4. [**4.4 Transactions**](exercises/4.4-transactions/NOTES.md)
   ACID compliance, atomic multi-step execution, and transaction safety using `commit()` and `rollback()` under simulated failure conditions.

- [**Independent Challenge: Local Records System**](independent/local_records_system/README.md)
  An enterprise-grade IT Asset & Maintenance Tracking system with schema validation, dynamic multi-attribute search filtering, executive analytical reports, and disaster recovery procedures.

---

## Key Takeaways

- **Zero-Dependency Persistence**: SQLite runs in-process with zero external server dependencies, making it ideal for client apps, embedded devices, and lightweight backend services.
- **Strict Parameterization**: Always pass query arguments as tuples to `cursor.execute(sql, (arg,))` to guarantee immunity against SQL injection vulnerabilities.
- **Foreign Keys Must Be Enabled**: In SQLite, foreign key enforcement is disabled by default; always execute `PRAGMA foreign_keys = ON;` upon opening every database connection.
- **All-Or-Nothing Atomicity**: Wrap multi-table modifications in explicit `try ... conn.commit() except ... conn.rollback()` blocks to prevent corrupted, partial writes.

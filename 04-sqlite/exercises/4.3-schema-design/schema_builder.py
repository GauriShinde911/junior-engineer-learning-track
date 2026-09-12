"""
4.3 Schema Design: schema_builder.py
Executes schema.sql to construct the normalized multi-table database.
Provides schema validation and inspection utilities for verification.
"""

from pathlib import Path
import sqlite3

SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"
DEFAULT_DB_FILE = Path(__file__).resolve().parent / "ecommerce.db"


def build_schema(database: str | Path | sqlite3.Connection = DEFAULT_DB_FILE) -> sqlite3.Connection:
    """
    Builds the multi-table schema by executing schema.sql.
    Enforces foreign keys and returns the active connection.
    """
    if isinstance(database, sqlite3.Connection):
        conn = database
    else:
        conn = sqlite3.connect(str(database))

    conn.execute("PRAGMA foreign_keys = ON;")
    sql_script = SCHEMA_FILE.read_text(encoding="utf-8")
    conn.executescript(sql_script)
    conn.commit()
    return conn


def inspect_schema(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """
    Introspects SQLite master catalog to return existing tables and their indexes.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, name, tbl_name
        FROM sqlite_master
        WHERE type IN ('table', 'index') AND name NOT LIKE 'sqlite_%'
        ORDER BY type, name;
    """)

    tables = []
    indexes = []
    for row in cursor.fetchall():
        obj_type, name, tbl_name = row[0], row[1], row[2]
        if obj_type == "table":
            tables.append(name)
        elif obj_type == "index":
            indexes.append(f"{name} (on {tbl_name})")

    return {"tables": sorted(tables), "indexes": sorted(indexes)}


if __name__ == "__main__":
    print(f"Applying schema from {SCHEMA_FILE.name} to {DEFAULT_DB_FILE.name}...")
    connection = build_schema(DEFAULT_DB_FILE)
    catalog = inspect_schema(connection)
    print("\nCreated Tables:")
    for table in catalog["tables"]:
        print(f"  - {table}")
    print("\nCreated Indexes:")
    for idx in catalog["indexes"]:
        print(f"  - {idx}")
    connection.close()
    print("\nSchema build complete.")

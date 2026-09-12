"""
4.2 Python sqlite3: db_connection.py
Reusable database connection and cursor helpers implementing Python context managers.
Handles pragmas, custom row factories, and transaction commit/rollback lifecycle.
"""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
import sqlite3

DEFAULT_DB_FILE = Path(__file__).resolve().parent / "app_inventory.db"


def configure_connection(conn: sqlite3.Connection) -> sqlite3.Connection:
    """Configures default SQLite pragmas and row factories."""
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_connection(
    database_uri: str | Path = DEFAULT_DB_FILE,
    autocommit: bool = True
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager yielding a configured sqlite3.Connection.
    If an unhandled exception occurs within the block, the transaction is rolled back.
    If execution completes successfully and autocommit=True, changes are committed.
    Always safely closes the connection upon exiting the block.
    """
    conn = sqlite3.connect(str(database_uri))
    configure_connection(conn)
    try:
        yield conn
        if autocommit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor(
    conn_or_uri: sqlite3.Connection | str | Path = DEFAULT_DB_FILE
) -> Generator[sqlite3.Cursor, None, None]:
    """
    Context manager yielding an active cursor.
    Supports either an existing connection or opens a managed connection from path.
    """
    if isinstance(conn_or_uri, sqlite3.Connection):
        cursor = conn_or_uri.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    else:
        with get_connection(conn_or_uri) as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

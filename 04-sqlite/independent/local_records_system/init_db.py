"""
independent/local_records_system/init_db.py
Database initialization and seeding script for the IT Asset Tracking System.
Creates fresh tables from schema.sql and seeds demo departments, assets, and service logs.
"""

from pathlib import Path
import sqlite3
import sys

CURRENT_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = CURRENT_DIR / "schema.sql"
DEFAULT_DB_PATH = CURRENT_DIR / "records.db"

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from repository import AssetRecord, AssetRepository, MaintenanceLog


def initialize_database(db_path: str | Path = DEFAULT_DB_PATH, seed: bool = True) -> sqlite3.Connection:
    """
    Initializes a fresh database by reading and applying schema.sql.
    Optionally seeds realistic department, asset, and maintenance data.
    """
    db_str = str(db_path)
    # If a real file path is provided and exists, remove for clean initialization if recreating
    conn = sqlite3.connect(db_str)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Apply DDL Schema
    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()

    if seed:
        seed_database(conn)

    return conn


def seed_database(conn: sqlite3.Connection) -> None:
    """Populates initial departments, assets, and maintenance history."""
    repo = AssetRepository(conn)

    # 1. Departments
    dept_eng = repo.create_department("ENG", "Engineering & Software Architecture")
    dept_ds = repo.create_department("DATA", "Data Science & Machine Learning")
    dept_ops = repo.create_department("OPS", "Cloud Operations & Infrastructure")
    dept_hr = repo.create_department("HR", "People Operations & Human Resources")

    # 2. Assets
    assets_to_seed = [
        AssetRecord(None, "AST-1001", "MacBook Pro 16\" M3 Max", "Laptop", dept_eng.id, "2024-01-15", 3499.00, "active"),
        AssetRecord(None, "AST-1002", "Dell Precision 5680 Workstation", "Laptop", dept_ds.id, "2024-02-10", 2850.00, "active"),
        AssetRecord(None, "AST-1003", "Dell PowerEdge R760 Rack Server", "Server", dept_ops.id, "2023-11-20", 11200.00, "active"),
        AssetRecord(None, "AST-1004", "NVIDIA RTX 6000 Ada GPU Node", "Server", dept_ds.id, "2024-03-01", 9800.00, "active"),
        AssetRecord(None, "AST-1005", "ThinkPad P1 Gen 6", "Laptop", dept_eng.id, "2023-08-14", 2200.00, "in_maintenance"),
        AssetRecord(None, "AST-1006", "Cisco Catalyst 9300 Switch 48-port", "Networking", dept_ops.id, "2022-05-18", 4100.00, "active"),
        AssetRecord(None, "AST-1007", "Logitech Rally Plus Conference Cam", "Office Equipment", dept_hr.id, "2023-01-22", 1850.00, "active"),
        AssetRecord(None, "AST-1008", "iPad Pro 12.9 M2 Display Unit", "Tablet", dept_hr.id, "2022-09-10", 1199.00, "retired"),
    ]

    saved_assets = []
    for ast in assets_to_seed:
        saved = repo.create_asset(ast)
        saved_assets.append(saved)

    # 3. Maintenance Records
    repo.log_maintenance(
        MaintenanceLog(
            None,
            saved_assets[4].id,  # ThinkPad P1
            "2024-04-10",
            "Swollen battery replacement and motherboard thermal repasting",
            320.00,
            "Premier Hardware Solutions",
        )
    )
    repo.log_maintenance(
        MaintenanceLog(
            None,
            saved_assets[2].id,  # PowerEdge R760
            "2024-02-15",
            "Failed hot-swap redundant power supply module replacement",
            450.00,
            "Dell Enterprise Mission-Critical Support",
        )
    )
    repo.log_maintenance(
        MaintenanceLog(
            None,
            saved_assets[2].id,  # PowerEdge R760
            "2024-06-01",
            "Firmware update and secondary SAS SSD replacement",
            280.00,
            "In-house Cloud Ops Team",
        )
    )


if __name__ == "__main__":
    print(f"Initializing Local Records Database at: {DEFAULT_DB_PATH}")
    connection = initialize_database(DEFAULT_DB_PATH, seed=True)
    cur = connection.cursor()
    cur.execute("SELECT COUNT(*) FROM assets;")
    total_assets = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM maintenance_logs;")
    total_logs = cur.fetchone()[0]
    print(f"Database successfully created and seeded with {total_assets} assets and {total_logs} maintenance logs.")
    connection.close()

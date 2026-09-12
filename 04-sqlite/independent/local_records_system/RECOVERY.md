# Disaster Recovery & Operational Runbook: Local Records System

This runbook outlines operational procedures for diagnosing database health, executing reliable backups, and recovering from corruption or accidental data loss in `records.db`.

---

## 1. Health Diagnostics & Corruption Detection

SQLite provides built-in integrity check pragmas to identify disk read errors, index desynchronization, or malformed B-Trees.

### Command-Line Diagnostic
```bash
# Run a comprehensive integrity check (returns "ok" if healthy)
python -c "import sqlite3; conn = sqlite3.connect('04-sqlite/independent/local_records_system/records.db'); print(conn.execute('PRAGMA integrity_check;').fetchall()); conn.close()"
```

### Fast Health Check (Non-locking)
```python
import sqlite3

def check_database_health(db_path: str) -> bool:
    with sqlite3.connect(db_path) as conn:
        result = conn.execute("PRAGMA quick_check;").fetchone()
        return result[0] == "ok"
```

If `PRAGMA integrity_check` returns anything other than `[('ok',)]`, the database file has suffered low-level corruption (e.g., partial disk write, sudden system reboot during non-WAL write).

---

## 2. Backup Procedures

Never use raw file copies (`cp` or `shutil.copy`) on an active SQLite database because copying during a transaction write can yield a torn page. Always use SQLite's native online backup API.

### Automated Online Backup Script
```python
import sqlite3
from pathlib import Path
from datetime import datetime

def perform_online_backup(source_db: str, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"records_backup_{timestamp}.db"

    # Open live database and target backup
    with sqlite3.connect(source_db) as src, sqlite3.connect(str(backup_file)) as dst:
        # Performs a non-blocking page-by-page transaction-safe snapshot
        src.backup(dst, pages=100)

    print(f"Backup successfully written to: {backup_file}")
    return backup_file
```

---

## 3. Recovery & Reinitialization Procedures

### Scenario A: Accidental Deletion / Total Loss
If `records.db` is accidentally deleted and no backup is available:
1. Re-run `init_db.py` to recreate all schema DDL and indexes:
   ```bash
   python 04-sqlite/independent/local_records_system/init_db.py
   ```
2. Verify table creation and integrity.

### Scenario B: Database Corrupted, Restoring from Backup
1. Move the corrupted file aside:
   ```bash
   mv 04-sqlite/independent/local_records_system/records.db 04-sqlite/independent/local_records_system/records.corrupt.bak
   ```
2. Identify the latest valid backup:
   ```bash
   ls -lt backups/
   ```
3. Run `PRAGMA integrity_check` on the backup to ensure it is clean.
4. Copy the verified backup to `records.db`.

### Scenario C: Salvaging Data from a Corrupted DB via SQL Dump
If a database fails `integrity_check` but contains unsaved data:
1. Dump surviving records to plain SQL:
   ```bash
   sqlite3 records.db ".recover" > recovered_data.sql
   ```
2. Reinitialize a clean database:
   ```bash
   python 04-sqlite/independent/local_records_system/init_db.py
   ```
3. Import the recovered SQL stream into the clean schema.

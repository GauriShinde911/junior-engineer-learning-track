# Local Records System: Enterprise IT Asset & Maintenance Tracker

An enterprise-grade local record-keeping and tracking system for IT equipment, department allocations, and service maintenance histories powered by Python's standard library `sqlite3` engine.

---

## Architecture Overview

- **`schema.sql`**: Relational DDL with foreign key constraints, data validation checks, and lookup indexes across `departments`, `assets`, and `maintenance_logs`.
- **`repository.py`**: Typed data access layer providing parameterized CRUD, transactional writes, and multi-criteria search filtering.
- **`reporting.py`**: Executive summary aggregations (department valuations, maintenance costs, repair-to-purchase ratios).
- **`init_db.py`**: Automation script to build tables from `schema.sql` and seed initial records.
- **`RECOVERY.md`**: Operational runbook covering database backups, integrity checks, and disaster recovery.

---

## Getting Started

### 1. Initialize Database
Initialize the database file and load sample seed data:

```bash
python 04-sqlite/independent/local_records_system/init_db.py
```

This generates `records.db` with sample departments, enterprise hardware assets, and historical maintenance events.

---

## Usage Examples

### Searching Assets by Multiple Criteria
```python
import sqlite3
from repository import AssetRepository

conn = sqlite3.connect("04-sqlite/independent/local_records_system/records.db")
repo = AssetRepository(conn)

# Filter active laptops costing over $2,000
results = repo.search_assets(category="Laptop", status="active", min_cost=2000.00)
for asset in results:
    print(f"[{asset['asset_tag']}] {asset['asset_name']} - ${asset['purchase_cost']:,.2f} ({asset['department_name']})")

conn.close()
```

### Logging a Maintenance Service Event
```python
from repository import AssetRepository, MaintenanceLog

conn = sqlite3.connect("04-sqlite/independent/local_records_system/records.db")
repo = AssetRepository(conn)

log = repo.log_maintenance(
    MaintenanceLog(
        id=None,
        asset_id=1,
        service_date="2024-07-15",
        description="Replaced faulty keyboard switch cluster",
        cost=110.00,
        performed_by="Onsite Tech Support"
    )
)
print(f"Logged service record #{log.id}")
conn.close()
```

### Running Management Reports
```python
import sqlite3
from reporting import get_department_valuation_summary, get_high_cost_maintenance_assets

conn = sqlite3.connect("04-sqlite/independent/local_records_system/records.db")

print("--- Department Asset Allocations ---")
for dept in get_department_valuation_summary(conn):
    print(f"{dept['department_name']}: {dept['total_assets']} assets, Total: ${dept['total_capital_cost']:,.2f}")

print("\n--- High Maintenance Assets (> $500 Total Repair Spend) ---")
for item in get_high_cost_maintenance_assets(conn, threshold=500.0):
    print(f"{item['asset_tag']} ({item['asset_name']}): ${item['total_repair_spend']:.2f} total repairs ({item['repair_to_purchase_ratio_pct']}% of purchase cost)")

conn.close()
```

---

## Running Automated Tests

Run the test suite verifying the repository, search logic, reporting, and foreign key cascades:

```bash
python -m pytest 04-sqlite/tests/test_independent_local_records.py
```

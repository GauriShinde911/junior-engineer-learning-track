"""
Unit tests for independent/local_records_system:
- init_db.py (schema creation & seeding)
- repository.py (AssetRepository CRUD, dynamic search filtering, constraints)
- reporting.py (Department valuations, expense reports, threshold audits)
"""

from pathlib import Path
import sqlite3
import sys
import pytest

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
PROJECT_DIR = MODULE_DIR / "independent" / "local_records_system"
sys.path.insert(0, str(PROJECT_DIR))

from init_db import initialize_database
from repository import AssetRecord, AssetRepository, MaintenanceLog
from reporting import (
    get_department_valuation_summary,
    get_high_cost_maintenance_assets,
    get_maintenance_expense_report,
    get_status_distribution,
)


@pytest.fixture
def records_db():
    """Provides a fresh, seeded in-memory instance of the local records system."""
    conn = initialize_database(":memory:", seed=True)
    yield conn
    conn.close()


@pytest.fixture
def empty_repo():
    """Provides an empty repository for isolated CRUD tests."""
    conn = initialize_database(":memory:", seed=False)
    repo = AssetRepository(conn)
    yield repo, conn
    conn.close()


# --- Initialization & Seeding Tests ---

def test_database_initialization_seeds_data(records_db):
    """Happy Path: Verify initial seeded departments, assets, and logs."""
    cur = records_db.cursor()
    cur.execute("SELECT COUNT(*) FROM departments;")
    assert cur.fetchone()[0] == 4

    cur.execute("SELECT COUNT(*) FROM assets;")
    assert cur.fetchone()[0] == 8

    cur.execute("SELECT COUNT(*) FROM maintenance_logs;")
    assert cur.fetchone()[0] == 3


# --- Asset Repository CRUD Tests ---

def test_asset_crud_lifecycle(empty_repo):
    """Happy Path: Complete Create, Read, Update, Delete lifecycle for an asset."""
    repo, conn = empty_repo
    dept = repo.create_department("QA", "Quality Assurance & Testing")

    # 1. Create
    asset = AssetRecord(
        id=None,
        asset_tag="AST-QA-01",
        name="Pixel 8 Pro Test Device",
        category="Mobile",
        department_id=dept.id,
        purchase_date="2024-05-01",
        purchase_cost=999.00,
        status="active",
    )
    saved = repo.create_asset(asset)
    assert saved.id is not None

    # 2. Read by ID & Tag
    by_id = repo.get_asset_by_id(saved.id)
    assert by_id is not None
    assert by_id.name == "Pixel 8 Pro Test Device"

    by_tag = repo.get_asset_by_tag("ast-qa-01")  # Case-insensitive
    assert by_tag is not None
    assert by_tag.id == saved.id

    # 3. Update
    by_id.status = "in_maintenance"
    by_id.purchase_cost = 899.00
    updated = repo.update_asset(by_id)
    assert updated is True

    reloaded = repo.get_asset_by_id(saved.id)
    assert reloaded.status == "in_maintenance"
    assert reloaded.purchase_cost == 899.00

    # 4. Delete
    deleted = repo.delete_asset(saved.id)
    assert deleted is True
    assert repo.get_asset_by_id(saved.id) is None


def test_duplicate_asset_tag_raises_error(empty_repo):
    """Negative Case: Inserting duplicate asset_tag raises ValueError."""
    repo, _ = empty_repo
    dept = repo.create_department("HR", "Human Resources")
    repo.create_asset(
        AssetRecord(None, "TAG-DUP", "Monitor A", "Peripherals", dept.id, "2024-01-01", 200.0)
    )
    with pytest.raises(ValueError, match="Failed to create asset 'TAG-DUP'"):
        repo.create_asset(
            AssetRecord(None, "TAG-DUP", "Monitor B", "Peripherals", dept.id, "2024-01-01", 250.0)
        )


def test_invalid_department_foreign_key_fails(empty_repo):
    """Negative Case: Assigning a non-existent department_id violates foreign key integrity."""
    repo, _ = empty_repo
    with pytest.raises(ValueError, match="FOREIGN KEY constraint failed"):
        repo.create_asset(
            AssetRecord(None, "TAG-NODPT", "Server", "Server", 999, "2024-01-01", 5000.0)
        )


def test_maintenance_logging_and_cascade_delete(empty_repo):
    """Happy Path: Log service event and confirm cascade deletion when asset is deleted."""
    repo, _ = empty_repo
    dept = repo.create_department("FIN", "Finance")
    asset = repo.create_asset(
        AssetRecord(None, "AST-FIN-1", "Office Printer", "Office Equipment", dept.id, "2023-01-01", 600.0)
    )

    # Log maintenance
    log = repo.log_maintenance(
        MaintenanceLog(None, asset.id, "2024-03-01", "Roller replacement", 75.00, "Xerox Support")
    )
    assert log.id is not None

    history = repo.get_maintenance_history(asset.id)
    assert len(history) == 1
    assert history[0].cost == 75.00

    # Delete asset and verify maintenance logs cascade delete
    repo.delete_asset(asset.id)
    history_after = repo.get_maintenance_history(asset.id)
    assert len(history_after) == 0


# --- Search and Filter Tests ---

def test_search_assets_with_filters(records_db):
    """Happy Path: Test multi-attribute compound search filters."""
    repo = AssetRepository(records_db)

    # 1. Search by keyword
    kw_results = repo.search_assets(keyword="MacBook")
    assert len(kw_results) == 1
    assert kw_results[0]["asset_tag"] == "AST-1001"

    # 2. Search by category & status
    laptop_results = repo.search_assets(category="Laptop", status="active")
    assert len(laptop_results) == 2

    # 3. Search by cost range
    expensive = repo.search_assets(min_cost=4000.00)
    tags = [r["asset_tag"] for r in expensive]
    assert "AST-1003" in tags  # Server $11,200
    assert "AST-1004" in tags  # Server $9,800
    assert "AST-1006" in tags  # Switch $4,100


# --- Reporting Analytics Tests ---

def test_reporting_queries(records_db):
    """Happy Path: Analytical report generation."""
    # Department valuation
    dept_summary = get_department_valuation_summary(records_db)
    assert len(dept_summary) == 4
    for dept in dept_summary:
        assert "total_capital_cost" in dept
        assert "total_assets" in dept

    # Status distribution
    status_dist = get_status_distribution(records_db)
    statuses = [s["status"] for s in status_dist]
    assert "active" in statuses
    assert "in_maintenance" in statuses

    # Maintenance expense report
    expense_report = get_maintenance_expense_report(records_db)
    assert len(expense_report) > 0

    # High cost audit
    high_cost = get_high_cost_maintenance_assets(records_db, threshold=300.0)
    assert len(high_cost) >= 1
    top_asset = high_cost[0]
    assert top_asset["total_repair_spend"] >= 300.0

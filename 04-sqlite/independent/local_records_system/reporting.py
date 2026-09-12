"""
independent/local_records_system/reporting.py
Analytical and managerial reporting queries for the local records tracking system.
Generates valuation summaries, departmental asset allocations, and maintenance expenditure reports.
"""

import sqlite3
from typing import Any


def get_department_valuation_summary(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """
    Returns asset count, total capital expenditure, and average asset cost per department.
    """
    cursor = conn.cursor()
    query = """
        SELECT
            d.code AS department_code,
            d.name AS department_name,
            COUNT(a.id) AS total_assets,
            COALESCE(ROUND(SUM(a.purchase_cost), 2), 0.0) AS total_capital_cost,
            COALESCE(ROUND(AVG(a.purchase_cost), 2), 0.0) AS avg_asset_cost
        FROM departments d
        LEFT JOIN assets a ON d.id = a.department_id
        GROUP BY d.id, d.code, d.name
        ORDER BY total_capital_cost DESC;
    """
    cursor.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def get_status_distribution(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """
    Returns asset distribution by operational status (active, in_maintenance, retired).
    """
    cursor = conn.cursor()
    query = """
        SELECT
            status,
            COUNT(id) AS count,
            ROUND(SUM(purchase_cost), 2) AS total_cost
        FROM assets
        GROUP BY status
        ORDER BY count DESC;
    """
    cursor.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def get_maintenance_expense_report(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """
    Aggregates maintenance incident counts and total repair expenditures grouped by asset category.
    """
    cursor = conn.cursor()
    query = """
        SELECT
            a.category,
            COUNT(m.id) AS maintenance_events,
            COALESCE(ROUND(SUM(m.cost), 2), 0.0) AS total_maintenance_spend,
            COALESCE(ROUND(AVG(m.cost), 2), 0.0) AS avg_repair_cost
        FROM assets a
        LEFT JOIN maintenance_logs m ON a.id = m.asset_id
        GROUP BY a.category
        ORDER BY total_maintenance_spend DESC;
    """
    cursor.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def get_high_cost_maintenance_assets(conn: sqlite3.Connection, threshold: float = 500.0) -> list[dict[str, Any]]:
    """
    Identifies assets whose cumulative maintenance costs exceed a specified financial threshold.
    Useful for repair vs. replace decisions.
    """
    cursor = conn.cursor()
    query = """
        SELECT
            a.id,
            a.asset_tag,
            a.name AS asset_name,
            a.category,
            a.purchase_cost,
            COUNT(m.id) AS service_count,
            ROUND(SUM(m.cost), 2) AS total_repair_spend,
            ROUND((SUM(m.cost) / a.purchase_cost) * 100, 1) AS repair_to_purchase_ratio_pct
        FROM assets a
        INNER JOIN maintenance_logs m ON a.id = m.asset_id
        GROUP BY a.id, a.asset_tag, a.name, a.category, a.purchase_cost
        HAVING total_repair_spend >= ?
        ORDER BY total_repair_spend DESC;
    """
    cursor.execute(query, (threshold,))
    return [dict(row) for row in cursor.fetchall()]

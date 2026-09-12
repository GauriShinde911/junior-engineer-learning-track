"""
independent/local_records_system/repository.py
Comprehensive repository for the IT Asset Tracking System.
Implements full CRUD, advanced multi-attribute searching/filtering,
and foreign-key constrained maintenance logging.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
import sqlite3
from typing import Any


@dataclass
class Department:
    id: int | None
    code: str
    name: str


@dataclass
class AssetRecord:
    id: int | None
    asset_tag: str
    name: str
    category: str
    department_id: int
    purchase_date: str
    purchase_cost: float
    status: str = "active"
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class MaintenanceLog:
    id: int | None
    asset_id: int
    service_date: str
    description: str
    cost: float
    performed_by: str
    created_at: str | None = None


class AssetRepository:
    """Encapsulates all database operations for assets, departments, and maintenance."""

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")

    # --- Department Operations ---

    def create_department(self, code: str, name: str) -> Department:
        sql = "INSERT INTO departments (code, name) VALUES (?, ?);"
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, (code.strip().upper(), name.strip()))
            self.conn.commit()
            return Department(cursor.lastrowid, code.strip().upper(), name.strip())
        except sqlite3.IntegrityError as err:
            self.conn.rollback()
            raise ValueError(f"Department code '{code}' already exists.") from err

    def list_departments(self) -> list[Department]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, code, name FROM departments ORDER BY code ASC;")
        return [Department(row["id"], row["code"], row["name"]) for row in cursor.fetchall()]

    # --- Asset CRUD Operations ---

    def create_asset(self, asset: AssetRecord) -> AssetRecord:
        sql = """
            INSERT INTO assets (asset_tag, name, category, department_id, purchase_date, purchase_cost, status)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                sql,
                (
                    asset.asset_tag.strip().upper(),
                    asset.name.strip(),
                    asset.category.strip(),
                    asset.department_id,
                    asset.purchase_date,
                    asset.purchase_cost,
                    asset.status,
                ),
            )
            self.conn.commit()
            asset.id = cursor.lastrowid
            return asset
        except sqlite3.IntegrityError as err:
            self.conn.rollback()
            raise ValueError(f"Failed to create asset '{asset.asset_tag}': {err}") from err

    def get_asset_by_id(self, asset_id: int) -> AssetRecord | None:
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT id, asset_tag, name, category, department_id, purchase_date, purchase_cost,
                      status, created_at, updated_at
               FROM assets WHERE id = ?;""",
            (asset_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return AssetRecord(
            id=row["id"],
            asset_tag=row["asset_tag"],
            name=row["name"],
            category=row["category"],
            department_id=row["department_id"],
            purchase_date=row["purchase_date"],
            purchase_cost=float(row["purchase_cost"]),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_asset_by_tag(self, asset_tag: str) -> AssetRecord | None:
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT id, asset_tag, name, category, department_id, purchase_date, purchase_cost,
                      status, created_at, updated_at
               FROM assets WHERE asset_tag = ?;""",
            (asset_tag.strip().upper(),),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return AssetRecord(
            id=row["id"],
            asset_tag=row["asset_tag"],
            name=row["name"],
            category=row["category"],
            department_id=row["department_id"],
            purchase_date=row["purchase_date"],
            purchase_cost=float(row["purchase_cost"]),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def update_asset(self, asset: AssetRecord) -> bool:
        if asset.id is None:
            raise ValueError("Asset ID is required for update.")

        sql = """
            UPDATE assets
            SET asset_tag = ?, name = ?, category = ?, department_id = ?,
                purchase_date = ?, purchase_cost = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                sql,
                (
                    asset.asset_tag.strip().upper(),
                    asset.name.strip(),
                    asset.category.strip(),
                    asset.department_id,
                    asset.purchase_date,
                    asset.purchase_cost,
                    asset.status,
                    asset.id,
                ),
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as err:
            self.conn.rollback()
            raise ValueError(f"Update failed for asset ID {asset.id}: {err}") from err

    def delete_asset(self, asset_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM assets WHERE id = ?;", (asset_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # --- Search and Filter Capability ---

    def search_assets(
        self,
        keyword: str | None = None,
        department_id: int | None = None,
        category: str | None = None,
        status: str | None = None,
        min_cost: float | None = None,
        max_cost: float | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Dynamically builds a parameterized SQL query with compound filter conditions.
        Returns asset details enriched with department information.
        """
        base_sql = """
            SELECT a.id, a.asset_tag, a.name AS asset_name, a.category,
                   d.code AS department_code, d.name AS department_name,
                   a.purchase_date, a.purchase_cost, a.status, a.created_at
            FROM assets a
            INNER JOIN departments d ON a.department_id = d.id
            WHERE 1=1
        """
        params: list[Any] = []

        if keyword:
            base_sql += " AND (a.name LIKE ? OR a.asset_tag LIKE ?)"
            wildcard = f"%{keyword.strip()}%"
            params.extend([wildcard, wildcard])

        if department_id is not None:
            base_sql += " AND a.department_id = ?"
            params.append(department_id)

        if category:
            base_sql += " AND a.category = ?"
            params.append(category.strip())

        if status:
            base_sql += " AND a.status = ?"
            params.append(status.strip())

        if min_cost is not None:
            base_sql += " AND a.purchase_cost >= ?"
            params.append(min_cost)

        if max_cost is not None:
            base_sql += " AND a.purchase_cost <= ?"
            params.append(max_cost)

        base_sql += " ORDER BY a.purchase_cost DESC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        cursor = self.conn.cursor()
        cursor.execute(base_sql, params)
        return [dict(row) for row in cursor.fetchall()]

    # --- Maintenance Logging Operations ---

    def log_maintenance(self, log: MaintenanceLog) -> MaintenanceLog:
        """Records a maintenance service event for an asset."""
        cursor = self.conn.cursor()
        sql = """
            INSERT INTO maintenance_logs (asset_id, service_date, description, cost, performed_by)
            VALUES (?, ?, ?, ?, ?);
        """
        try:
            cursor.execute(
                sql,
                (log.asset_id, log.service_date, log.description, log.cost, log.performed_by),
            )
            self.conn.commit()
            log.id = cursor.lastrowid
            return log
        except sqlite3.IntegrityError as err:
            self.conn.rollback()
            raise ValueError(f"Failed to log maintenance for asset ID {log.asset_id}: {err}") from err

    def get_maintenance_history(self, asset_id: int) -> list[MaintenanceLog]:
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT id, asset_id, service_date, description, cost, performed_by, created_at
               FROM maintenance_logs
               WHERE asset_id = ?
               ORDER BY service_date DESC;""",
            (asset_id,),
        )
        return [
            MaintenanceLog(
                id=row["id"],
                asset_id=row["asset_id"],
                service_date=row["service_date"],
                description=row["description"],
                cost=float(row["cost"]),
                performed_by=row["performed_by"],
                created_at=row["created_at"],
            )
            for row in cursor.fetchall()
        ]

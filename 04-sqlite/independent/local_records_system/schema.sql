-- Local Records System: Enterprise IT Asset & Maintenance Tracking Schema
-- Enforces referential integrity, check constraints, audit timestamps, and indexing.

PRAGMA foreign_keys = ON;

-- Departments Lookup Table
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

-- Assets Core Records Table
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_tag TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    purchase_date TEXT NOT NULL,
    purchase_cost REAL NOT NULL CHECK (purchase_cost >= 0.0),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'in_maintenance', 'retired')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT
);

-- Maintenance & Service Logs
CREATE TABLE IF NOT EXISTS maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    service_date TEXT NOT NULL,
    description TEXT NOT NULL,
    cost REAL NOT NULL CHECK (cost >= 0.0),
    performed_by TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

-- Indexes for Fast Querying and Relational Joins
CREATE INDEX IF NOT EXISTS idx_assets_department ON assets(department_id);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category);
CREATE INDEX IF NOT EXISTS idx_maintenance_asset_id ON maintenance_logs(asset_id);

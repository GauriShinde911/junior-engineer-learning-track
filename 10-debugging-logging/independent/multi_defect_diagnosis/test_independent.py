import os
import sys
from pathlib import Path
import pytest

CHALLENGE_DIR = Path(__file__).resolve().parent
FIXED_APP_DIR = CHALLENGE_DIR / "fixed_app"
BROKEN_APP_DIR = CHALLENGE_DIR / "broken_app"

# Import fixed app components safely
if str(FIXED_APP_DIR) not in sys.path:
    sys.path.insert(0, str(FIXED_APP_DIR))

import config as fixed_config
import inventory as fixed_inventory
import pricing as fixed_pricing
import main as fixed_main


def test_fixed_config_path_resolution_and_env_coercion(monkeypatch):
    catalog = fixed_config.load_catalog()
    assert "KEYBOARD" in catalog
    assert catalog["KEYBOARD"]["price"] == 100.00

    # Test env var string coercion to integer
    monkeypatch.setenv("BATCH_LIMIT", "35")
    limit = fixed_config.get_batch_limit()
    assert limit == 35
    assert isinstance(limit, int)


def test_fixed_inventory_atomic_reservation_on_failure():
    catalog = fixed_config.load_catalog()
    inv = fixed_inventory.InventoryManager(catalog)
    initial_mouse_stock = inv.stock["MOUSE"]

    order = [
        {"sku": "MOUSE", "quantity": 10},
        {"sku": "MONITOR", "quantity": 999},  # Cannot be fulfilled (only 5 in stock)
    ]

    with pytest.raises(fixed_inventory.OutOfStockError):
        inv.reserve_items(order)

    # In fixed app, MOUSE stock must not be deducted
    assert inv.stock["MOUSE"] == initial_mouse_stock


def test_fixed_pricing_exact_100_boundary_and_tax():
    catalog = fixed_config.load_catalog()
    order = [{"sku": "KEYBOARD", "quantity": 1}]  # Exactly $100.00

    pricing = fixed_pricing.calculate_pricing(order, catalog, tax_rate=0.10)
    assert pricing["subtotal"] == 100.00
    assert pricing["discount"] == 15.00  # 15% discount applied at $100.00
    assert pricing["tax"] == 8.50       # 10% on ($100 - $15 = $85)
    assert pricing["total"] == 93.50     # $85 + $8.50


def test_fixed_pipeline_end_to_end_execution():
    order = [
        {"sku": "MOUSE", "quantity": 2},     # 2 * $25 = $50
        {"sku": "KEYBOARD", "quantity": 1},  # 1 * $100 = $100. Subtotal $150
    ]
    result = fixed_main.process_order_batch(order)
    assert result["status"] == "APPROVED"
    assert result["pricing"]["subtotal"] == 150.00
    assert result["pricing"]["discount"] == 22.50  # 15% of $150

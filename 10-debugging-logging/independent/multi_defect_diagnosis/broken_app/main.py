"""
broken_app/main.py - Pipeline Orchestrator

Integrates configuration loading, batch size checking, inventory reservation,
and pricing calculation for batch orders.
"""

from typing import List, Dict, Any
from config import load_catalog, get_batch_limit
from inventory import InventoryManager, OutOfStockError
from pricing import calculate_pricing


def process_order_batch(order_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    catalog = load_catalog()
    batch_limit = get_batch_limit()

    total_units = sum(item["quantity"] for item in order_items)
    
    # Can crash with TypeError if get_batch_limit() returned str from os.getenv
    if total_units > batch_limit:
        raise ValueError(f"Batch unit limit exceeded: {total_units} > {batch_limit}")

    inventory = InventoryManager(catalog)
    inventory.reserve_items(order_items)
    pricing = calculate_pricing(order_items, catalog)

    return {
        "status": "APPROVED",
        "pricing": pricing,
        "remaining_stock": inventory.stock
    }


if __name__ == "__main__":
    test_order = [
        {"sku": "KEYBOARD", "quantity": 1},  # Exactly $100.00
    ]
    try:
        res = process_order_batch(test_order)
        print("Order result:", res)
    except Exception as e:
        print("Pipeline execution failed:", type(e).__name__, e)

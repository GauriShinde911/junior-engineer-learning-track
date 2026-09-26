"""
fixed_app/inventory.py - Stock Reservation & Warehouse Management (Fixed)

FIX APPLIED:
Implemented two-phase validation before mutation.
Phase 1: Validates SKU existence and stock sufficiency across the full batch.
Phase 2: Deducts stock atomically only after all items are confirmed.
"""

from typing import Dict, List, Any


class OutOfStockError(Exception):
    pass


class InventoryManager:
    def __init__(self, catalog: Dict[str, Any]):
        self.stock = {sku: item["stock"] for sku, item in catalog.items()}

    def reserve_items(self, order_items: List[Dict[str, Any]]) -> None:
        """
        Atomically reserves stock. If any item is unavailable, stock is not mutated.
        """
        # Phase 1: Aggregate and validate
        aggregated: Dict[str, int] = {}
        for req in order_items:
            sku = req["sku"]
            qty = req["quantity"]

            if sku not in self.stock:
                raise KeyError(f"Unknown SKU {sku}")
            aggregated[sku] = aggregated.get(sku, 0) + qty

        for sku, total_needed in aggregated.items():
            if self.stock[sku] < total_needed:
                raise OutOfStockError(
                    f"Insufficient stock for {sku}: requested {total_needed}, available {self.stock[sku]}"
                )

        # Phase 2: Apply mutations
        for sku, total_needed in aggregated.items():
            self.stock[sku] -= total_needed

"""
broken_app/inventory.py - Stock Reservation & Warehouse Management

PLANTED DEFECT 2:
State mutation without rollback. During multi-item order fulfillment, item stock
is subtracted immediately in a loop. If a later item in the order has insufficient stock,
the earlier items remain permanently deducted, corrupting inventory balances.
"""

from typing import Dict, List, Any


class OutOfStockError(Exception):
    pass


class InventoryManager:
    def __init__(self, catalog: Dict[str, Any]):
        self.stock = {sku: item["stock"] for sku, item in catalog.items()}

    def reserve_items(self, order_items: List[Dict[str, Any]]) -> None:
        """
        DEFECT 2: In-place sequential mutation without atomic guarantee.
        """
        for req in order_items:
            sku = req["sku"]
            qty = req["quantity"]

            if sku not in self.stock:
                raise KeyError(f"Unknown SKU {sku}")

            if self.stock[sku] < qty:
                # Raises error, but previously processed items in order_items remain subtracted!
                raise OutOfStockError(
                    f"Insufficient stock for {sku}: requested {qty}, available {self.stock[sku]}"
                )

            # Mutates state immediately before the rest of the order is verified
            self.stock[sku] -= qty

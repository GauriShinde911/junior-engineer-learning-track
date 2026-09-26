"""
broken_program_3.py - Multi-Warehouse Inventory Transfer Service

Problem Description:
The warehouse service processes batch transfer requests between facilities.
In the buggy implementation, inventory levels are mutated directly in-place during iteration.
If a later item in the batch fails due to insufficient stock or invalid IDs, the earlier items
have already mutated the source and target warehouse states, leaving inventory corrupted
with no rollback mechanism.
"""

from typing import List, Dict, Any


class InsufficientStockError(Exception):
    """Raised when source warehouse does not have enough stock."""
    pass


class InvalidItemError(Exception):
    """Raised when an item does not exist in the warehouse."""
    pass


def transfer_inventory_batch_buggy(
    source: Dict[str, int],
    target: Dict[str, int],
    transfers: List[Dict[str, Any]]
) -> None:
    """
    BUGGY IMPLEMENTATION:
    Mutates source and target dictionaries sequentially.
    Bug: If an exception is raised on item N, items 1..(N-1) remain deducted and transferred!
    """
    for item in transfers:
        sku = item["sku"]
        qty = item["quantity"]
        
        if sku not in source:
            raise InvalidItemError(f"SKU {sku} not found in source inventory")
        if source[sku] < qty:
            raise InsufficientStockError(f"Insufficient stock for SKU {sku}: available {source[sku]}, requested {qty}")
        
        # Immediate in-place mutation without atomic transaction or rollback
        source[sku] -= qty
        target[sku] = target.get(sku, 0) + qty


def transfer_inventory_batch_fixed(
    source: Dict[str, int],
    target: Dict[str, int],
    transfers: List[Dict[str, Any]]
) -> None:
    """
    CORRECTED IMPLEMENTATION:
    Employs two-phase commit / validation before mutation.
    Validates all requested items first against aggregate needs before applying mutations.
    """
    # Phase 1: Validate input and compute aggregated deductions
    deductions: Dict[str, int] = {}
    for item in transfers:
        sku = item["sku"]
        qty = item["quantity"]
        if qty <= 0:
            raise ValueError(f"Quantity must be positive for SKU {sku}")
        deductions[sku] = deductions.get(sku, 0) + qty

    # Check existence and total capacity across the entire batch
    for sku, total_needed in deductions.items():
        if sku not in source:
            raise InvalidItemError(f"SKU {sku} not found in source inventory")
        if source[sku] < total_needed:
            raise InsufficientStockError(
                f"Insufficient stock for SKU {sku}: available {source[sku]}, requested {total_needed}"
            )

    # Phase 2: All items validated. Perform atomic mutations
    for sku, total_qty in deductions.items():
        source[sku] -= total_qty
        target[sku] = target.get(sku, 0) + total_qty


if __name__ == "__main__":
    source_wh = {"LAPTOP": 10, "MOUSE": 50, "MONITOR": 2}
    target_wh = {"LAPTOP": 0, "MOUSE": 0, "MONITOR": 0}
    
    batch = [
        {"sku": "LAPTOP", "quantity": 3},
        {"sku": "MOUSE", "quantity": 10},
        {"sku": "MONITOR", "quantity": 5},  # Exceeds available stock (2)
    ]
    
    print("Initial source:", source_wh)
    try:
        transfer_inventory_batch_buggy(source_wh, target_wh, batch)
    except InsufficientStockError as e:
        print("Buggy transfer failed with error:", e)
        print("Corrupted source after failed buggy transfer:", source_wh)
        print("Corrupted target after failed buggy transfer:", target_wh)

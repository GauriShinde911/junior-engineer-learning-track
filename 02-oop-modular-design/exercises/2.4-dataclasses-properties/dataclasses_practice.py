"""
Exercise 2.4: Dataclasses & Properties

Demonstrates:
- @dataclass auto-generating __init__, __repr__, and __eq__
- __post_init__ for validation after the generated constructor runs
- frozen=True for immutable, hashable dataclasses
- field(default_factory=list) to avoid mutable default pitfalls
- dataclasses.asdict() for JSON-ready serialization
- @property on a regular class for comparison (so you see what dataclass saves you)
"""

from dataclasses import dataclass, field, asdict
from typing import List


# =====================================================================
# 1. BASIC DATACLASS WITH __post_init__ VALIDATION
# =====================================================================
@dataclass
class ProductRecord:
    """
    Represents a catalogue product.
    __post_init__ runs automatically after the generated __init__,
    giving us a clean place to validate without writing a manual __init__.
    """
    name: str
    price: float
    sku: str

    def __post_init__(self):
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Product name cannot be blank.")
        if self.price < 0:
            raise ValueError(f"Price must be non-negative, got {self.price}.")
        self.sku = self.sku.strip().upper()


# =====================================================================
# 2. FROZEN DATACLASS — IMMUTABLE & HASHABLE
# =====================================================================
@dataclass(frozen=True)
class StockEntry:
    """
    Represents a warehouse location snapshot.
    frozen=True means no attribute can be reassigned after creation.
    Frozen dataclasses are hashable, so they can be used as dict keys or in sets.
    """
    warehouse_id: str
    aisle: str
    shelf: int

    def label(self) -> str:
        return f"{self.warehouse_id}:{self.aisle}{self.shelf}"


# =====================================================================
# 3. DATACLASS WITH MUTABLE DEFAULT (use field, NOT bare [])
# =====================================================================
@dataclass
class Warehouse:
    """
    Manages a collection of ProductRecords.

    IMPORTANT: Never write `products: list = []` as a class-level default.
    Every instance would share the SAME list object, causing hard-to-find bugs.
    Use `field(default_factory=list)` instead — each instance gets its own list.
    """
    name: str
    location: str
    products: List[ProductRecord] = field(default_factory=list)

    def add_product(self, product: ProductRecord) -> None:
        if not isinstance(product, ProductRecord):
            raise TypeError("Expected a ProductRecord instance.")
        self.products.append(product)

    def total_inventory_value(self) -> float:
        return round(sum(p.price for p in self.products), 2)

    def find_by_sku(self, sku: str) -> ProductRecord | None:
        target = sku.strip().upper()
        return next((p for p in self.products if p.sku == target), None)


# =====================================================================
# 4. asdict() — EASY JSON SERIALIZATION
# =====================================================================
def serialize_warehouse(warehouse: Warehouse) -> dict:
    """
    Converts a Warehouse (and all nested ProductRecords) to a plain dict.
    Ready for json.dumps() without any manual mapping.
    """
    return asdict(warehouse)


# =====================================================================
# DEMONSTRATION
# =====================================================================
if __name__ == "__main__":
    # --- 1. ProductRecord with validation ---
    print("=== ProductRecord ===")
    p1 = ProductRecord(name="  Mechanical Keyboard  ", price=85.50, sku="kb-001")
    p2 = ProductRecord(name="Monitor Stand", price=35.00, sku="ms-999")
    print(p1)   # name is stripped, sku is uppercased
    print(p2)
    print("p1 == p1:", p1 == p1)     # True — __eq__ compares by value
    print("p1 == p2:", p1 == p2)     # False

    try:
        ProductRecord(name="Bad Item", price=-5.0, sku="BAD")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # --- 2. Frozen / hashable StockEntry ---
    print("\n=== StockEntry (frozen) ===")
    loc1 = StockEntry(warehouse_id="WH-A", aisle="B", shelf=3)
    loc2 = StockEntry(warehouse_id="WH-A", aisle="B", shelf=3)
    print(loc1.label())
    print("loc1 == loc2:", loc1 == loc2)  # True — same values
    print("hash works:", hash(loc1))       # hashable because frozen

    # Prove immutability
    try:
        loc1.shelf = 99
    except Exception as e:
        print(f"Mutation blocked: {type(e).__name__}: {e}")

    # StockEntry as a set member / dict key
    location_set = {loc1, loc2, StockEntry("WH-B", "C", 7)}
    print("Unique locations:", len(location_set))  # 2, not 3

    # --- 3. Warehouse with field(default_factory=list) ---
    print("\n=== Warehouse ===")
    wh = Warehouse(name="Mumbai DC", location="Andheri East")
    wh.add_product(p1)
    wh.add_product(p2)
    print(wh)
    print("Inventory value: $", wh.total_inventory_value())
    print("Find KB-001:", wh.find_by_sku("kb-001"))

    # Prove isolation between warehouse instances
    wh2 = Warehouse(name="Pune DC", location="Hinjewadi")
    print("wh2 products (should be empty):", wh2.products)

    # --- 4. Serialization ---
    print("\n=== Serialization (asdict) ===")
    import json
    snapshot = serialize_warehouse(wh)
    print(json.dumps(snapshot, indent=2))

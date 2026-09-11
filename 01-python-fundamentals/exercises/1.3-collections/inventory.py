"""
1.3 Collections: Inventory Management System
Demonstrates: Lists, dictionaries, indexing, list comprehensions, dict comprehensions,
sorting with lambda functions, and mutable in-place updates.
"""

def calculate_total_inventory_value(inventory: list) -> float:
    """Calculate the total monetary value of all items in inventory."""
    return round(sum(item["qty"] * item["price"] for item in inventory), 2)


def get_low_stock_items(inventory: list, threshold: int = 10) -> list:
    """Filter items with quantity below threshold using a list comprehension."""
    return [item for item in inventory if item["qty"] < threshold]


def create_price_lookup(inventory: list) -> dict:
    """Build a fast name -> price mapping dictionary using dict comprehension."""
    return {item["name"]: item["price"] for item in inventory}


def restock_item(inventory: list, item_name: str, quantity: int) -> bool:
    """
    Find and restock an item in-place (mutates the underlying dictionary).
    Returns True if updated, False if item was not found.
    """
    if quantity <= 0:
        raise ValueError(f"Restock quantity must be positive, got {quantity}")

    for item in inventory:
        if item["name"].lower() == item_name.strip().lower():
            item["qty"] += quantity
            return True
    return False


def get_top_valued_items(inventory: list, n: int = 3) -> list:
    """Return top N items sorted by total stock value (qty * price) descending."""
    sorted_items = sorted(
        inventory,
        key=lambda x: x["qty"] * x["price"],
        reverse=True
    )
    return sorted_items[:n]  # Slicing the first n items


SAMPLE_INVENTORY = [
    {"name": "Laptop", "qty": 5, "price": 800.0},
    {"name": "Mouse", "qty": 25, "price": 20.0},
    {"name": "Keyboard", "qty": 8, "price": 45.0},
    {"name": "Monitor", "qty": 3, "price": 150.0},
    {"name": "USB Cable", "qty": 50, "price": 5.0}
]

if __name__ == "__main__":
    print("=== Inventory Collections Demo ===")
    total_val = calculate_total_inventory_value(SAMPLE_INVENTORY)
    print(f"Total Portfolio Value: ${total_val:,.2f}")

    low_stock = get_low_stock_items(SAMPLE_INVENTORY, threshold=10)
    print(f"Low stock items (< 10): {[i['name'] for i in low_stock]}")

    lookup = create_price_lookup(SAMPLE_INVENTORY)
    print("Quick Price Lookup:", lookup)

    top_3 = get_top_valued_items(SAMPLE_INVENTORY, n=3)
    print("\nTop 3 Value Items:")
    for item in top_3:
        print(f" - {item['name']}: {item['qty']} units @ ${item['price']} = ${item['qty'] * item['price']:.2f}")

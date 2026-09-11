"""
1.2 Control Flow: Search and Filter Algorithms
Demonstrates: Iteration with for loops, early exit with break, skipping with continue,
linear search algorithms, and multi-condition filtering.
"""

def search_by_name(items: list, target_name: str):
    """
    Search for the first item matching target_name (case-insensitive).
    Uses break to immediately terminate loop upon finding a match.
    """
    cleaned = target_name.strip().lower()
    found = None
    for item in items:
        if item.get("name", "").strip().lower() == cleaned:
            found = item
            break  # Early termination
    return found


def filter_by_category(items: list, target_category: str) -> list:
    """Filter records by exact category name."""
    cleaned = target_category.strip().lower()
    matches = []
    for item in items:
        if item.get("category", "").strip().lower() == cleaned:
            matches.append(item)
    return matches


def filter_by_price_range(items: list, min_price: float, max_price: float) -> list:
    """Filter records within [min_price, max_price], skipping invalid prices."""
    if min_price > max_price:
        raise ValueError(f"min_price ({min_price}) cannot exceed max_price ({max_price})")

    matches = []
    for item in items:
        price = item.get("price")
        # Use continue to skip records without numeric price
        if not isinstance(price, (int, float)):
            continue
        if min_price <= price <= max_price:
            matches.append(item)
    return matches


# Default catalog dataset
CATALOG = [
    {"name": "Wireless Mouse", "category": "Electronics", "price": 25.99},
    {"name": "Mechanical Keyboard", "category": "Electronics", "price": 79.99},
    {"name": "Desk Lamp", "category": "Furniture", "price": 34.50},
    {"name": "Ergonomic Chair", "category": "Furniture", "price": 199.00},
    {"name": "USB-C Hub", "category": "Electronics", "price": 45.00},
    {"name": "Notebook", "category": "Stationery", "price": 4.99},
    {"name": "Gel Pens (Pack of 5)", "category": "Stationery", "price": 8.50}
]

if __name__ == "__main__":
    print("=== Search & Filter Demo ===")
    found_item = search_by_name(CATALOG, "desk lamp")
    print("Search 'desk lamp':", found_item)

    furniture = filter_by_category(CATALOG, "furniture")
    print(f"\nFurniture ({len(furniture)} found):")
    for f in furniture:
        print(f" - {f['name']} (${f['price']})")

    budget = filter_by_price_range(CATALOG, 10.0, 50.0)
    print(f"\nItems between $10 and $50 ({len(budget)} found):")
    for b in budget:
        print(f" - {b['name']} (${b['price']})")

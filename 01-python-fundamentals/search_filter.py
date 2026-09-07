# sample product catalog
products = [
    {"name": "Wireless Mouse", "category": "Electronics", "price": 25.99},
    {"name": "Mechanical Keyboard", "category": "Electronics", "price": 79.99},
    {"name": "Desk Lamp", "category": "Furniture", "price": 34.50},
    {"name": "Ergonomic Chair", "category": "Furniture", "price": 199.00},
    {"name": "USB-C Hub", "category": "Electronics", "price": 45.00},
    {"name": "Notebook", "category": "Stationery", "price": 4.99},
    {"name": "Gel Pens (Pack of 5)", "category": "Stationery", "price": 8.50}
]

# searches for a product by its exact name (case-insensitive)
def search_by_name(items, target_name):
    for item in items:
        if item["name"].lower() == target_name.lower():
            return item
    return None

# filters items by their category
def filter_by_category(items, target_category):
    matched = []
    for item in items:
        if item["category"].lower() == target_category.lower():
            matched.append(item)
    return matched

# filters items within a specified minimum and maximum price range
def filter_by_price_range(items, min_price, max_price):
    matched = []
    for item in items:
        if min_price <= item["price"] <= max_price:
            matched.append(item)
    return matched

if __name__ == "__main__":
    print("=== Product Catalog Search & Filter ===\n")
    
    # 1. Search by exact name
    found = search_by_name(products, "Desk Lamp")
    print("Search 'Desk Lamp':", found)
    
    # 2. Filter by category
    electronics = filter_by_category(products, "Electronics")
    print(f"\nElectronics ({len(electronics)} items):")
    for item in electronics:
        print(f"  - {item['name']}: ${item['price']}")
        
    # 3. Filter by price range
    budget_items = filter_by_price_range(products, 10.0, 50.0)
    print(f"\nItems between $10 and $50 ({len(budget_items)} items):")
    for item in budget_items:
        print(f"  - {item['name']}: ${item['price']}")

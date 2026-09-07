# sample inventory dataset
sample_inventory = [
    {"name": "Laptop", "qty": 5, "price": 800.0},
    {"name": "Mouse", "qty": 25, "price": 20.0},
    {"name": "Keyboard", "qty": 8, "price": 45.0},
    {"name": "Monitor", "qty": 3, "price": 150.0},
    {"name": "USB Cable", "qty": 50, "price": 5.0}
]

# calculates the total monetary value of all inventory items
def get_total_value(items):
    total = 0.0
    for item in items:
        total = total + (item["qty"] * item["price"])
    return total

# filters and returns a list of items that have quantity below the threshold
def get_low_stock_items(items, threshold=10):
    low_stock = []
    for item in items:
        if item["qty"] < threshold:
            low_stock.append(item)
    return low_stock

if __name__ == "__main__":
    print("Total Inventory Value: $", get_total_value(sample_inventory))
    
    threshold = 10
    low_items = get_low_stock_items(sample_inventory, threshold)
    print(f"\nItems with less than {threshold} in stock:")
    for item in low_items:
        print(f"- {item['name']}: {item['qty']} left (${item['price']} each)")

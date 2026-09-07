# sample transaction log
transactions = [
    {"category": "Groceries", "amount": 45.50},
    {"category": "Utilities", "amount": 120.00},
    {"category": "Groceries", "amount": 32.10},
    {"category": "Entertainment", "amount": 15.00},
    {"category": "Utilities", "amount": 65.25},
    {"category": "Groceries", "amount": 88.40}
]

# aggregates total spending grouped by category
def group_totals_by_category(records):
    totals = {}
    for item in records:
        category = item["category"]
        amount = item["amount"]
        
        if category in totals:
            totals[category] = totals[category] + amount
        else:
            totals[category] = amount
            
    return totals

if __name__ == "__main__":
    category_totals = group_totals_by_category(transactions)
    print("Category Breakdown:")
    for cat, total in category_totals.items():
        print(f"- {cat}: ${total:.2f}")

import csv
import json
import os

# Assumption 1: An expense is stored as a dictionary with keys: 'date', 'category', 'amount'.
# Assumption 2: Expected CSV format is 'date,category,amount' (with or without a header row).
# Assumption 3: Amounts must be strictly positive numbers (> 0).

def validate_expense(date, category, amount):
    # validates individual expense fields before adding
    if not date or not str(date).strip():
        raise ValueError("Expense date cannot be empty")
    
    if not category or not str(category).strip():
        raise ValueError("Expense category cannot be empty")
        
    try:
        num_amount = float(amount)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid amount '{amount}': must be a valid number")
        
    if num_amount <= 0:
        raise ValueError(f"Invalid amount '{num_amount}': amount must be greater than zero")
        
    return {
        "date": str(date).strip(),
        "category": str(category).strip().title(),
        "amount": round(num_amount, 2)
    }

def add_expense(expenses_list, date, category, amount):
    # validates and appends an expense to the list, returning the created record
    expense = validate_expense(date, category, amount)
    expenses_list.append(expense)
    return expense

def calculate_category_summary(expenses_list):
    # groups total spending per category into a dictionary
    summary = {}
    for exp in expenses_list:
        cat = exp["category"]
        amt = exp["amount"]
        if cat in summary:
            summary[cat] = summary[cat] + amt
        else:
            summary[cat] = amt
    return {cat: round(total, 2) for cat, total in summary.items()}

def import_expenses_from_csv(filepath):
    # reads expenses from a CSV file, skipping malformed rows
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    imported = []
    skipped_rows = 0
    
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        
        for line_num, row in enumerate(reader, start=1):
            # skip empty lines
            if not row or not any(field.strip() for field in row):
                continue
                
            # skip header if present
            if line_num == 1 and any(h.lower() in ["date", "category", "amount"] for h in row):
                continue
                
            if len(row) != 3:
                print(f"[Warning] Line {line_num}: Expected 3 columns (date, category, amount), got {len(row)}. Skipping.")
                skipped_rows += 1
                continue
                
            raw_date, raw_cat, raw_amt = row
            try:
                valid_item = validate_expense(raw_date, raw_cat, raw_amt)
                imported.append(valid_item)
            except ValueError as err:
                print(f"[Warning] Line {line_num}: {err}. Skipping row.")
                skipped_rows += 1
                
    return imported, skipped_rows

def export_expenses_to_json(expenses_list, filepath):
    # exports the list of expenses into a formatted JSON file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(expenses_list, f, indent=2)

def print_summary(expenses_list):
    # displays a clean console summary of total and category spending
    if not expenses_list:
        print("No expenses recorded yet.")
        return
        
    summary = calculate_category_summary(expenses_list)
    total_spend = sum(exp["amount"] for exp in expenses_list)
    
    print("\n--- Expense Summary ---")
    print(f"Total Transactions: {len(expenses_list)}")
    print(f"Total Amount Spent: ${total_spend:.2f}\n")
    print("Breakdown by Category:")
    for cat, total in summary.items():
        print(f"  - {cat:<15}: ${total:.2f}")
    print("-----------------------\n")

if __name__ == "__main__":
    tracker = []
    
    # manual adds
    add_expense(tracker, "2026-01-05", "Groceries", 45.50)
    add_expense(tracker, "2026-01-06", "Transit", 12.00)
    add_expense(tracker, "2026-01-06", "Groceries", 28.30)
    add_expense(tracker, "2026-01-07", "Books", 25.00)
    
    print_summary(tracker)
    
    # export demo
    output_file = "expenses_export.json"
    export_expenses_to_json(tracker, output_file)
    print(f"Exported {len(tracker)} expenses to {output_file}")

"""
Anti-Pattern Demonstration: Bad Code Example

This module contains a deliberately poorly designed function that violates
clean code and SOLID principles:
- Multiple responsibilities: validation, tax/discount calculation, console output, and disk saving.
- Cryptic and misleading variable names (d, f, x, tot, t, z).
- Hardcoded rules and tight coupling to stdout and local file system.
- Untestable and difficult to extend.
"""

import os
import json


# DELIBERATELY BAD FUNCTION: DO NOT USE IN PRODUCTION
def do_stuff(d, f="orders.txt"):
    # 1. Cryptic validation mixed directly with logic
    if not d or "u" not in d or "items" not in d:
        print("ERROR: bad input")
        return None

    if "@" not in d["u"]:
        print("ERROR: bad email")
        return False

    tot = 0.0
    for x in d["items"]:
        if "p" not in x or x["p"] <= 0:
            print("ERROR: bad item price")
            return None
        q = x.get("q", 1)
        tot += x["p"] * q

    # 2. Hardcoded business logic (discounts & taxes)
    disc = 0.0
    if tot > 100:
        disc = tot * 0.10  # 10% discount for orders > $100

    tax = (tot - disc) * 0.08  # hardcoded 8% tax rate
    final_tot = (tot - disc) + tax

    # 3. Direct console printing side-effect
    print("--------------------------------")
    print("ORDER RECEIPT")
    print("Customer:", d["u"])
    print("Subtotal:", tot)
    print("Discount:", disc)
    print("Tax:", tax)
    print("Total:", final_tot)
    print("--------------------------------")

    # 4. Hardcoded file I/O mixed directly into calculation function
    order_record = {
        "user": d["u"],
        "subtotal": tot,
        "discount": disc,
        "tax": tax,
        "total": final_tot
    }

    with open(f, "a", encoding="utf-8") as file_handle:
        file_handle.write(json.dumps(order_record) + "\n")

    print(f"Saved order to {f}")
    return final_tot


if __name__ == "__main__":
    sample_order = {
        "u": "customer@example.com",
        "items": [
            {"name": "Keyboard", "p": 75.0, "q": 1},
            {"name": "Mouse", "p": 35.0, "q": 1}
        ]
    }
    dummy_file = "test_bad_orders.txt"
    try:
        do_stuff(sample_order, dummy_file)
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

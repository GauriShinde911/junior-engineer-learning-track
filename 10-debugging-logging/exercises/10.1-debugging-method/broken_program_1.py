"""
broken_program_1.py - Invoice and Tax Calculation Service

Problem Description:
The invoice service calculates subtotal, discounts, sales tax, and the final total
for customer orders. In the buggy implementation, tax is computed on the pre-discount
subtotal instead of the net discounted subtotal, leading to customer overcharges.
"""

from typing import List, Dict, Any


def calculate_invoice_buggy(items: List[Dict[str, Any]], discount_percent: float, tax_rate: float) -> Dict[str, float]:
    """
    BUGGY IMPLEMENTATION:
    Calculates invoice totals.
    Bug: Sales tax is calculated on gross subtotal instead of the discounted subtotal.
    """
    gross_subtotal = sum(item["price"] * item["quantity"] for item in items)
    discount_amount = gross_subtotal * (discount_percent / 100.0)
    
    # BUG: Multiplying tax_rate by gross_subtotal ignores the customer's discount!
    tax_amount = gross_subtotal * tax_rate
    
    total = (gross_subtotal - discount_amount) + tax_amount
    return {
        "gross_subtotal": round(gross_subtotal, 2),
        "discount_amount": round(discount_amount, 2),
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2)
    }


def calculate_invoice_fixed(items: List[Dict[str, Any]], discount_percent: float, tax_rate: float) -> Dict[str, float]:
    """
    CORRECTED IMPLEMENTATION:
    Sales tax is applied strictly to the post-discount taxable amount.
    """
    gross_subtotal = sum(item["price"] * item["quantity"] for item in items)
    discount_amount = gross_subtotal * (discount_percent / 100.0)
    net_subtotal = gross_subtotal - discount_amount
    
    # FIX: Tax is correctly assessed on the net subtotal after discount
    tax_amount = net_subtotal * tax_rate
    total = net_subtotal + tax_amount
    
    return {
        "gross_subtotal": round(gross_subtotal, 2),
        "discount_amount": round(discount_amount, 2),
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2)
    }


if __name__ == "__main__":
    sample_items = [
        {"name": "Mechanical Keyboard", "price": 100.0, "quantity": 1},
        {"name": "USB-C Cable", "price": 20.0, "quantity": 2},
    ]
    # $140 subtotal, 20% discount ($28), 10% tax rate
    # Expected net: $112.00, Tax on net: $11.20, Total: $123.20
    # Buggy outputs Tax: $14.00, Total: $126.00
    print("Buggy Output:", calculate_invoice_buggy(sample_items, discount_percent=20.0, tax_rate=0.10))
    print("Fixed Output:", calculate_invoice_fixed(sample_items, discount_percent=20.0, tax_rate=0.10))

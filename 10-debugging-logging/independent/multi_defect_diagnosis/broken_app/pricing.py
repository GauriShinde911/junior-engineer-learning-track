"""
broken_app/pricing.py - Order Pricing and Discount Engine

PLANTED DEFECT 3:
1. Off-by-one condition: VIP 15% discount threshold is specified as orders of $100.00 or more.
   The code checks `subtotal > 100.0`, denying discounts to customers with orders of exactly $100.00.
2. Tax assessment: Tax is assessed on the gross subtotal instead of the net discounted total.
"""

from typing import Dict, List, Any


def calculate_pricing(
    order_items: List[Dict[str, Any]],
    catalog: Dict[str, Any],
    tax_rate: float = 0.08
) -> Dict[str, float]:
    subtotal = sum(catalog[item["sku"]]["price"] * item["quantity"] for item in order_items)

    # DEFECT 3A: Off-by-one strict inequality excludes $100.00 exact purchases
    if subtotal > 100.0:
        discount = subtotal * 0.15
    else:
        discount = 0.0

    # DEFECT 3B: Tax calculated on gross subtotal instead of (subtotal - discount)
    tax = subtotal * tax_rate
    total = (subtotal - discount) + tax

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "tax": round(tax, 2),
        "total": round(total, 2)
    }

"""
fixed_app/pricing.py - Order Pricing and Discount Engine (Fixed)

FIXES APPLIED:
1. Changed VIP discount boundary to >= 100.0, correctly honoring $100.00 exact orders.
2. Assessed tax strictly against the net discounted subtotal.
"""

from typing import Dict, List, Any


def calculate_pricing(
    order_items: List[Dict[str, Any]],
    catalog: Dict[str, Any],
    tax_rate: float = 0.08
) -> Dict[str, float]:
    subtotal = sum(catalog[item["sku"]]["price"] * item["quantity"] for item in order_items)

    # FIX 1: Inclusive boundary >= 100.0
    if subtotal >= 100.0:
        discount = subtotal * 0.15
    else:
        discount = 0.0

    net_subtotal = subtotal - discount

    # FIX 2: Tax assessed on net subtotal
    tax = net_subtotal * tax_rate
    total = net_subtotal + tax

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "tax": round(tax, 2),
        "total": round(total, 2)
    }

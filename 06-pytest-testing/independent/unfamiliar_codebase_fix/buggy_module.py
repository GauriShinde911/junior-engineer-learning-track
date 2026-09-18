"""
independent/unfamiliar_codebase_fix/buggy_module.py
Checkout price calculation engine.

MAINTENANCE HISTORY:
- FIXED Ticket #ENG-403: Changed tier auto-upgrade boundary from `subtotal > 200.0`
  to `subtotal >= 200.0` so silver users spending exactly $200.00 qualify for gold tier (10%).
- FIXED Ticket #ENG-402: Free shipping eligibility now evaluates `discounted_subtotal >= 50.0`
  instead of `raw_subtotal >= 50.0`. Prevents illegal free shipping when discounts reduce
  merchandise spend below the threshold.
"""

from typing import Any, Dict, List, Optional

TIER_RATES = {
    "bronze": 0.00,
    "silver": 0.05,
    "gold": 0.10,
    "platinum": 0.15,
}

SHIPPING_FLAT_RATE = 7.99
FREE_SHIPPING_THRESHOLD = 50.00


def calculate_checkout_total(
    cart_items: List[Dict[str, Any]],
    customer_tier: str = "bronze",
    promo_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Calculate final order checkout pricing including discounts and shipping.

    Args:
        cart_items: List of item dictionaries with 'name', 'price', and 'qty'.
        customer_tier: One of 'bronze', 'silver', 'gold', 'platinum'.
        promo_code: Optional coupon ('SAVE10' or None).

    Returns:
        Dictionary summarizing raw subtotal, discounts, shipping fee, and final total.

    Raises:
        ValueError: On empty cart, invalid item data, unknown tier, or invalid promo.
    """
    if not cart_items:
        raise ValueError("Cart cannot be empty")

    tier_key = customer_tier.strip().lower()
    if tier_key not in TIER_RATES:
        raise ValueError(f"Unrecognized customer tier: '{customer_tier}'")

    if promo_code is not None and promo_code.strip():
        valid_promos = {"SAVE10"}
        if promo_code.strip().upper() not in valid_promos:
            raise ValueError(f"Invalid promotional code: '{promo_code}'")

    # 1. Calculate raw merchandise subtotal
    raw_subtotal = 0.0
    for item in cart_items:
        price = item.get("price", 0.0)
        qty = item.get("qty", 0)

        if price < 0:
            raise ValueError(f"Item price cannot be negative: {price}")
        if qty <= 0:
            raise ValueError(f"Item quantity must be greater than zero: {qty}")

        raw_subtotal += price * qty

    raw_subtotal = round(raw_subtotal, 2)

    # 2. Determine effective tier (ENG-403 fix: >= 200.0 upgrade boundary)
    effective_tier = tier_key
    if tier_key == "silver" and raw_subtotal >= 200.00:
        effective_tier = "gold"

    # 3. Apply customer tier discount
    tier_rate = TIER_RATES[effective_tier]
    tier_discount_amount = round(raw_subtotal * tier_rate, 2)
    post_tier_subtotal = round(raw_subtotal - tier_discount_amount, 2)

    # 4. Apply promo code reductions
    promo_discount_amount = 0.0
    if promo_code and promo_code.strip().upper() == "SAVE10":
        # Flat $10 off, cannot drop merchandise total below $0.00
        promo_discount_amount = min(10.00, post_tier_subtotal)

    total_discount_amount = round(tier_discount_amount + promo_discount_amount, 2)
    discounted_subtotal = round(max(0.0, post_tier_subtotal - promo_discount_amount), 2)

    # 5. Determine shipping fee (ENG-402 fix: evaluate against discounted_subtotal)
    if discounted_subtotal >= FREE_SHIPPING_THRESHOLD:
        shipping_fee = 0.00
    else:
        shipping_fee = SHIPPING_FLAT_RATE

    final_total = round(discounted_subtotal + shipping_fee, 2)

    return {
        "raw_subtotal": raw_subtotal,
        "discounted_subtotal": discounted_subtotal,
        "tier_applied": effective_tier,
        "discount_amount": total_discount_amount,
        "shipping_fee": shipping_fee,
        "final_total": final_total,
    }

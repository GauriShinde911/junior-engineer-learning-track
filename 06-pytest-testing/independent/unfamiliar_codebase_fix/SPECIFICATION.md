# E-Commerce Checkout Engine: Feature & Defect Specification

## System Context
The `checkout` subsystem calculates final order pricing including item subtotals, membership tier discounts, promotional coupon reductions, and shipping fees.

---

## Business Requirements & Rules

### 1. Item Subtotal
- An order contains a list of line item dictionaries: `{"name": str, "price": float, "qty": int}`.
- Subtotal equals the sum of `price * qty` for all items rounded to 2 decimal places.
- Empty cart raises `ValueError("Cart cannot be empty")`.
- Any item with `price < 0` or `qty <= 0` raises `ValueError`.

### 2. Customer Tier Discounts
Discounts apply directly to the item subtotal:
- `"bronze"`: 0% discount
- `"silver"`: 5% discount
- `"gold"`: 10% discount
- `"platinum"`: 15% discount
- Any unrecognized tier raises `ValueError("Unrecognized customer tier")`.

**Tier Auto-Upgrade Rule**:
- A `"silver"` customer whose subtotal is **greater than or equal to $200.00 (`>= 200.00`)** automatically qualifies for the `"gold"` discount rate (10.0%) on that order.

### 3. Promotional Codes
- Optional `promo_code` parameter:
  - `"SAVE10"`: Deducts a flat $10.00 from the post-tier-discounted item total. Cannot reduce item total below $0.00.
  - `None` or empty string: No coupon applied.
  - Any other unrecognized promo code raises `ValueError("Invalid promotional code")`.

### 4. Shipping Fee Calculation
- Flat standard shipping fee: **$7.99**.
- Free shipping threshold: **$50.00**.
- **CRITICAL BUSINESS RULE (The Defect Area)**:
  Free shipping eligibility is evaluated against the **final discounted merchandise subtotal** (after tier and promo discounts), **NOT** the raw pre-discount subtotal.
  - If `discounted_subtotal >= 50.00` -> shipping is **$0.00**.
  - If `discounted_subtotal < 50.00` -> shipping is **$7.99**.

### 5. Final Output Schema
The checkout engine returns a dictionary:
```python
{
    "raw_subtotal": float,       # Sum before discounts
    "discounted_subtotal": float,# Merchandise after tier & promo
    "tier_applied": str,         # Customer tier used (e.g. "gold" if upgraded)
    "discount_amount": float,    # Total savings from tier & promo
    "shipping_fee": float,       # $0.00 or $7.99
    "final_total": float,        # discounted_subtotal + shipping_fee
}
```
All floating-point amounts must be rounded to 2 decimal places.

---

## Original Defect Report
- **Ticket #ENG-402**: Customers whose merchandise totals were discounted below $50 were still granted free shipping because the legacy implementation checked `if raw_subtotal >= 50.0:` instead of `if discounted_subtotal >= 50.0:`.
- **Ticket #ENG-403**: Silver tier customers spending exactly $200.00 did not receive the gold discount because the code checked `subtotal > 200.0` instead of `>= 200.0`.

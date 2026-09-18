"""
independent/unfamiliar_codebase_fix/test_buggy_module.py
Test-first test suite for checkout engine specification and bug regressions.

Pinned behaviors:
1. Specification compliance: line totals, tier discounts, promo reductions, shipping fees.
2. Regression ENG-402: Free shipping must be determined by post-discount subtotal, not raw subtotal.
3. Regression ENG-403: Silver auto-upgrade must trigger at >= $200.00, not strictly > $200.00.
"""

from typing import Any, Dict, List
import pytest

from buggy_module import calculate_checkout_total


# ---------------------------------------------------------------------------
# Test Fixtures & Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def single_item_cart() -> List[Dict[str, Any]]:
    return [{"name": "Developer Handbook", "price": 40.00, "qty": 1}]


# ---------------------------------------------------------------------------
# Specification Tests: Tier Discounts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "tier,expected_rate",
    [
        ("bronze", 0.00),
        ("silver", 0.05),
        ("gold", 0.10),
        ("platinum", 0.15),
    ],
)
def test_standard_tier_discounts(tier: str, expected_rate: float):
    """Verify each customer tier receives its exact percentage reduction."""
    cart = [{"name": "Course Access", "price": 100.00, "qty": 1}]
    result = calculate_checkout_total(cart, customer_tier=tier)

    expected_discount = round(100.00 * expected_rate, 2)
    expected_discounted = round(100.00 - expected_discount, 2)

    assert result["tier_applied"] == tier
    assert result["discount_amount"] == expected_discount
    assert result["discounted_subtotal"] == expected_discounted


# ---------------------------------------------------------------------------
# Regression Test: Ticket ENG-403 (Silver Auto-Upgrade at Exactly $200)
# ---------------------------------------------------------------------------

def test_regression_eng_403_silver_upgrade_at_exact_boundary():
    """REGRESSION #ENG-403: Silver customer spending exactly $200.00 MUST upgrade to gold (10%).

    The original buggy implementation used `if subtotal > 200:` which failed to upgrade
    a purchase of exactly $200.00, giving only 5% discount instead of 10%.
    """
    cart = [{"name": "Software License", "price": 100.00, "qty": 2}]  # exactly $200.00
    result = calculate_checkout_total(cart, customer_tier="silver")

    # Gold tier gives 10% discount ($20.00 off), bringing total to $180.00
    assert result["tier_applied"] == "gold"
    assert result["discount_amount"] == 20.00
    assert result["discounted_subtotal"] == 180.00
    assert result["shipping_fee"] == 0.00  # >= 50 qualifies for free shipping
    assert result["final_total"] == 180.00


def test_silver_below_upgrade_threshold():
    """Verify spending below $200 retains standard silver 5% discount."""
    cart = [{"name": "Monitor Arm", "price": 199.99, "qty": 1}]
    result = calculate_checkout_total(cart, customer_tier="silver")

    assert result["tier_applied"] == "silver"
    assert result["discount_amount"] == round(199.99 * 0.05, 2)


# ---------------------------------------------------------------------------
# Regression Test: Ticket ENG-402 (Shipping Eligibility on Discounted Subtotal)
# ---------------------------------------------------------------------------

def test_regression_eng_402_free_shipping_disallowed_when_discount_drops_under_50():
    """REGRESSION #ENG-402: Free shipping must check discounted subtotal, not raw subtotal.

    Raw items = $52.00 (looks >= $50).
    Platinum 15% discount = -$7.80.
    Discounted merchandise subtotal = $44.20.
    Because $44.20 < $50.00, the customer MUST be charged the $7.99 shipping fee.
    Legacy bug checked `raw_subtotal >= 50.0`, mistakenly granting free shipping.
    """
    cart = [{"name": "Specialty Tool", "price": 52.00, "qty": 1}]
    result = calculate_checkout_total(cart, customer_tier="platinum")

    assert result["raw_subtotal"] == 52.00
    assert result["discount_amount"] == 7.80
    assert result["discounted_subtotal"] == 44.20

    # Must be charged shipping because $44.20 < $50.00
    assert result["shipping_fee"] == 7.99
    assert result["final_total"] == round(44.20 + 7.99, 2)


def test_free_shipping_granted_when_discounted_subtotal_is_at_least_50():
    """Verify free shipping applies when discounted subtotal >= $50.00."""
    cart = [{"name": "Mechanical Keyboard", "price": 60.00, "qty": 1}]
    result = calculate_checkout_total(cart, customer_tier="bronze")

    assert result["discounted_subtotal"] == 60.00
    assert result["shipping_fee"] == 0.00
    assert result["final_total"] == 60.00


def test_free_shipping_exact_fifty_boundary():
    """Verify exactly $50.00 discounted merchandise subtotal qualifies for free shipping."""
    cart = [{"name": "Item", "price": 50.00, "qty": 1}]
    result = calculate_checkout_total(cart, customer_tier="bronze")

    assert result["discounted_subtotal"] == 50.00
    assert result["shipping_fee"] == 0.00
    assert result["final_total"] == 50.00


# ---------------------------------------------------------------------------
# Promo Code "SAVE10" Tests
# ---------------------------------------------------------------------------

def test_promo_code_save10_applied_after_tier_discount():
    """Verify SAVE10 deducts $10 from post-tier subtotal."""
    cart = [{"name": "SSD Drive", "price": 100.00, "qty": 1}]
    # Gold tier 10% -> $90.00. SAVE10 -> $80.00. Shipping is free ($80 >= 50).
    result = calculate_checkout_total(cart, customer_tier="gold", promo_code="SAVE10")

    assert result["raw_subtotal"] == 100.00
    assert result["tier_applied"] == "gold"
    assert result["discount_amount"] == 20.00  # 10 (tier) + 10 (promo)
    assert result["discounted_subtotal"] == 80.00
    assert result["shipping_fee"] == 0.00
    assert result["final_total"] == 80.00


def test_promo_code_save10_floors_at_zero():
    """Verify promo discount cannot drop subtotal below $0.00."""
    cart = [{"name": "Sticker Pack", "price": 6.00, "qty": 1}]
    result = calculate_checkout_total(cart, customer_tier="bronze", promo_code="SAVE10")

    assert result["discounted_subtotal"] == 0.00
    # $0 < $50 -> shipping charged
    assert result["shipping_fee"] == 7.99
    assert result["final_total"] == 7.99


# ---------------------------------------------------------------------------
# Input Validation & Error Handling Tests
# ---------------------------------------------------------------------------

def test_empty_cart_raises_value_error():
    """Verify empty cart is rejected."""
    with pytest.raises(ValueError, match="Cart cannot be empty"):
        calculate_checkout_total([])


def test_invalid_item_price_or_qty_raises_value_error():
    """Verify negative price or zero quantity raise ValueError."""
    with pytest.raises(ValueError, match="Item price cannot be negative"):
        calculate_checkout_total([{"name": "Bad Item", "price": -5.0, "qty": 1}])

    with pytest.raises(ValueError, match="Item quantity must be greater than zero"):
        calculate_checkout_total([{"name": "Bad Item", "price": 10.0, "qty": 0}])


def test_unrecognized_tier_raises_value_error(single_item_cart):
    """Verify invalid customer tier is rejected."""
    with pytest.raises(ValueError, match="Unrecognized customer tier"):
        calculate_checkout_total(single_item_cart, customer_tier="diamond")


def test_unrecognized_promo_code_raises_value_error(single_item_cart):
    """Verify invalid promotional code is rejected."""
    with pytest.raises(ValueError, match="Invalid promotional code"):
        calculate_checkout_total(single_item_cart, promo_code="DISCOUNT50")

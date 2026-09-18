"""
exercises/6.3-fixtures-parametrization/test_parametrized_examples.py
Demonstrating parameterized tests with @pytest.mark.parametrize and fixture consumption.
Collapses redundant test boilerplate into expressive, readable test matrices.
"""

from pathlib import Path
from typing import Any, Dict, List
import pytest

from test_data import (
    calculate_order_subtotal,
    calculate_tax,
    make_order,
    make_order_item,
    make_user,
    transition_order_status,
)


# ---------------------------------------------------------------------------
# Parameterized: State Sales Tax Calculations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "subtotal,state_code,expected_tax",
    [
        (100.0, "CA", 8.25),   # 8.25%
        (100.0, "NY", 8.00),   # 8.00%
        (100.0, "TX", 6.25),   # 6.25%
        (100.0, "WA", 6.50),   # 6.50%
        (100.0, "OR", 0.00),   # 0% tax-free
        (0.0, "CA", 0.00),     # zero subtotal boundary
        (49.99, "TX", 3.12),   # fractional rounding: 49.99 * 0.0625 = 3.124375 -> 3.12
    ],
    ids=["ca-rate", "ny-rate", "tx-rate", "wa-rate", "or-tax-free", "zero-subtotal", "fractional-rounding"],
)
def test_calculate_tax_across_states(subtotal: float, state_code: str, expected_tax: float):
    """Collapses 7 distinct tax scenario checks into a single clean test definition."""
    actual = calculate_tax(subtotal, state_code)
    assert actual == expected_tax


@pytest.mark.parametrize(
    "invalid_state",
    ["ZZ", "FL", "", "12", "USA"],
    ids=["nonexistent-code", "unsupported-state", "empty-string", "numeric", "country-code"],
)
def test_calculate_tax_unsupported_states_raise_error(invalid_state: str):
    """Verify that unsupported state codes trigger ValueError across all variants."""
    with pytest.raises(ValueError, match="Unsupported state tax code"):
        calculate_tax(100.0, invalid_state)


# ---------------------------------------------------------------------------
# Parameterized: State Machine Transitions
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "current_status,action,expected_status",
    [
        ("pending", "pay", "paid"),
        ("pending", "cancel", "cancelled"),
        ("paid", "ship", "shipped"),
        ("paid", "refund", "refunded"),
        ("shipped", "deliver", "delivered"),
    ],
    ids=["pay-pending", "cancel-pending", "ship-paid", "refund-paid", "deliver-shipped"],
)
def test_transition_order_status_valid(current_status: str, action: str, expected_status: str):
    """Verify all legitimate state transitions in the order lifecycle."""
    assert transition_order_status(current_status, action) == expected_status


@pytest.mark.parametrize(
    "current_status,illegal_action",
    [
        ("pending", "deliver"),  # cannot deliver unpaid order
        ("paid", "pay"),         # already paid
        ("cancelled", "pay"),    # cannot pay cancelled order
        ("delivered", "cancel"), # cannot cancel delivered order
    ],
    ids=["deliver-unpaid", "repay-paid", "pay-cancelled", "cancel-delivered"],
)
def test_transition_order_status_illegal(current_status: str, illegal_action: str):
    """Verify illegal transitions are strictly rejected."""
    with pytest.raises(ValueError, match="Illegal transition"):
        transition_order_status(current_status, illegal_action)


# ---------------------------------------------------------------------------
# Factory + Parameterized Integration
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "tier,expected_active",
    [
        ("admin", True),
        ("member", True),
        ("guest", False),
    ],
)
def test_make_user_tier_customization(tier: str, expected_active: bool):
    """Verify factory customization generates valid user models."""
    user = make_user(username=f"{tier}_user", role=tier, is_active=expected_active)
    assert user["role"] == tier
    assert user["is_active"] is expected_active


def test_calculate_order_subtotal_with_factory():
    """Verify calculating subtotal using composite items from factories."""
    item1 = make_order_item("item-1", "Mechanical Keyboard", 89.99, quantity=2)
    item2 = make_order_item("item-2", "USB-C Cable", 9.99, quantity=3)
    order = make_order(order_id=501, user_id=42, items=[item1, item2])

    expected = round((89.99 * 2) + (9.99 * 3), 2)  # 179.98 + 29.97 = 209.95
    assert calculate_order_subtotal(order) == expected


# ---------------------------------------------------------------------------
# Consuming conftest.py Fixtures
# ---------------------------------------------------------------------------

def test_sample_app_config_fixture(sample_app_config: Dict[str, Any]):
    """Verify conftest sample_app_config fixture injection."""
    assert sample_app_config["app_env"] == "testing"
    assert sample_app_config["max_retries"] == 3
    assert sample_app_config["feature_flags"]["enable_rate_limiting"] is True


def test_sample_user_catalog_fixture(sample_user_catalog: List[Dict[str, Any]]):
    """Verify conftest user catalog fixture contains expected accounts."""
    usernames = [u["username"] for u in sample_user_catalog]
    assert "alice_admin" in usernames
    assert len(sample_user_catalog) == 3


def test_temp_log_file_fixture_io(temp_log_file: Path):
    """Verify write operation to isolated filesystem path created by fixture."""
    assert temp_log_file.exists()
    temp_log_file.write_text("AUDIT: User logged in\n", encoding="utf-8")
    content = temp_log_file.read_text(encoding="utf-8")
    assert "AUDIT: User logged in" in content

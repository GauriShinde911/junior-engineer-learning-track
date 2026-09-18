"""
exercises/6.3-fixtures-parametrization/test_data.py
Reusable test data factory functions and domain business logic used in parametrization tests.
"""

from typing import Any, Dict, List, Optional


STATE_TAX_RATES = {
    "CA": 0.0825,
    "NY": 0.0800,
    "TX": 0.0625,
    "WA": 0.0650,
    "OR": 0.0000,  # No sales tax
}


def make_user(
    user_id: int = 1,
    username: str = "default_user",
    role: str = "member",
    is_active: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Factory creating user profile dictionary with sensible defaults."""
    user = {
        "id": user_id,
        "username": username,
        "role": role,
        "is_active": is_active,
    }
    user.update(kwargs)
    return user


def make_order_item(
    item_id: str,
    name: str,
    unit_price: float,
    quantity: int = 1,
) -> Dict[str, Any]:
    """Factory creating a single line item for an order."""
    if unit_price < 0 or quantity <= 0:
        raise ValueError("Price must be non-negative and quantity must be positive")
    return {
        "item_id": item_id,
        "name": name,
        "unit_price": unit_price,
        "quantity": quantity,
    }


def make_order(
    order_id: int = 1001,
    user_id: int = 1,
    items: Optional[List[Dict[str, Any]]] = None,
    status: str = "pending",
) -> Dict[str, Any]:
    """Factory creating an order aggregate with nested items."""
    return {
        "order_id": order_id,
        "user_id": user_id,
        "items": items if items is not None else [],
        "status": status,
    }


def calculate_order_subtotal(order: Dict[str, Any]) -> float:
    """Calculate raw subtotal across all line items in an order."""
    total = sum(item["unit_price"] * item["quantity"] for item in order.get("items", []))
    return round(total, 2)


def calculate_tax(subtotal: float, state_code: str) -> float:
    """Calculate state sales tax for a subtotal.

    Args:
        subtotal: Pre-tax order amount.
        state_code: 2-letter uppercase US state code.

    Returns:
        Tax amount rounded to 2 decimals.

    Raises:
        ValueError: If subtotal is negative or state_code is unrecognized.
    """
    if subtotal < 0:
        raise ValueError("Subtotal cannot be negative")
    code = state_code.strip().upper()
    if code not in STATE_TAX_RATES:
        raise ValueError(f"Unsupported state tax code: {state_code}")

    rate = STATE_TAX_RATES[code]
    return round(subtotal * rate, 2)


def transition_order_status(current_status: str, action: str) -> str:
    """Evaluate valid state machine transitions for an order.

    Valid flows:
    - pending -> [pay -> paid, cancel -> cancelled]
    - paid -> [ship -> shipped, refund -> refunded]
    - shipped -> [deliver -> delivered]
    """
    allowed_transitions = {
        ("pending", "pay"): "paid",
        ("pending", "cancel"): "cancelled",
        ("paid", "ship"): "shipped",
        ("paid", "refund"): "refunded",
        ("shipped", "deliver"): "delivered",
    }
    key = (current_status.lower(), action.lower())
    if key not in allowed_transitions:
        raise ValueError(f"Illegal transition: action '{action}' on status '{current_status}'")
    return allowed_transitions[key]

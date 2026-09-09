"""
Exercise: SOLID-Refactored Order Checkout System

=============================================================================
ANALYSIS OF SOLID PRINCIPLES: VIOLATIONS IN BAD CODE & HOW THIS REFACTOR FIXES THEM
=============================================================================

1. S - Single Responsibility Principle (SRP)
   - VIOLATION IN BAD CODE:
     The function `do_stuff()` was responsible for 4 completely separate concerns:
     (1) input validation, (2) pricing and tax calculation, (3) console receipt printing,
     and (4) file persistence. Any change to any of these reasons required editing the same function.
   - HOW THIS REFACTOR FIXES IT:
     Each concern has its own dedicated class:
     - `OrderValidator`: solely responsible for validating input data.
     - `PricingCalculator`: solely responsible for computing totals, discounts, and taxes.
     - `ReceiptFormatter`: solely responsible for human-readable output formatting.
     - `OrderRepository`: solely responsible for persistence operations.
     - `CheckoutService`: purely coordinates the workflow.

2. O - Open/Closed Principle (OCP)
   - VIOLATION IN BAD CODE:
     Adding a new promotional discount or varying tax rate required modifying the inner
     conditional branches of `do_stuff()`.
   - HOW THIS REFACTOR FIXES IT:
     Discounts are encapsulated via the `DiscountStrategy` interface (Strategy pattern).
     You can add `VipDiscountStrategy` or `PercentageDiscountStrategy` by extending the base class
     without modifying a single line of `PricingCalculator` or `CheckoutService`.

3. L - Liskov Substitution Principle (LSP)
   - VIOLATION IN BAD CODE:
     No abstractions or guarantees existed; callers had to anticipate arbitrary return types
     (None vs False vs float) and side-effects.
   - HOW THIS REFACTOR FIXES IT:
     All implementations of `DiscountStrategy` and `OrderRepository` conform to their base contracts.
     Any concrete repository or discount strategy can substitute for its base type without breaking
     the behavior of `CheckoutService`.

4. I - Interface Segregation Principle (ISP)
   - VIOLATION IN BAD CODE:
     The monolithic function forced every caller to accept disk I/O and console output even if
     they only needed to calculate the price.
   - HOW THIS REFACTOR FIXES IT:
     Interfaces are lean and decoupled: persistence (`OrderRepository`), calculation
     (`DiscountStrategy`), and presentation (`ReceiptFormatter`) are separated. Callers depend
     only on what they need.

5. D - Dependency Inversion Principle (DIP)
   - VIOLATION IN BAD CODE:
     High-level business checkout logic directly instantiated and coupled to low-level file I/O
     (`open(f, 'a')`) and stdout (`print`).
   - HOW THIS REFACTOR FIXES IT:
     High-level module `CheckoutService` depends strictly on abstractions (`OrderRepository`,
     `DiscountStrategy`). Concrete dependencies are injected via constructor (Dependency Injection).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
import os
import tempfile


# =====================================================================
# DOMAIN MODELS & VALUE OBJECTS
# =====================================================================
@dataclass(frozen=True)
class OrderItem:
    name: str
    price: float
    quantity: int = 1

    def subtotal(self) -> float:
        return self.price * self.quantity


@dataclass(frozen=True)
class OrderSummary:
    user_email: str
    items: List[OrderItem]
    subtotal: float
    discount: float
    tax: float
    total: float


# =====================================================================
# 1. VALIDATION LAYER (SRP)
# =====================================================================
class OrderValidator:
    """Validates raw customer and order data."""

    @staticmethod
    def validate(user_email: str, items_data: List[Dict[str, Any]]) -> List[OrderItem]:
        if not user_email or "@" not in user_email:
            raise ValueError(f"Invalid customer email: '{user_email}'")

        if not items_data:
            raise ValueError("Order must contain at least one item.")

        parsed_items: List[OrderItem] = []
        for idx, item in enumerate(items_data):
            name = str(item.get("name", f"Item #{idx+1}")).strip()
            price = float(item.get("price", 0.0))
            quantity = int(item.get("quantity", 1))

            if price <= 0:
                raise ValueError(f"Item '{name}' must have a positive price. Got: {price}")
            if quantity <= 0:
                raise ValueError(f"Item '{name}' must have quantity >= 1. Got: {quantity}")

            parsed_items.append(OrderItem(name=name, price=price, quantity=quantity))

        return parsed_items


# =====================================================================
# 2. DISCOUNT STRATEGY (OCP & LSP)
# =====================================================================
class DiscountStrategy(ABC):
    """Abstract discount policy. Extend this to add new rules without altering core pricing."""

    @abstractmethod
    def calculate_discount(self, subtotal: float) -> float:
        pass


class NoDiscountStrategy(DiscountStrategy):
    """Default: No discount applied."""

    def calculate_discount(self, subtotal: float) -> float:
        return 0.0


class ThresholdDiscountStrategy(DiscountStrategy):
    """Applies a percentage discount if subtotal exceeds a given threshold."""

    def __init__(self, threshold: float = 100.0, discount_percent: float = 0.10):
        self.threshold = threshold
        self.discount_percent = discount_percent

    def calculate_discount(self, subtotal: float) -> float:
        if subtotal > self.threshold:
            return round(subtotal * self.discount_percent, 2)
        return 0.0


# =====================================================================
# 3. PRICING & CALCULATION ENGINE (SRP)
# =====================================================================
class PricingCalculator:
    """Calculates subtotal, discount, and tax based on business rules."""

    def __init__(self, tax_rate: float = 0.08, discount_strategy: Optional[DiscountStrategy] = None):
        self.tax_rate = tax_rate
        self.discount_strategy = discount_strategy or NoDiscountStrategy()

    def calculate(self, user_email: str, items: List[OrderItem]) -> OrderSummary:
        subtotal = round(sum(item.subtotal() for item in items), 2)
        discount = self.discount_strategy.calculate_discount(subtotal)
        taxable_amount = max(0.0, subtotal - discount)
        tax = round(taxable_amount * self.tax_rate, 2)
        total = round(taxable_amount + tax, 2)

        return OrderSummary(
            user_email=user_email,
            items=items,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total
        )


# =====================================================================
# 4. DATA ACCESS REPOSITORY (DIP & LSP)
# =====================================================================
class OrderRepository(ABC):
    """Storage contract. High-level service depends on this, not on file/db details."""

    @abstractmethod
    def save_order(self, order: OrderSummary) -> None:
        pass


class FileOrderRepository(OrderRepository):
    """Concrete file-based persistence."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def save_order(self, order: OrderSummary) -> None:
        record = {
            "user_email": order.user_email,
            "items_count": len(order.items),
            "subtotal": order.subtotal,
            "discount": order.discount,
            "tax": order.tax,
            "total": order.total
        }
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


class InMemoryOrderRepository(OrderRepository):
    """In-memory storage for unit testing without disk I/O."""

    def __init__(self):
        self.records: List[OrderSummary] = []

    def save_order(self, order: OrderSummary) -> None:
        self.records.append(order)


# =====================================================================
# 5. PRESENTATION LAYER (ISP & SRP)
# =====================================================================
class ReceiptFormatter:
    """Generates formatted receipt strings for console, email, or PDF."""

    @staticmethod
    def format_text_receipt(order: OrderSummary) -> str:
        lines = [
            "=" * 40,
            "ORDER RECEIPT",
            f"Customer: {order.user_email}",
            "-" * 40
        ]
        for item in order.items:
            lines.append(f"  {item.name:<20} x{item.quantity}  ${item.subtotal():>7.2f}")
        lines.extend([
            "-" * 40,
            f"Subtotal:              ${order.subtotal:>7.2f}",
            f"Discount:             -${order.discount:>7.2f}",
            f"Tax (8%):              ${order.tax:>7.2f}",
            "=" * 40,
            f"Total Due:             ${order.total:>7.2f}",
            "=" * 40
        ])
        return "\n".join(lines)


# =====================================================================
# 6. HIGH-LEVEL ORCHESTRATION SERVICE (DIP & SRP)
# =====================================================================
class CheckoutService:
    """
    Coordinates checkout workflow using injected abstractions.
    Does not know or care how items are stored or how discounts are calculated.
    """

    def __init__(self, calculator: PricingCalculator, repository: OrderRepository):
        self._calculator = calculator
        self._repository = repository

    def checkout(self, user_email: str, items_data: List[Dict[str, Any]]) -> OrderSummary:
        # Step 1: Validate input
        validated_items = OrderValidator.validate(user_email, items_data)

        # Step 2: Compute pricing & totals
        summary = self._calculator.calculate(user_email, validated_items)

        # Step 3: Persist via repository abstraction
        self._repository.save_order(summary)

        return summary


# =====================================================================
# DEMONSTRATION & VERIFICATION
# =====================================================================
if __name__ == "__main__":
    raw_order_data = [
        {"name": "Mechanical Keyboard", "price": 75.0, "quantity": 1},
        {"name": "Wireless Mouse", "price": 35.0, "quantity": 1}
    ]
    customer_email = "customer@example.com"

    # Setup dependencies
    discount_policy = ThresholdDiscountStrategy(threshold=100.0, discount_percent=0.10)
    pricing_engine = PricingCalculator(tax_rate=0.08, discount_strategy=discount_policy)

    temp_storage = os.path.join(tempfile.gettempdir(), "refactored_orders.jsonl")
    repo = FileOrderRepository(file_path=temp_storage)

    # Initialize service with Dependency Injection
    service = CheckoutService(calculator=pricing_engine, repository=repo)

    try:
        order_summary = service.checkout(customer_email, raw_order_data)
        receipt_text = ReceiptFormatter.format_text_receipt(order_summary)
        print(receipt_text)
        print(f"\n[Verified] Order saved through repository to: {temp_storage}")
    finally:
        if os.path.exists(temp_storage):
            os.remove(temp_storage)

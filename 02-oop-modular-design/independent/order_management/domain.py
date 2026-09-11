"""
Domain Layer: Core Business Entities

This module contains the fundamental business objects for order management.
It contains business rules and validations (e.g. valid pricing, email format)
and is completely decoupled from storage, databases, APIs, or presentation logic.
"""

from typing import List, Optional
import uuid


class Product:
    """
    Represents an item available for purchase with price validation.
    """

    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price  # routes through property setter

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError(f"Price cannot be negative: {value}")
        self._price = round(float(value), 2)

    def __repr__(self) -> str:
        return f"Product(name='{self.name}', price={self._price})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return False
        return self.name == other.name and self.price == other.price


class Customer:
    """
    Represents a customer with email validation.
    """

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email  # routes through property setter

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        cleaned = str(value).strip()
        if "@" not in cleaned or "." not in cleaned:
            raise ValueError(f"Invalid email format: '{value}'")
        self._email = cleaned

    def __repr__(self) -> str:
        return f"Customer(name='{self.name}', email='{self._email}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Customer):
            return False
        return self.name == other.name and self.email == other.email


class Order:
    """
    Represents a placed customer order containing one or more products.
    """

    def __init__(
        self,
        customer: Customer,
        products: Optional[List[Product]] = None,
        order_id: Optional[str] = None,
        status: str = "PENDING"
    ):
        if not isinstance(customer, Customer):
            raise TypeError("Expected customer to be an instance of Customer")

        self.order_id = order_id or f"ORD-{uuid.uuid4().hex[:8].upper()}"
        self.customer = customer
        self.products: List[Product] = []
        self.status = status

        if products:
            for product in products:
                self.add_product(product)

    def add_product(self, product: Product) -> None:
        if not isinstance(product, Product):
            raise TypeError("Expected a Product instance")
        self.products.append(product)

    @property
    def total(self) -> float:
        return round(sum(item.price for item in self.products), 2)

    def __repr__(self) -> str:
        return (
            f"Order(id='{self.order_id}', customer={self.customer.name}, "
            f"items={len(self.products)}, total=${self.total:.2f}, status='{self.status}')"
        )


class Invoice:
    """
    Wraps an order and generates human-readable invoice statements.
    """

    def __init__(self, invoice_id: str, order: Order):
        if not isinstance(order, Order):
            raise TypeError("Expected order to be an instance of Order")
        self.invoice_id = invoice_id
        self.order = order

    def generate_summary(self) -> str:
        lines = [
            "=" * 38,
            f"INVOICE #{self.invoice_id}",
            f"Order ID: {self.order.order_id}",
            f"Customer: {self.order.customer.name} <{self.order.customer.email}>",
            "-" * 38,
            "Items:"
        ]

        for idx, item in enumerate(self.order.products, start=1):
            lines.append(f"  {idx}. {item.name:<22} ${item.price:>7.2f}")

        lines.append("-" * 38)
        lines.append(f"Total Due:               ${self.order.total:>7.2f}")
        lines.append("=" * 38)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Invoice(id='{self.invoice_id}', order_id='{self.order.order_id}', total=${self.order.total:.2f})"

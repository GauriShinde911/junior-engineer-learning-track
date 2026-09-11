"""
Service Layer: Business Workflow Orchestration

This layer coordinates domain objects and the repository.
It executes use-cases such as placing orders, fetching invoices, and
enforcing business constraints (e.g. non-empty order items).
"""

from typing import List, Optional
import uuid

try:
    from .domain import Customer, Product, Order, Invoice
    from .repository import OrderRepository
except ImportError:
    from domain import Customer, Product, Order, Invoice
    from repository import OrderRepository


class OrderService:
    """
    Application service managing the lifecycle of orders.
    Accepts any concrete implementation of OrderRepository via dependency injection.
    """

    def __init__(self, repository: OrderRepository):
        if not isinstance(repository, OrderRepository):
            raise TypeError("repository must be an instance of OrderRepository")
        self._repository = repository

    def create_order(
        self,
        customer: Customer,
        products: List[Product],
        order_id: Optional[str] = None
    ) -> Order:
        """
        Validates business requirements and creates a new persisted order.
        """
        if not products:
            raise ValueError("An order must contain at least one product.")

        if order_id and self._repository.get_by_id(order_id) is not None:
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order = Order(customer=customer, products=products, order_id=order_id, status="CONFIRMED")
        self._repository.save(order)
        return order

    def get_order(self, order_id: str) -> Order:
        """
        Retrieves an order by its ID or raises KeyError if not found.
        """
        order = self._repository.get_by_id(order_id)
        if not order:
            raise KeyError(f"Order '{order_id}' not found.")
        return order

    def create_invoice(self, order_id: str, invoice_id: Optional[str] = None) -> Invoice:
        """
        Generates a commercial invoice for an existing order.
        """
        order = self.get_order(order_id)
        generated_id = invoice_id or f"INV-{uuid.uuid4().hex[:6].upper()}"
        return Invoice(invoice_id=generated_id, order=order)

    def list_customer_orders(self, customer_email: str) -> List[Order]:
        """
        Finds all orders placed by a specific customer email.
        """
        target = customer_email.strip().lower()
        all_orders = self._repository.list_all()
        return [o for o in all_orders if o.customer.email.lower() == target]

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancels an order if it exists.
        """
        order = self.get_order(order_id)
        order.status = "CANCELLED"
        self._repository.save(order)
        return True


if __name__ == "__main__":
    from repository import InMemoryOrderRepository

    repo = InMemoryOrderRepository()
    service = OrderService(repository=repo)

    cust = Customer("Gauri Shinde", "gauri@example.com")
    item1 = Product("Laptop Stand", 35.00)
    item2 = Product("Mechanical Keyboard", 85.50)

    order = service.create_order(cust, [item1, item2], order_id="ORD-DEMO-1")
    invoice = service.create_invoice(order.order_id, invoice_id="INV-9901")

    print(f"Created: {order}")
    print(invoice.generate_summary())

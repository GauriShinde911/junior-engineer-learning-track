"""
Repository Layer: Data Persistence Abstraction

========================================================================================
WHY BUSINESS LOGIC DOES NOT DEPEND ON HOW DATA IS STORED (Modular Architecture & DIP)
========================================================================================
In a well-architected modular system, the Domain and Service layers represent pure
business rules (e.g., "A product cannot have a negative price", "An order must contain
at least one item", "How order totals and invoices are calculated").

The storage mechanism (in-memory dictionary, SQLite, PostgreSQL, MongoDB, or AWS S3)
is merely an *infrastructure detail*.

If the business service directly imported or wrote SQL queries or file operations:
1. Tight Coupling: Changing databases would require rewriting business logic.
2. Inability to Test: Testing business logic would force setting up and tearing down
   real database tables or disk files instead of running fast, isolated unit tests.
3. Violation of Dependency Inversion Principle (DIP): High-level modules (OrderService)
   should not depend on low-level modules (SQL/File I/O). Both should depend on
   abstractions (the `OrderRepository` interface).

By defining `OrderRepository` as an Abstract Base Class (interface):
- `OrderService` talks only to the interface methods (`save`, `get_by_id`, `list_all`, `delete`).
- Concrete implementations (like `InMemoryOrderRepository`, `SqliteOrderRepository`) can be
  swapped via constructor injection at runtime or mocked during testing with zero changes
  to business logic.
========================================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

try:
    from .domain import Order
except ImportError:
    from domain import Order


class OrderRepository(ABC):
    """
    Abstract interface for Order persistence.
    High-level business services depend exclusively on this contract.
    """

    @abstractmethod
    def save(self, order: Order) -> None:
        """Persist or update an order."""
        pass

    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Retrieve an order by its unique ID. Returns None if not found."""
        pass

    @abstractmethod
    def list_all(self) -> List[Order]:
        """List all stored orders."""
        pass

    @abstractmethod
    def delete(self, order_id: str) -> bool:
        """Delete an order by ID. Returns True if deleted, False otherwise."""
        pass


class InMemoryOrderRepository(OrderRepository):
    """
    Concrete in-memory implementation of OrderRepository.
    Ideal for unit testing, prototypes, and local debugging.
    """

    def __init__(self):
        self._storage: Dict[str, Order] = {}

    def save(self, order: Order) -> None:
        if not isinstance(order, Order):
            raise TypeError("Expected an instance of Order")
        self._storage[order.order_id] = order

    def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._storage.get(order_id)

    def list_all(self) -> List[Order]:
        return list(self._storage.values())

    def delete(self, order_id: str) -> bool:
        if order_id in self._storage:
            del self._storage[order_id]
            return True
        return False

"""
Unit Tests for independent/order_management using a MOCK repository.

This demonstrates true unit testing of business logic (OrderService) in isolation:
No real database, disk file, or real in-memory list is used.
A mock repository confirms that OrderService interacts with the OrderRepository
interface exactly as expected.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(MODULE_DIR / "independent"))

from independent.order_management.domain import Product, Customer, Order
from independent.order_management.repository import OrderRepository
from independent.order_management.service import OrderService


# =====================================================================
# Fixtures
# =====================================================================
@pytest.fixture
def mock_repository():
    """Provides a strict mock conforming to the OrderRepository interface."""
    return MagicMock(spec=OrderRepository)


@pytest.fixture
def order_service(mock_repository):
    """Provides an OrderService instance injected with the mock repository."""
    return OrderService(repository=mock_repository)


@pytest.fixture
def sample_customer():
    return Customer("Gauri Shinde", "gauri@example.com")


@pytest.fixture
def sample_products():
    return [
        Product("Webcam 1080p", 49.99),
        Product("Ring Light", 25.00)
    ]


# =====================================================================
# Test Cases Using Mock Repository
# =====================================================================
class TestOrderServiceWithMockRepository:

    def test_service_initialization_requires_order_repository(self):
        with pytest.raises(TypeError, match="repository must be an instance of OrderRepository"):
            OrderService(repository="not_a_repository")

    def test_create_order_calls_repository_save(self, order_service, mock_repository, sample_customer, sample_products):
        mock_repository.get_by_id.return_value = None

        order = order_service.create_order(
            customer=sample_customer,
            products=sample_products,
            order_id="ORD-TEST-100"
        )

        assert order.order_id == "ORD-TEST-100"
        assert order.customer == sample_customer
        assert len(order.products) == 2
        assert order.total == 74.99
        assert order.status == "CONFIRMED"

        # Verify mock repository was called with the order object
        mock_repository.save.assert_called_once_with(order)

    def test_create_order_empty_products_raises_error_and_does_not_save(self, order_service, mock_repository, sample_customer):
        with pytest.raises(ValueError, match="An order must contain at least one product"):
            order_service.create_order(customer=sample_customer, products=[])

        # Confirm repository.save was NEVER called
        mock_repository.save.assert_not_called()

    def test_create_order_duplicate_id_raises_error(self, order_service, mock_repository, sample_customer, sample_products):
        # Simulate that the mock repo already has this order
        mock_repository.get_by_id.return_value = Order(sample_customer, sample_products, order_id="ORD-DUP")

        with pytest.raises(ValueError, match="Order with ID 'ORD-DUP' already exists"):
            order_service.create_order(sample_customer, sample_products, order_id="ORD-DUP")

        mock_repository.save.assert_not_called()

    def test_get_order_success(self, order_service, mock_repository, sample_customer, sample_products):
        fake_order = Order(sample_customer, sample_products, order_id="ORD-FOUND")
        mock_repository.get_by_id.return_value = fake_order

        retrieved = order_service.get_order("ORD-FOUND")

        mock_repository.get_by_id.assert_called_once_with("ORD-FOUND")
        assert retrieved == fake_order

    def test_get_order_not_found_raises_key_error(self, order_service, mock_repository):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(KeyError, match="Order 'ORD-MISSING' not found"):
            order_service.get_order("ORD-MISSING")

        mock_repository.get_by_id.assert_called_once_with("ORD-MISSING")

    def test_create_invoice_retrieves_order_and_formats(self, order_service, mock_repository, sample_customer, sample_products):
        fake_order = Order(sample_customer, sample_products, order_id="ORD-INV")
        mock_repository.get_by_id.return_value = fake_order

        invoice = order_service.create_invoice("ORD-INV", invoice_id="INV-999")

        assert invoice.invoice_id == "INV-999"
        assert invoice.order == fake_order
        summary = invoice.generate_summary()
        assert "INVOICE #INV-999" in summary
        assert "Webcam 1080p" in summary
        mock_repository.get_by_id.assert_called_once_with("ORD-INV")

    def test_list_customer_orders_filters_correctly(self, order_service, mock_repository):
        cust_a = Customer("Alice", "alice@example.com")
        cust_b = Customer("Bob", "bob@example.com")
        order1 = Order(cust_a, [Product("Item 1", 10.0)], order_id="ORD-1")
        order2 = Order(cust_b, [Product("Item 2", 20.0)], order_id="ORD-2")
        order3 = Order(cust_a, [Product("Item 3", 30.0)], order_id="ORD-3")

        # Mock repository returns all orders
        mock_repository.list_all.return_value = [order1, order2, order3]

        alice_orders = order_service.list_customer_orders("alice@example.com")

        mock_repository.list_all.assert_called_once()
        assert len(alice_orders) == 2
        assert [o.order_id for o in alice_orders] == ["ORD-1", "ORD-3"]

    def test_cancel_order_updates_status_and_saves(self, order_service, mock_repository, sample_customer, sample_products):
        fake_order = Order(sample_customer, sample_products, order_id="ORD-CANCEL", status="CONFIRMED")
        mock_repository.get_by_id.return_value = fake_order

        result = order_service.cancel_order("ORD-CANCEL")

        assert result is True
        assert fake_order.status == "CANCELLED"
        mock_repository.save.assert_called_once_with(fake_order)

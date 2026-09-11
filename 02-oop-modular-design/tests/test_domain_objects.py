"""
Unit Tests for exercises/2.1-classes-encapsulation/domain_objects.py
"""

import sys
from pathlib import Path
import pytest

# Ensure the 2.1 subsection folder is on the Python path
TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "2.1-classes-encapsulation"
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(SUBSECTION_DIR))

from domain_objects import Product, Customer, Order, Invoice


# =====================================================================
# Product Tests
# =====================================================================
class TestProduct:
    def test_valid_product_creation(self):
        prod = Product("Wireless Mouse", 29.99)
        assert prod.name == "Wireless Mouse"
        assert prod.price == 29.99

    def test_product_price_rounding(self):
        prod = Product("Coffee Beans", 14.994)
        assert prod.price == 14.99
        prod2 = Product("Tea Leaves", 14.996)
        assert prod2.price == 15.00

    def test_product_negative_price_raises_error(self):
        with pytest.raises(ValueError, match="Price cannot be negative"):
            Product("Defective Item", -5.00)

    def test_product_price_setter_negative_raises_error(self):
        prod = Product("Desk Lamp", 40.0)
        with pytest.raises(ValueError, match="Price cannot be negative"):
            prod.price = -1.0

    def test_product_repr(self):
        prod = Product("Monitor", 199.50)
        assert repr(prod) == "Product(name='Monitor', price=199.5)"


# =====================================================================
# Customer Tests
# =====================================================================
class TestCustomer:
    def test_valid_customer_creation(self):
        cust = Customer("Alice Smith", "alice@example.com")
        assert cust.name == "Alice Smith"
        assert cust.email == "alice@example.com"

    def test_customer_email_stripping(self):
        cust = Customer("Bob Jones", "  bob@test.org  ")
        assert cust.email == "bob@test.org"

    def test_customer_email_missing_at_raises_error(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            Customer("Charlie", "charlietest.com")

    def test_customer_email_missing_dot_raises_error(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            Customer("Dave", "dave@testcom")

    def test_customer_repr(self):
        cust = Customer("Eve", "eve@secure.io")
        assert repr(cust) == "Customer(name='Eve', email='eve@secure.io')"


# =====================================================================
# Order Tests
# =====================================================================
class TestOrder:
    def test_order_creation_default_empty_products(self):
        cust = Customer("Gauri", "gauri@example.com")
        order = Order(cust)
        assert order.customer == cust
        assert order.products == []
        assert order.total == 0.0

    def test_order_total_calculation(self):
        cust = Customer("Gauri", "gauri@example.com")
        p1 = Product("Notebook", 4.50)
        p2 = Product("Pen", 1.75)
        order = Order(cust, [p1, p2])
        assert order.total == 6.25

    def test_order_add_product(self):
        cust = Customer("Gauri", "gauri@example.com")
        order = Order(cust)
        p1 = Product("Backpack", 45.00)
        order.add_product(p1)
        assert len(order.products) == 1
        assert order.total == 45.00

    def test_order_add_invalid_product_raises_type_error(self):
        cust = Customer("Gauri", "gauri@example.com")
        order = Order(cust)
        with pytest.raises(TypeError, match="Expected a Product instance"):
            order.add_product("Not a product")

    def test_order_repr(self):
        cust = Customer("Gauri", "gauri@example.com")
        p1 = Product("Mouse", 25.00)
        order = Order(cust, [p1])
        assert "Order(customer=Gauri, items=1, total=$25.00)" == repr(order)


# =====================================================================
# Invoice Tests
# =====================================================================
class TestInvoice:
    def test_invoice_generation_summary(self):
        cust = Customer("Gauri Shinde", "gauri@example.com")
        p1 = Product("Keyboard", 80.00)
        p2 = Product("Mousepad", 15.50)
        order = Order(cust, [p1, p2])

        invoice = Invoice("INV-2026", order)
        summary = invoice.generate_summary()

        assert "INVOICE #INV-2026" in summary
        assert "Gauri Shinde <gauri@example.com>" in summary
        assert "Keyboard" in summary
        assert "$  80.00" in summary
        assert "Mousepad" in summary
        assert "$  15.50" in summary
        assert "Total Due:               $  95.50" in summary

    def test_invoice_repr(self):
        cust = Customer("Gauri", "gauri@example.com")
        order = Order(cust, [Product("Item", 10.00)])
        invoice = Invoice("INV-001", order)
        assert repr(invoice) == "Invoice(id='INV-001', total=$10.00)"

# represents an individual product with price validation
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price  # triggers property setter validation

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError(f"Price cannot be negative: {value}")
        self._price = round(float(value), 2)

    def __repr__(self):
        return f"Product(name='{self.name}', price={self._price})"


# represents a customer with email validation
class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email  # triggers property setter validation

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        cleaned = str(value).strip()
        if "@" not in cleaned or "." not in cleaned:
            raise ValueError(f"Invalid email address: '{value}'")
        self._email = cleaned

    def __repr__(self):
        return f"Customer(name='{self.name}', email='{self._email}')"


# holds a customer and a collection of products
class Order:
    def __init__(self, customer, products=None):
        self.customer = customer
        self.products = products if products is not None else []

    def add_product(self, product):
        if not isinstance(product, Product):
            raise TypeError("Expected a Product instance")
        self.products.append(product)

    @property
    def total(self):
        return round(sum(p.price for p in self.products), 2)

    def __repr__(self):
        return f"Order(customer={self.customer.name}, items_count={len(self.products)}, total=${self.total:.2f})"


# wraps an order and produces formatted invoice summaries
class Invoice:
    def __init__(self, invoice_id, order):
        self.invoice_id = invoice_id
        self.order = order

    def generate_summary(self):
        lines = [
            "=" * 38,
            f"INVOICE: #{self.invoice_id}",
            f"Customer: {self.order.customer.name} ({self.order.customer.email})",
            "-" * 38,
            "Items Ordered:"
        ]
        
        for idx, item in enumerate(self.order.products, start=1):
            lines.append(f"  {idx}. {item.name:<22} ${item.price:>7.2f}")
            
        lines.append("-" * 38)
        lines.append(f"Total Amount Due:        ${self.order.total:>7.2f}")
        lines.append("=" * 38)
        return "\n".join(lines)

    def __repr__(self):
        return f"Invoice(id='{self.invoice_id}', total=${self.order.total:.2f})"


if __name__ == "__main__":
    print("--- Domain Models Demo ---\n")
    
    # 1. Create customer & products
    cust = Customer("Gauri Shinde", "gauri@example.com")
    laptop = Product("ThinkPad Laptop", 899.99)
    mouse = Product("Wireless Mouse", 29.50)
    usb_hub = Product("USB-C Hub", 45.00)
    
    print("Created Customer:", cust)
    print("Created Products:", [laptop, mouse, usb_hub])
    
    # 2. Build an order
    order = Order(cust, [laptop, mouse])
    order.add_product(usb_hub)
    print("\nCreated Order:", order)
    print(f"Order Total: ${order.total:.2f}")
    
    # 3. Generate invoice
    invoice = Invoice("INV-2026-001", order)
    print("\n" + invoice.generate_summary())
    
    # 4. Demonstrate validation checks
    print("\n--- Validation Error Tests ---")
    try:
        invalid_product = Product("Broken Price", -15.00)
    except ValueError as e:
        print("Caught expected negative price error:", e)
        
    try:
        invalid_cust = Customer("Bad Email", "invalid-email-string")
    except ValueError as e:
        print("Caught expected bad email error:", e)

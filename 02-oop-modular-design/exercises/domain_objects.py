# represents an individual product with non-negative price validation
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price  # routes through property setter

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


# represents a customer with email format validation
class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email  # routes through property setter

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        cleaned = str(value).strip()
        if "@" not in cleaned or "." not in cleaned:
            raise ValueError(f"Invalid email format: '{value}'")
        self._email = cleaned

    def __repr__(self):
        return f"Customer(name='{self.name}', email='{self._email}')"


# holds a customer and an itemized list of Product instances
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
        return round(sum(item.price for item in self.products), 2)

    def __repr__(self):
        return f"Order(customer={self.customer.name}, items={len(self.products)}, total=${self.total:.2f})"


# wraps an order and produces a clean text invoice summary
class Invoice:
    def __init__(self, invoice_id, order):
        self.invoice_id = invoice_id
        self.order = order

    def generate_summary(self):
        lines = [
            "=" * 38,
            f"INVOICE #{self.invoice_id}",
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

    def __repr__(self):
        return f"Invoice(id='{self.invoice_id}', total=${self.order.total:.2f})"


if __name__ == "__main__":
    cust = Customer("Gauri Shinde", "gauri@example.com")
    item1 = Product("Laptop Stand", 35.00)
    item2 = Product("Mechanical Keyboard", 85.50)
    
    order = Order(cust, [item1, item2])
    invoice = Invoice("INV-1001", order)
    
    print(invoice.generate_summary())

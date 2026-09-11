# Order Management Service (Modular Architecture)

A decoupled, layered mini-service built in Python demonstrating **Modular Architecture (5.5)** applied to e-commerce domain objects (`Product`, `Customer`, `Order`, and `Invoice`).

---

## The 3-Layer Split: Domain vs. Service vs. Repository

When building production-ready applications, mixing business logic with database queries or console formatting makes code hard to test, fragile, and rigid.

We split this project into 3 distinct layers:

```
order_management/
├── domain.py         <- Core business models & validation rules
├── repository.py     <- Abstract storage interface + InMemory adapter
├── service.py        <- Workflow coordination (use cases)
└── README.md         <- Plain-language guide
```

### 1. The Domain Layer (`domain.py`) — *The Nouns & Invariants*
- **What it is:** Defines the core entities of your business: `Product`, `Customer`, `Order`, and `Invoice`.
- **What it does:** Enforces rules that must **always** be true, regardless of where or how the data is stored:
  - A product price can never be negative.
  - A customer email must have valid `@` and `.` characters.
  - An invoice summary formats prices to two decimal places.
- **Key rule:** The domain layer has **zero dependencies** on external libraries, databases, or frameworks.

### 2. The Repository Layer (`repository.py`) — *The Storage Contract*
- **What it is:** The bridge between memory and persistence.
- **What it does:**
  - `OrderRepository` (Abstract Base Class) declares **what** storage operations must exist (`save`, `get_by_id`, `list_all`, `delete`).
  - `InMemoryOrderRepository` is one concrete implementation that stores orders in a Python dictionary.
- **Key rule:** Storage is an *infrastructure detail*. The rest of your application only talks to the abstract `OrderRepository` contract, not concrete database drivers.

### 3. The Service Layer (`service.py`) — *The Verbs & Workflows*
- **What it is:** The orchestrator that executes user stories and business workflows.
- **What it does:**
  - `OrderService` coordinates domain objects and the repository:
    - Creating an order (validating at least one product is included).
    - Preventing duplicate order IDs.
    - Creating invoices from stored orders.
    - Querying orders by customer email.
- **Key rule:** `OrderService` receives an `OrderRepository` through **dependency injection** in its constructor. It has no idea whether records are saved to memory, a local SQLite file, or a cloud PostgreSQL instance.

---

## Why Business Logic Doesn't Depend on Storage

1. **Testability with Mocks:** In unit tests (`tests/test_order_management.py`), we can pass a fake/mock repository to `OrderService`. Tests run in milliseconds with zero disk I/O or test database setup.
2. **Swap-ability:** When switching from an in-memory test dictionary to PostgreSQL, AWS DynamoDB, or MongoDB, you only write a new repository class. You **never touch `service.py` or `domain.py`**.
3. **Single Responsibility:** Developers working on business validation don't have to think about SQL connection pooling or database schemas, and vice-versa.

---

## Quick Demo

```python
from order_management.domain import Customer, Product
from order_management.repository import InMemoryOrderRepository
from order_management.service import OrderService

# 1. Wire dependencies
repo = InMemoryOrderRepository()
service = OrderService(repository=repo)

# 2. Use business service
customer = Customer("Gauri Shinde", "gauri@example.com")
products = [Product("Keyboard", 89.99), Product("Mouse", 29.99)]

order = service.create_order(customer, products)
invoice = service.create_invoice(order.order_id)

print(invoice.generate_summary())
```

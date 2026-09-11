# 2.3 Abstract Classes & Interfaces

An **abstract class** (via `abc.ABC`) defines a *contract* — a guaranteed set of methods that every concrete subclass must implement. It cannot be instantiated directly. Python's `abc` module provides this mechanism since Python has no separate `interface` keyword.

---

## Core Concepts

### Defining an abstract class
```python
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def save(self, record: dict) -> None: ...

    @abstractmethod
    def find_by_id(self, id: str) -> dict | None: ...
```
Any class that inherits `Repository` **must** implement `save` and `find_by_id`, or Python raises `TypeError` at instantiation.

### Why depend on the interface, not the implementation?
The business logic layer (a `Service` class) receives a `Repository` object via its constructor. It calls only methods declared on the ABC — it has zero knowledge of whether data lives in RAM, a JSON file, PostgreSQL, or a remote API.

```python
class ProductService:
    def __init__(self, repo: Repository):
        self._repo = repo   # only ABC methods used below

    def add_product(self, product: dict) -> None:
        self._repo.save(product)
```

This is the **Dependency Inversion Principle** (DIP) from SOLID: high-level modules should not depend on low-level modules; both should depend on abstractions.

### Two concrete implementations, same interface
```python
class InMemoryRepository(Repository): ...    # dict, fast, ideal for tests
class JsonFileRepository(Repository):  ...   # JSON file, persistent
```
Swapping between them requires no change to `ProductService`.

---

## Abstract vs Regular Base Class

| | `abc.ABC` | Plain base class |
|---|---|---|
| Can be instantiated | ❌ No | ✅ Yes |
| Enforces method override | ✅ Yes (TypeError) | ❌ No (silent) |
| Communicates intent | ✅ Explicit contract | ⚠️ Implicit |

---

## Files in this subsection

| File | Purpose |
|---|---|
| `interfaces_practice.py` | `UserRepository` ABC with `InMemoryUserRepository` and `JsonFileUserRepository` implementations; `UserService` depends only on the ABC — swapping storage needs zero service changes |

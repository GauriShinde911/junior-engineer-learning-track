# 2.1 Classes & Encapsulation

Python classes bundle state (attributes) and behaviour (methods) into a single reusable unit. Encapsulation means the internal data of an object is protected from arbitrary external mutation — the class controls how it is read or changed.

---

## Core Concepts

### `__init__` and instance attributes
`__init__` runs once when an object is created. Every attribute defined with `self.x = …` is *instance-scoped* — each object gets its own copy.

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price   # delegates to property setter below
```

### Properties — controlled attribute access
A `@property` getter + `@<attr>.setter` pair lets you expose an attribute that *looks* plain but runs validation on write.

```python
@property
def price(self):
    return self._price

@price.setter
def price(self, value):
    if value < 0:
        raise ValueError("Price cannot be negative")
    self._price = round(float(value), 2)
```
The leading underscore (`_price`) is a *convention* that signals "don't touch this directly".

### `__repr__` and `__str__`
- `__repr__` → unambiguous developer-facing string; shown in REPL and `repr()`.
- `__str__` → human-readable string; used by `print()` and `str()`.
- If only `__repr__` is defined, `str()` falls back to it.

### Object composition
Complex domain objects are built by **composing** simpler ones — `Order` holds a `Customer` reference and a list of `Product` instances. This keeps each class focused on a single concern.

---

## Key Rules to Remember

| Rule | Why it matters |
|---|---|
| Prefix internal state with `_` | Signals the field is managed by the class, not callers |
| Always validate in the setter, not the getter | Validation runs exactly once, on write |
| Keep `__init__` thin | Heavy logic in constructors makes testing harder |
| Use `isinstance()` guards on composed objects | Catch type errors at the boundary, not deep inside logic |

---

## File in this subsection

| File | Purpose |
|---|---|
| `domain_objects.py` | Four domain classes (`Product`, `Customer`, `Order`, `Invoice`) demonstrating encapsulation via properties and composition |

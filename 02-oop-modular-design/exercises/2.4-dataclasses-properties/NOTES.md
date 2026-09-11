# 2.4 Dataclasses & Properties

`dataclasses` (Python 3.7+) eliminate most of the boilerplate in plain classes — `__init__`, `__repr__`, and `__eq__` are auto-generated from the field declarations. Properties add controlled attribute access on top of that.

---

## Core Concepts

### Basic `@dataclass`
```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float

p = Point(1.0, 2.5)
print(p)        # Point(x=1.0, y=2.5)   ← __repr__ generated
print(p == Point(1.0, 2.5))  # True     ← __eq__ generated
```

### Field defaults and `field()`
```python
@dataclass
class Inventory:
    product_name: str
    quantity: int = 0
    tags: list = field(default_factory=list)  # mutable default — always use field()
```
Never use `tags: list = []` as a class-level default — all instances would share the same list object.

### `frozen=True` — immutable dataclasses
```python
@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float
```
Attempting to mutate a frozen instance raises `FrozenInstanceError`. Frozen dataclasses are hashable and safe to use as dict keys or in sets.

### `__post_init__` — validation after auto-init
```python
@dataclass
class ProductRecord:
    name: str
    price: float

    def __post_init__(self):
        if self.price < 0:
            raise ValueError(f"Price must be non-negative, got {self.price}")
        self.name = self.name.strip()
```
`__post_init__` runs automatically at the end of the generated `__init__`.

### `@dataclass` + `@property` together
When you need computed attributes or property setters on a dataclass, use `field(init=False)` for internal backing storage:

```python
@dataclass
class Circle:
    _radius: float = field(repr=False)
    area: float = field(init=False, repr=False)

    def __post_init__(self):
        self.area = 3.14159 * self._radius ** 2
```

### `dataclasses.asdict()` and `astuple()`
```python
from dataclasses import asdict
record = asdict(some_dataclass_instance)  # → plain dict, ready for JSON serialization
```

---

## Dataclass vs Plain Class

| | `@dataclass` | Plain class |
|---|---|---|
| `__init__` | Auto-generated | Manual |
| `__repr__` | Auto-generated | Manual |
| `__eq__` | Auto-generated (by value) | Identity by default |
| Immutability | `frozen=True` | Manual `__setattr__` override |
| Best for | Data containers, DTOs | Stateful objects with complex behaviour |

---

## Files in this subsection

| File | Purpose |
|---|---|
| `dataclasses_practice.py` | `ProductRecord` with `__post_init__` validation, `StockEntry` (frozen + hashable), `Warehouse` inventory manager using `field(default_factory=list)`, and `asdict()` serialization |

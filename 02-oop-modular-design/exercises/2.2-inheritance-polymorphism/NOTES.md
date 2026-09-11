# 2.2 Inheritance & Polymorphism

Inheritance lets a child class *reuse and extend* a parent class. Polymorphism means different child classes can be treated identically through a shared interface — the caller doesn't need to know which concrete type it holds.

---

## Core Concepts

### Single inheritance
```python
class Animal:
    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"
```
`Dog` inherits everything from `Animal` and overrides `speak`.

### `super()` — calling parent logic
Use `super().__init__(…)` to invoke the parent constructor before adding child-specific setup.

```python
class ElectricCar(Car):
    def __init__(self, make, model, battery_kwh):
        super().__init__(make, model)   # Car.__init__ runs first
        self.battery_kwh = battery_kwh
```

### Polymorphism in practice
```python
animals: list[Animal] = [Dog(), Cat(), Parrot()]
for a in animals:
    print(a.speak())   # each calls its own implementation
```
The loop doesn't care about the concrete type — it only knows `Animal.speak()` exists.

### Method Resolution Order (MRO)
Python resolves method calls left-to-right through the inheritance chain. Inspect it with `ClassName.__mro__`.

### When to use inheritance (IS-A rule)
Use inheritance only when the relationship is genuinely "X **is a** Y" — not just "X uses some of Y's code". For code reuse without an IS-A relationship, prefer composition (see 2.3).

---

## When NOT to Use Inheritance

| Smell | Better alternative |
|---|---|
| Subclass overrides almost everything | Composition + interface |
| You're inheriting to reuse a helper method | Extract a utility function |
| You need multiple independent behaviours | Mixins or composition |

---

## Files in this subsection

| File | Purpose |
|---|---|
| `inheritance_composition.py` | Abstract `Notifier` ABC with `EmailNotifier` / `SmsNotifier` subclasses; `OrderService` uses composition to accept any `Notifier` — explains why composition beats inheritance for swappable strategies |
| `polymorphism_demo.py` | Vehicle hierarchy (`Vehicle → Car, Truck, Motorcycle`) with a `describe_fleet()` function that works polymorphically on any mix |

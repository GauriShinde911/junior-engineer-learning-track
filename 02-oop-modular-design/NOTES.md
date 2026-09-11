# 02. OOP & Modular Design — Module Overview & Index

Object-oriented programming turns data and behaviour into cohesive, reusable units. This module covers the full arc: defining classes with encapsulation, building hierarchies with inheritance, formalising contracts with abstract classes, eliminating boilerplate with dataclasses, applying the SOLID design principles, and finally composing independent modules into a layered architecture.

---

## Curriculum Index & Subsection Overviews

1. [**2.1 Classes & Encapsulation**](exercises/2.1-classes-encapsulation/NOTES.md)
   `__init__`, `@property` getters/setters, `__repr__`, and domain object composition. The `_private` convention and why validation belongs in the setter.

2. [**2.2 Inheritance & Polymorphism**](exercises/2.2-inheritance-polymorphism/NOTES.md)
   Single inheritance, `super().__init__()`, the IS-A rule, method resolution order (MRO), and polymorphic dispatch — same function, different runtime behaviour per subtype.

3. [**2.3 Abstract Classes & Interfaces**](exercises/2.3-abstract-interfaces/NOTES.md)
   `abc.ABC` and `@abstractmethod` as Python's interface mechanism. The Dependency Inversion Principle: services depend on ABCs, never on concrete implementations.

4. [**2.4 Dataclasses & Properties**](exercises/2.4-dataclasses-properties/NOTES.md)
   `@dataclass` auto-generating `__init__`, `__repr__`, and `__eq__`. `__post_init__` for validation, `frozen=True` for immutability, `field(default_factory=…)` to avoid mutable-default bugs, and `asdict()` for serialization.

5. [**2.5 SOLID Principles**](exercises/2.5-solid-principles/NOTES.md)
   The five principles (SRP, OCP, LSP, ISP, DIP) with a deliberately bad function as the anti-pattern and a fully refactored version mapping each violation to its fix.

6. [**2.6 Modular Architecture**](exercises/2.6-modular-architecture/NOTES.md)
   The Domain → Service → Repository three-layer pattern. Business logic is isolated from storage so that swapping a database backend requires zero changes to the service or domain layers.

- [**Independent Project: Order Management Service**](independent/order_management/README.md)
  A multi-file mini-service (`domain.py`, `service.py`, `repository.py`) applying the modular architecture to a real order-processing workflow.

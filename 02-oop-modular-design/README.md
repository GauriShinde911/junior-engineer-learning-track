# 02. OOP & Modular Design

## Overview
Object-oriented programming in Python: classes, encapsulation, inheritance, polymorphism, abstract base classes, dataclasses, SOLID principles, and layered modular architecture.

---

## Folder Structure

```
02-oop-modular-design/
├── exercises/
│   ├── 2.1-classes-encapsulation/
│   │   ├── domain_objects.py
│   │   └── NOTES.md
│   ├── 2.2-inheritance-polymorphism/
│   │   ├── inheritance_composition.py
│   │   ├── polymorphism_demo.py
│   │   └── NOTES.md
│   ├── 2.3-abstract-interfaces/
│   │   ├── interfaces_practice.py
│   │   └── NOTES.md
│   ├── 2.4-dataclasses-properties/
│   │   ├── dataclasses_practice.py
│   │   └── NOTES.md
│   ├── 2.5-solid-principles/
│   │   ├── bad_code_example.py
│   │   ├── refactored_example.py
│   │   └── NOTES.md
│   └── 2.6-modular-architecture/
│       ├── modular_demo.py
│       └── NOTES.md
├── independent/
│   └── order_management/     ← Mini order-management service
│       ├── domain.py
│       ├── service.py
│       ├── repository.py
│       ├── __init__.py
│       └── README.md
├── tests/
│   ├── test_domain_objects.py
│   └── test_order_management.py
├── NOTES.md                   ← Skill-level overview & subsection index
└── README.md
```

---

## Instructions

1. **Read `NOTES.md`** at the skill level for a full subsection overview.
2. **Guided Exercises (`exercises/`)**: Work through subsections 2.1–2.6 in order; each has its own `NOTES.md` explaining the concepts.
3. **Independent Challenge (`independent/order_management/`)**: Build on the concepts without step-by-step guidance.
4. **Testing (`tests/`)**: Run pytest to validate all solutions.

```bash
# Run all tests for this skill
pytest 02-oop-modular-design/tests/

# Run a specific subsection exercise
python 02-oop-modular-design/exercises/2.1-classes-encapsulation/domain_objects.py
```

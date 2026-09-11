# 2.5 SOLID Principles

SOLID is five design principles that make object-oriented code maintainable, testable, and extensible. Violating them produces "code smells" — functions that are hard to test, extend, or understand.

---

## The Five Principles

### S — Single Responsibility Principle (SRP)
> A class (or function) should have **one, and only one, reason to change.**

A function that validates input, calculates totals, prints receipts, *and* saves to disk has four reasons to change. Each concern should live in its own function or class.

### O — Open/Closed Principle (OCP)
> Software entities should be **open for extension but closed for modification.**

Adding a new discount type should not require editing the core calculation function. Instead, pass in a strategy or subclass that handles the new rule.

### L — Liskov Substitution Principle (LSP)
> Subclasses must be **substitutable** for their base class without breaking correctness.

If `Bird.fly()` exists, a `Penguin(Bird)` that raises `NotImplementedError` on `fly()` violates LSP. The hierarchy needs redesigning.

### I — Interface Segregation Principle (ISP)
> Clients should not be forced to depend on interfaces they **do not use.**

One fat ABC with 10 methods forces every implementer to stub out the irrelevant ones. Split into smaller, focused ABCs.

### D — Dependency Inversion Principle (DIP)
> High-level modules should not depend on low-level modules. **Both should depend on abstractions.**

A `ReportService` that imports `PostgresDatabase` directly is tightly coupled. Inject a `Database` ABC instead — the service never needs to change when you swap the storage backend.

---

## Spotting SOLID Violations

| Symptom | Violated principle |
|---|---|
| Function is 100+ lines doing many unrelated things | SRP |
| Adding a feature requires editing existing code | OCP |
| Subclass crashes or behaves unexpectedly in parent's place | LSP |
| Implementing an ABC requires stubbing irrelevant methods | ISP |
| High-level code `import`s concrete low-level modules | DIP |

---

## Files in this subsection

| File | Purpose |
|---|---|
| `bad_code_example.py` | A deliberately bad function (`do_stuff`) mixing validation, tax calculation, printing, and file I/O — cryptic names, untestable, zero separation of concerns |
| `refactored_example.py` | SOLID-refactored version: each concern extracted into its own function/class; a top-level comment maps each SOLID violation in the bad version to its fix |

# 2.6 Modular Architecture

Modular architecture splits a codebase into layers with clear boundaries: each layer knows about the one below it through an *abstraction* (interface), never through a concrete implementation. The canonical three-layer split for a backend service is **Domain → Service → Repository**.

---

## The Three-Layer Pattern

```
┌─────────────────────────────────────┐
│           domain.py                 │  ← Pure data + rules, no I/O
│  (entities, value objects, errors)  │
└──────────────┬──────────────────────┘
               │  uses
┌──────────────▼──────────────────────┐
│           service.py                │  ← Business logic, orchestration
│  (use-case methods, validations)    │
└──────────────┬──────────────────────┘
               │  calls via interface
┌──────────────▼──────────────────────┐
│         repository.py               │  ← Data access only
│  (abstract Repository ABC +         │
│   InMemory / DB implementations)    │
└─────────────────────────────────────┘
```

### Why this separation?
- **Testability**: Unit tests for `service.py` inject a fake/mock repository — no real database needed.
- **Replaceability**: Swap `InMemoryRepository` for `PostgresRepository` without touching service or domain.
- **Readability**: New engineers find business rules in `service.py` immediately — they're not buried in SQL queries or HTTP calls.

### Domain layer rules
- No imports from `service.py` or `repository.py` (zero upward dependencies).
- No I/O (no `print`, no file access, no network calls).
- Contains data classes / entities and any *pure* business rules.

### Service layer rules
- Imports from `domain.py` and the Repository *interface* (ABC), never the concrete implementation.
- Orchestrates workflows: validate → act → persist → return result.

### Repository layer rules
- Owns all storage logic — SQL queries, JSON file I/O, in-memory dictionaries.
- The business service never needs to change when you swap implementations.

---

## Files in this subsection

| File | Purpose |
|---|---|
| `modular_demo.py` | Mini library-book checkout system split into domain (`Book`, `Member`), service (`LibraryService`), and repository (`BookRepository` ABC + `InMemoryBookRepository`) in a single file — each layer clearly labelled |

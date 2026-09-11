# 1.3 Collections — Quick Reference

## Core Concepts
Python collections store groups of items with distinct trade-offs:
- **`list`**: Ordered, mutable sequence indexed by integers.
- **`tuple`**: Ordered, immutable sequence; hashable if all its items are hashable.
- **`set`**: Unordered collection of unique, hashable elements.
- **`dict`**: Key-value mapping preserving insertion order; keys must be hashable.

## Key Syntax & Methods
- Slicing: `seq[start:stop:step]` creates a shallow copy of a sub-sequence.
- Comprehensions: `[x for x in data if cond]` and `{k: v for k, v in data}` provide concise, expressive transformations.
- Dict methods: `.get(key, default)`, `.items()`, `.keys()`, `.values()`.
- Copying: `list.copy()` / `copy.deepcopy()` to avoid unintended shared-mutation bugs.

## Theory to Know
- **Mutability vs. Immutability**: Modifying a list changes its contents in-place. Modifying a tuple or string requires allocating a new object.
- **Hashing & $O(1)$ Lookups**: Dict keys and set members must be hashable (`__hash__` and `__eq__`). This enables average $O(1)$ lookups via hash tables, compared to $O(n)$ linear scans across lists.
- **Reference Aliasing**: Writing `b = a` creates another reference to the same list in memory; mutating `b` mutates `a`. Always copy when defensive isolation is needed.

## Connection to What Was Built
- `inventory.py`: Demonstrates list comprehensions, sorting with lambdas, and in-place dict mutation.
- `employee_directory.py`: Explores unique sets, linear search, and explicitly tests shallow vs. deep copy isolation.
- `transaction_aggregation.py`: Uses dictionaries for grouping and demonstrates composite tuple keys `(category, month)`.

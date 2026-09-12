# 4.4 Transactions

A database transaction is a sequence of one or more database operations treated as a single indivisible unit of work, adhering to ACID principles (Atomicity, Consistency, Isolation, Durability).

## Key Concepts & Syntax

- `conn.commit()`: Writes all pending changes of the active transaction permanently to disk.
- `conn.rollback()`: Reverts all uncommitted queries made since the beginning of the transaction.
- `BEGIN / SAVEPOINT`: Defines transaction checkpoints or manual transaction boundaries.
- `try ... except ... finally`: The idiomatic Python structure wrapping database calls with `rollback()` on failure and `commit()` on success.
- `sqlite3.IntegrityError`: Raised when a constraint (e.g., CHECK, NOT NULL, FOREIGN KEY) is violated during query execution.

## Core Theory: Atomicity & The All-or-Nothing Guarantee

**Atomicity** guarantees that either every modification within a transaction succeeds and is committed, or the entire operation is rolled back with zero side effects. In financial transfers or order placements, executing step 1 (deducting funds or stock) without step 2 (crediting the recipient or logging the order) corrupts business state. Wrapping operations in a transaction ensures power cuts, network timeouts, or application exceptions leave the database completely clean and uncorrupted.

## Practical Implementation

In this folder, `transfer_exercise.py` implements an atomic financial transfer that rolls back sender debits if an artificial failure occurs before crediting the receiver. `order_transaction.py` orchestrates multi-step order placements across `orders`, `order_items`, and inventory reduction, guaranteeing that an out-of-stock item cancels the entire checkout without partial deductions.

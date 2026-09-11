# 1.2 Control Flow — Quick Reference

## Core Concepts
Control flow dictates the execution order of statements based on conditional logic and iteration. Python relies strictly on 4-space indentation levels rather than braces to define code blocks. Decisions evaluate boolean truth values, while loops iterate over finite sequences or continue indefinitely until an exit condition is met.

## Key Keywords & Syntax
- `if`, `elif`, `else`: Multi-branch conditional dispatch.
- `for ... in ...`: Definite iteration over any iterable object (lists, strings, ranges).
- `while`: Indefinite iteration running as long as a boolean expression remains `True`.
- `break`: Immediately terminates the innermost enclosing loop.
- `continue`: Skips the remainder of the current loop iteration and proceeds to the next.
- `<val_if_true> if <condition> else <val_if_false>`: Ternary conditional expression for inline assignments.

## Built-in Functions & Tools
- `range(start, stop[, step])`: Generates an arithmetic progression of integers on-demand (lazy evaluation, memory efficient).
- `enumerate(iterable, start=0)`: Yields pairs of `(index, item)` during loop traversal.

## Theory to Know
- **Short-Circuit Evaluation**: Logical `and` and `or` evaluate expressions from left to right and stop evaluation as soon as the outcome is determined.
- **Off-By-One Pitfalls**: `range(a, b)` includes `a` but excludes `b` (`[a, b)`).
- **Time Complexity in Search**: Iterating with `for item in list` performs an $O(n)$ linear scan; using `break` yields an average-case speedup when matches occur early.

## Connection to What Was Built
- `number_analysis.py`: Demonstrates mathematical filtering, parity checks, and $O(\sqrt{n})$ loop-based prime verification.
- `pattern_generation.py`: Uses nested `for` loops and string multiplication for grid shapes.
- `search_filter.py`: Implements early-exit linear search with `break` and data filtering with `continue`.
- `menu_loop.py`: Employs a stateful `while True` loop with sentinel exit commands.

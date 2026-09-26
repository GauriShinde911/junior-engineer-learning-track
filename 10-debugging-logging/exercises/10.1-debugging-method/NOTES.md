# 10.1 Debugging Method

## Core Concepts
Debugging is not guesswork or changing random lines until code works; it is a systematic, scientific method. When an error occurs, an engineer reproduces the issue with minimal inputs, isolates the exact failure path, gathers concrete evidence before making assumptions, forms a testable hypothesis, applies a surgical fix, and verifies the solution with automated regression tests.

## Key Tools & Techniques
- `id(object)`: Inspects memory addresses to identify shared references or mutable default argument traps.
- `print()` / Debugger Breakpoints (`breakpoint()`): Pauses execution and prints intermediate variables to inspect state transitions.
- Assertions (`assert`): Encodes invariant assumptions directly into code to detect invalid state as early as possible.
- Minimal Reproducible Example (MRE): Strips away unrelated dependencies and boilerplate until only the failing logic remains.

## Why Evidence Must Come Before Hypotheses
Humans suffer from confirmation bias: if you form a hypothesis first without inspecting state, you instinctively search only for data that proves your hunch and ignore contradictory facts. Gathering hard runtime evidence first (memory addresses, variable values, call boundaries) constrains the solution space to objective facts, preventing wasteful rewrites of working code.

## Connection to Exercises
In `broken_program_1.py`, we traced calculation logic to discover taxes charged on pre-discount subtotals. In `broken_program_2.py`, we used `id()` to expose a mutable default list leaking state across requests. In `broken_program_3.py`, we observed in-place state mutation corrupting warehouse balances upon partial batch failures, resolving it with a two-phase atomic validation pattern documented in `DEBUG_LOG.md`.

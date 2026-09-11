# 1.4 Functions — Quick Reference

## Core Concepts
Functions are first-class citizens in Python, meaning they can be assigned to variables, passed as arguments, and returned from other functions. Well-designed functions encapsulate single responsibilities, accept explicit inputs via parameters, and return deterministic results.

## Key Keywords & Syntax
- `def function_name(params):`: Defines a callable function.
- `return <val>`: Exits function and delivers output to caller; omitting `return` yields `None`.
- `*args`: Collects extra positional arguments into an immutable `tuple`.
- `**kwargs`: Collects extra keyword arguments into a standard `dict`.
- `*`: Standalone asterisk marks subsequent arguments as keyword-only.

## Scope & Lifetime
- **LEGB Rule**: Python resolves variable names by searching scopes in order: **L**ocal $\rightarrow$ **E**nclosing $\rightarrow$ **G**lobal $\rightarrow$ **B**uilt-in.
- **Default Argument Pitfall**: Default parameter expressions evaluate once when the function is defined. Never use mutable objects (`[]` or `{}`) as defaults; use `None` and initialize inside the body instead.

## Theory to Know
- **Pure Functions**: A pure function produces the exact same output for given inputs and causes zero observable side effects (no printing, no disk writes, no mutation of global or passed mutable variables). Pure functions are fundamentally easier to test and parallelize.

## Connection to What Was Built
- `utility_library.py`: Refactors ad-hoc math, conversion, text formatting, and collection filtering logic from sections 1.1–1.3 into pure, typed functions using `*args`, `**kwargs`, and keyword-only constraints.

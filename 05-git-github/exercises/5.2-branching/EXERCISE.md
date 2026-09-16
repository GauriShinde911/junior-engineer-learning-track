# Exercise 5.2: Branching Strategies & Keeping Current

In professional engineering teams, `main` represents production-ready code. All feature work and bug fixes are developed in isolated branches, committed in small logical increments, kept up to date with `main`, and integrated cleanly.

> **Safety Warning**: Run all commands inside:
> `cd exercises/5.2-branching/sandbox`

---

## Step 0: Initialize Sandbox

```bash
python exercises/5.2-branching/setup_sandbox.py
cd exercises/5.2-branching/sandbox
```

---

## Step 1: Feature Branch 1 — Multiplication & Division

1. Create and switch to a descriptive feature branch:
   ```bash
   git switch -c feat/multiply-divide
   ```
2. Open `calculator.py` and implement multiplication:
   ```python
   def multiply(a: float, b: float) -> float:
       """Returns the product of two numbers."""
       return a * b
   ```
3. Commit small atomic chunk 1:
   ```bash
   git add calculator.py
   git commit -m "feat: implement multiply function"
   ```
4. Now implement division in `calculator.py`:
   ```python
   def divide(a: float, b: float) -> float:
       """Returns the quotient of two numbers."""
       if b == 0:
           raise ValueError("Cannot divide by zero.")
       return a / b
   ```
5. Commit small atomic chunk 2:
   ```bash
   git add calculator.py
   git commit -m "feat: implement divide function with zero check"
   ```
6. Verify your two commits on this branch:
   ```bash
   git log --oneline -n 2
   ```

---

## Step 2: Merge Branch 1 with Non-Fast-Forward (`--no-ff`)

1. Switch back to `main`:
   ```bash
   git switch main
   ```
2. Merge the feature branch creating an explicit merge commit:
   ```bash
   git merge --no-ff feat/multiply-divide -m "merge: integrate feat/multiply-divide into main"
   ```
   *(Why `--no-ff`? In team repos, `--no-ff` preserves the visual group of commits that represent the feature lifecycle in Git history).*
3. Delete the merged local branch to keep the repo clean:
   ```bash
   git branch -d feat/multiply-divide
   ```

---

## Step 3: Feature Branch 2 — Fix Typo & Add Docs on Main

Simulate a teammate pushing an update to `main` while you work on another branch.

1. Create a new branch for testing:
   ```bash
   git switch -c test/calculator-tests
   ```
2. While on this branch, pretend `main` received an important hotfix. Switch to `main`:
   ```bash
   git switch main
   ```
3. Update `README.md` on `main`:
   ```markdown
   # Math Utilities Library

   Standard mathematical operations service. Supported: add, subtract, multiply, divide.
   ```
4. Commit the documentation fix directly to `main`:
   ```bash
   git add README.md
   git commit -m "docs: document supported math operations in README"
   ```

---

## Step 4: Keeping Your Branch Current via Rebase

Now switch back to your in-progress feature branch:

```bash
git switch test/calculator-tests
```
Your branch is now "behind" `main` by 1 commit.

1. Add tests in `test_calculator.py` on your branch:
   ```python
   from calculator import multiply, divide
   import pytest

   def test_multiplication():
       assert multiply(3, 4) == 12
       assert multiply(-2, 3) == -6

   def test_division_by_zero():
       try:
           divide(10, 0)
           assert False, "Should raise ValueError"
       except ValueError:
           pass
   ```
2. Commit the new tests:
   ```bash
   git add test_calculator.py
   git commit -m "test: add unit tests for multiply and divide"
   ```
3. Rebase your branch onto the latest `main`:
   ```bash
   git rebase main
   ```
4. Inspect what happened:
   ```bash
   git log --graph --oneline
   ```
   Git replayed your test commit on top of the latest `main` commit (`docs: document supported math operations...`). Your branch history is completely linear and up to date!

5. Finally, merge into `main`:
   ```bash
   git switch main
   git merge test/calculator-tests
   git branch -d test/calculator-tests
   ```

---

## Step 5: Feature Branch 3 — Power & Square Root

1. Branch off `main`:
   ```bash
   git switch -c feat/advanced-math
   ```
2. Add exponentiation to `calculator.py`:
   ```python
   def power(base: float, exp: float) -> float:
       """Returns base raised to the power of exp."""
       return base ** exp
   ```
3. Commit and merge back to `main`:
   ```bash
   git add calculator.py
   git commit -m "feat: add power function"
   git switch main
   git merge feat/advanced-math
   git branch -d feat/advanced-math
   ```

---

## Verification

Run:
```bash
git log --graph --oneline
python test_calculator.py
```
All commits are organized, all branches were safely merged, and test operations pass!

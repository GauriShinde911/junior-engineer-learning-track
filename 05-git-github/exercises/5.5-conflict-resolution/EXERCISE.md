# Exercise 5.5: Merge Conflict Resolution

Merge conflicts occur whenever two branches make divergent modifications to the exact same lines of code since their common ancestor commit. Git cannot guess which change is correct, so it pauses the merge, inserts conflict markers, and asks the developer to synthesize the resolution.

> **Safety Warning**: Run all commands strictly inside:
> `cd exercises/5.5-conflict-resolution/sandbox`

---

## Step 0: Initialize Sandbox

```bash
python exercises/5.5-conflict-resolution/setup_conflict_sandbox.py
cd exercises/5.5-conflict-resolution/sandbox
```

Verify your starting state:
```bash
git branch
```
You have three branches: `main`, `feature/vip-loyalty`, and `feature/seasonal-promo`.

---

## Step 1: Reproduce the Conflict

1. Merge `feature/seasonal-promo` into `main`:
   ```bash
   git merge feature/seasonal-promo
   ```
   This succeeds cleanly with a Fast-Forward merge because `main` had no conflicting commits yet.

2. Now attempt to merge `feature/vip-loyalty` into `main`:
   ```bash
   git merge feature/vip-loyalty
   ```
   Git pauses and prints:
   ```text
   Auto-merging pricing.py
   CONFLICT (content): Merge conflict in pricing.py
   Automatic merge failed; fix conflicts and then commit the result.
   ```
3. Check status:
   ```bash
   git status
   ```
   Notice that `pricing.py` is listed under **"Unmerged paths: both modified"**.

---

## Step 2: Inspect the Conflict Markers

Open `pricing.py` in your text editor. Look at the conflict block:

```python
<<<<<<< HEAD
    if customer_tier == "holiday_special":
        discount_rate = 0.25
    elif customer_tier == "member":
        discount_rate = 0.10
    elif customer_tier == "standard":
        discount_rate = 0.02
=======
    if customer_tier == "vip":
        discount_rate = 0.20
    elif customer_tier == "member":
        discount_rate = 0.08
    elif customer_tier == "standard":
        discount_rate = 0.0
>>>>>>> feature/vip-loyalty
```

### Anatomical Breakdown of Conflict Markers:
- `<<<<<<< HEAD`: Marks the start of the changes from your current branch (`main`, which contains the seasonal promo).
- `=======`: The dividing line between the two competing implementations.
- `>>>>>>> feature/vip-loyalty`: Marks the end of changes coming from the branch you are merging in.

---

## Step 3: Thoughtful Resolution (Do NOT Blindly Pick One Side!)

### What "Blindly Picking One Side" Means (The Bad Way):
Novice engineers often pick `Accept Current Change` or `Accept Incoming Change` blindly.
- If you keep only `HEAD`, the VIP loyalty program is lost!
- If you keep only `feature/vip-loyalty`, the holiday seasonal promo is erased!

### The Senior Engineer Approach (Synthesize Both Intents):
1. Understand intent 1: Business wants the new `holiday_special` tier (25%).
2. Understand intent 2: Business wants the new `vip` tier (20%).
3. Negotiate overlapping values: For `member`, the promotional rate (10%) takes precedence over the standard 8% rate during the promo season. Standard remains 0%.

### Edit `pricing.py`
Delete all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) and synthesize the clean, unified logic:

```python
"""E-commerce pricing calculation engine."""

def calculate_discount(order_total: float, customer_tier: str) -> float:
    """Calculates final discounted price based on customer membership."""
    discount_rate = 0.0
    # --- TIER DISCOUNT LOGIC START ---
    if customer_tier == "holiday_special":
        discount_rate = 0.25
    elif customer_tier == "vip":
        discount_rate = 0.20
    elif customer_tier == "member":
        discount_rate = 0.10
    elif customer_tier == "standard":
        discount_rate = 0.0
    # --- TIER DISCOUNT LOGIC END ---

    discount_amount = round(order_total * discount_rate, 2)
    return round(order_total - discount_amount, 2)
```

---

## Step 4: Validate with Tests Before Finalizing

Never commit a merge resolution before validating that the code works!

1. Update `test_pricing.py` to assert both the holiday special and VIP tier:
   ```python
   """Unit tests for pricing calculations."""
   from pricing import calculate_discount

   def test_standard():
       assert calculate_discount(100.0, "standard") == 100.0

   def test_member():
       assert calculate_discount(100.0, "member") == 90.0

   def test_vip():
       assert calculate_discount(100.0, "vip") == 80.0

   def test_holiday():
       assert calculate_discount(100.0, "holiday_special") == 75.0

   if __name__ == "__main__":
       test_standard()
       test_member()
       test_vip()
       test_holiday()
       print("All resolved pricing tests passed!")
   ```
2. Run the test script:
   ```bash
   python test_pricing.py
   ```
   Confirm output: `All resolved pricing tests passed!`

---

## Step 5: Stage and Complete the Merge

1. Tell Git the conflict in `pricing.py` is resolved:
   ```bash
   git add pricing.py test_pricing.py
   ```
2. Check `git status`:
   ```bash
   git status
   ```
   All conflicts fixed, changes staged.
3. Finalize the merge commit:
   ```bash
   git commit -m "merge: resolve pricing tiers combining holiday promo and VIP loyalty"
   ```
4. Verify the integrated history:
   ```bash
   git log --graph --oneline -n 6
   ```

You have successfully navigated, analyzed, synthesized, and tested a real merge conflict!

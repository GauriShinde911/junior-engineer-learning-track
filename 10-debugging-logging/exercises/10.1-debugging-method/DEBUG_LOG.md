# Debugging Log: 10.1 Debugging Method

This log documents the systematic debugging process applied to each of the three programs in this subsection, adhering to the evidence-first protocol: **Reproduce -> Isolate -> Hypothesize -> Inspect Evidence -> Fix -> Verify**.

---

## Case 1: `broken_program_1.py` (Sales Tax Calculation on Discounted Orders)

### 1. Reproduce
- **Trigger**: Run calculation with subtotal $140.00, 20% promotional discount ($28.00), and 10% tax rate.
- **Expected Outcome**:
  - Net subtotal: `$140.00 - $28.00 = $112.00`
  - Tax (10% on net): `$11.20`
  - Total: `$112.00 + $11.20 = $123.20`
- **Actual Outcome**:
  - Gross subtotal: `$140.00`
  - Discount: `$28.00`
  - Tax: `$14.00` (overcharged by $2.80)
  - Total: `$126.00`

### 2. Isolate
- Traced the calculation through the function line-by-line:
  - Line 18: `gross_subtotal = sum(...)` -> evaluates to `140.0`.
  - Line 19: `discount_amount = gross_subtotal * (discount_percent / 100.0)` -> evaluates to `28.0`.
  - Line 22: `tax_amount = gross_subtotal * tax_rate` -> calculates tax on `$140.00` rather than the post-discount taxable amount.

### 3. Hypothesize
- **Hypothesis**: The formula for `tax_amount` incorrectly references `gross_subtotal` instead of computing `net_subtotal = gross_subtotal - discount_amount` first and applying `tax_rate` to `net_subtotal`.

### 4. Inspect Evidence (Collected Prior to Code Change)
- Running an interactive inspection session:
  ```python
  gross = 140.0
  discount = 28.0
  tax_rate = 0.10
  
  # Current buggy code output:
  print("Current tax:", gross * tax_rate)           # Yields 14.0
  
  # Business requirement evidence:
  net = gross - discount
  print("True taxable base:", net)                   # Yields 112.0
  print("Expected tax:", net * tax_rate)             # Yields 11.2
  print("Difference (overcharge):", (gross * tax_rate) - (net * tax_rate))  # Yields 2.80
  ```
- Evidence clearly confirms that the tax calculation formula has an architectural ordering defect.

### 5. The Fix
- Compute `net_subtotal = gross_subtotal - discount_amount`.
- Update `tax_amount` to multiply `tax_rate` against `net_subtotal`.
- Update `total = net_subtotal + tax_amount`.

### 6. Verify
- Ran test cases covering 0% discount, 100% discount, zero tax rate, and fractional currency amounts.
- In all scenarios, `net_subtotal + tax_amount == total` and customer is never taxed on discounted amounts.

---

## Case 2: `broken_program_2.py` (Cross-Tenant Tag Pollution via Mutable Default)

### 1. Reproduce
- **Trigger**: Invocations of `register_user_event_buggy` in sequence for separate user sessions:
  1. `register_user_event_buggy("user_101", "login")`
  2. `register_user_event_buggy("user_202", "view_profile")`
- **Expected Outcome**:
  - `user_101` tags: `['source:api', 'action:login']`
  - `user_202` tags: `['source:api', 'action:view_profile']`
- **Actual Outcome**:
  - `user_202` tags: `['source:api', 'action:login', 'source:api', 'action:view_profile']`
  - User 202's event payload contains User 101's audit history!

### 2. Isolate
- Inspected the function signature: `def register_user_event_buggy(user_id, action, tags=[])`.
- Checked object memory addresses (`id(tags)`) across calls.

### 3. Hypothesize
- **Hypothesis**: The default parameter `tags=[]` is evaluated once when the function definition is executed at module import time, not each time the function is called. Therefore, every invocation that omits `tags` mutates the same list instance stored in `__defaults__`.

### 4. Inspect Evidence (Collected Prior to Code Change)
- Examined function defaults in the Python runtime:
  ```python
  fn = register_user_event_buggy
  print("Default object before call:", fn.__defaults__[0], "ID:", id(fn.__defaults__[0]))
  fn("user_1", "action_1")
  print("Default object after call 1:", fn.__defaults__[0], "ID:", id(fn.__defaults__[0]))
  fn("user_2", "action_2")
  print("Default object after call 2:", fn.__defaults__[0], "ID:", id(fn.__defaults__[0]))
  ```
- **Observed Output**:
  - Object IDs remained identical: `id(fn.__defaults__[0]) == 2419082312` across calls.
  - The list inside `__defaults__` grew on each call: `['source:api', 'action:action_1', 'source:api', 'action:action_2']`.
- Evidence conclusively demonstrates that state is persisting in the function object's `__defaults__` tuple.

### 5. The Fix
- Replace `tags: List[str] = []` with `tags: Optional[List[str]] = None`.
- Inside the function body, initialize `user_tags = [] if tags is None else list(tags)`.

### 6. Verify
- Re-ran consecutive calls with different user IDs; verified `id(event1['tags']) != id(event2['tags'])`.
- Verified that callers who supply an explicit list do not have their original list mutated externally (`list(tags)` shallow copy).

---

## Case 3: `broken_program_3.py` (In-Place Mutation Without Rollback on Batch Failure)

### 1. Reproduce
- **Trigger**: Run a 3-item batch transfer where Item 1 and Item 2 are valid, but Item 3 exceeds available stock.
  - Source: `{"LAPTOP": 10, "MOUSE": 50, "MONITOR": 2}`
  - Target: `{"LAPTOP": 0, "MOUSE": 0, "MONITOR": 0}`
  - Batch: 3 Laptops, 10 Mice, 5 Monitors (only 2 in stock).
- **Expected Outcome**:
  - Transfer fails with `InsufficientStockError`.
  - Source and Target remain completely unchanged (atomic all-or-nothing semantics).
- **Actual Outcome**:
  - Transfer fails with `InsufficientStockError`.
  - Source became: `{"LAPTOP": 7, "MOUSE": 40, "MONITOR": 2}`.
  - Target became: `{"LAPTOP": 3, "MOUSE": 10, "MONITOR": 0}`.
  - Inventory is partially transferred and state is corrupt.

### 2. Isolate
- Traced the loop in `transfer_inventory_batch_buggy`:
  ```python
  for item in transfers:
      # checks item
      source[sku] -= qty
      target[sku] += qty
  ```
- Mutation occurs inside the loop before subsequent items are validated.

### 3. Hypothesize
- **Hypothesis**: The system lacks transaction isolation. Checking constraints iteratively while mutating shared state means any late failure leaves previous mutations permanent.

### 4. Inspect Evidence (Collected Prior to Code Change)
- Monitored dictionary state at each loop step:
  ```python
  Step 0: Source LAPTOP=10, Target LAPTOP=0
  Step 1 (LAPTOP transferred): Source LAPTOP=7, Target LAPTOP=3
  Step 2 (MOUSE transferred): Source MOUSE=40, Target MOUSE=10
  Step 3 (MONITOR requested 5, avail 2): EXCEPTION RAISED
  Post-Exception State Check:
  Assert Source == Initial State -> FAILED (LAPTOP=7 != 10, MOUSE=40 != 50)
  ```
- Evidence proves the loop produces side effects before validation is complete.

### 5. The Fix
- Implement a two-phase transaction pattern:
  - **Phase 1 (Validation & Aggregation)**: Compute total requested deductions per SKU and verify that every SKU exists and has sufficient stock across the entire batch.
  - **Phase 2 (Atomic Application)**: Once all checks pass without exception, apply all inventory mutations.

### 6. Verify
- Tested batch failures on first item, middle item, and last item.
- Confirmed source and target dictionaries retain identical pre-transfer state whenever any error is raised.
- Confirmed successful batches transfer all items completely.

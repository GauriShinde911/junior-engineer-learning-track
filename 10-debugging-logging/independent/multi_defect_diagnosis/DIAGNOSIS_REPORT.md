# Independent Challenge: Multi-Defect Diagnosis Report

This diagnosis report investigates and documents three distinct defects discovered in `broken_app/`. In adherence to the evidence-first protocol, runtime evidence was systematically gathered and inspected **prior** to designing any code modifications.

---

## Defect 1: Relative Path Resolution & Uncoerced Environment Variable in `config.py`

### 1. Initial Symptom
- When running `python broken_app/main.py` from repository root:
  ```text
  FileNotFoundError: [Errno 2] No such file or directory: 'data/catalog.json'
  ```
- When `BATCH_LIMIT` is set in the environment (`export BATCH_LIMIT=20`):
  ```text
  TypeError: '>' not supported between instances of 'int' and 'str'
  ```

### 2. Evidence Gathered (Prior to Fix)
- Inspected `broken_app/config.py`:
  ```python
  catalog_path = "data/catalog.json"
  with open(catalog_path, "r", encoding="utf-8") as f:
  ```
- Evaluated `Path.cwd()` vs `Path(__file__)`:
  - When the process current working directory (`CWD`) is `repo/`, `"data/catalog.json"` looks for `repo/data/catalog.json` instead of `repo/10-debugging-logging/independent/multi_defect_diagnosis/broken_app/data/catalog.json`.
- Evaluated `get_batch_limit()` with `$env:BATCH_LIMIT = "25"`:
  - `type(os.getenv("BATCH_LIMIT"))` returned `<class 'str'>`.
  - In `main.py`: `total_units > batch_limit` evaluated `1 > "25"`, triggering a fatal `TypeError`.

### 3. Root Cause
- Hardcoded relative filesystem paths depend on process invocation directory rather than module-relative paths.
- `os.getenv()` returns strings, requiring explicit integer casting with fallback handling.

### 4. Proposed Fix
- Use `Path(__file__).resolve().parent / "data" / "catalog.json"`.
- Wrap `get_batch_limit()` in `int(os.getenv("BATCH_LIMIT", 50))`.

---

## Defect 2: Corrupted Stock on Partial Order Failure in `inventory.py`

### 1. Initial Symptom
An order requesting `{"sku": "MOUSE", "quantity": 10}` and `{"sku": "MONITOR", "quantity": 99}` failed with `OutOfStockError`, but the warehouse system permanently lost 10 mice from available stock.

### 2. Evidence Gathered (Prior to Fix)
- Executed an inspection session tracking `inventory.stock` before and after failed reservation:
  ```python
  inv = InventoryManager(catalog)
  print("Pre-order MOUSE stock:", inv.stock["MOUSE"])  # 50
  try:
      inv.reserve_items([{"sku": "MOUSE", "quantity": 10}, {"sku": "MONITOR", "quantity": 99}])
  except OutOfStockError:
      pass
  print("Post-failure MOUSE stock:", inv.stock["MOUSE"]) # 40 (Lost 10 units!)
  ```
- The code in `broken_app/inventory.py` subtracts stock sequentially inside the loop `self.stock[sku] -= qty` before validating subsequent items in the batch.

### 3. Root Cause
Lack of atomic transaction semantics or two-phase commit validation: in-place mutations occurred before complete verification of all order items.

### 4. Proposed Fix
Implement two-phase validation:
1. Aggregate and verify that all requested items exist and have sufficient stock.
2. Only after all checks succeed without error, perform stock deductions.

---

## Defect 3: Off-By-One Threshold & Tax Calculation Error in `pricing.py`

### 1. Initial Symptom
- Customer orders with subtotal of exactly $100.00 (e.g. 1 Mechanical Keyboard) received $0.00 discount despite company policy advertising "15% off orders of $100 or more".
- For orders over $100.00, sales tax was charged on the undiscounted subtotal, resulting in customer overcharges.

### 2. Evidence Gathered (Prior to Fix)
- Evaluated condition with `subtotal = 100.00`:
  ```python
  subtotal = 100.00
  print(subtotal > 100.0)   # False!
  print(subtotal >= 100.0)  # True
  ```
  Strict inequality `>` improperly excluded boundary values.
- Evaluated tax calculation on a $200 order with $30 discount (8% tax rate):
  ```python
  # Buggy calculation:
  tax_buggy = 200.0 * 0.08  # $16.00
  total_buggy = (200.0 - 30.0) + 16.00  # $186.00
  
  # Net taxable base calculation:
  net = 200.0 - 30.0  # $170.00
  tax_correct = 170.0 * 0.08  # $13.60
  total_correct = 170.0 + 13.60  # $183.60
  # Overcharge: $2.40
  ```

### 3. Root Cause
- Off-by-one boundary defect (`>` instead of `>=`).
- Tax assessed on gross subtotal instead of net post-discount subtotal.

### 4. Proposed Fix
- Change condition to `if subtotal >= 100.0:`.
- Assess tax on `net_subtotal = subtotal - discount`.

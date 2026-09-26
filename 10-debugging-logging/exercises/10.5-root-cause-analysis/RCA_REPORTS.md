# Root Cause Analysis (RCA) Reports: 10.5

This document details 5 industry-grade RCA incident reports, demonstrating the distinction between **superficial symptoms** and **fundamental root causes**, followed by minimal reproductions, corrective actions, and regression test strategies.

---

## Incident Report 1: Premature Token Expiration Across Multi-Region Deployments

### 1. Symptom as First Observed
Users in Asia-Pacific regions reported immediate session logouts upon logging in, while European users experienced session timeouts occurring 5 hours after the documented 1-hour expiration window.

### 2. Actual Root Cause
The service compared `datetime.now()` (naive local server time) against a UTC-aware token timestamp. Depending on the server host's timezone offset from UTC (`+08:00` vs `-05:00`), naive comparisons yielded incorrect expiration judgments.

### 3. Minimal Reproduction
```python
from datetime import datetime, timezone, timedelta

valid_utc_token = {"expires_at": datetime.now(timezone.utc) + timedelta(hours=1)}
# On a machine set to GMT+5:30:
now_naive = datetime.now()
is_expired = now_naive >= valid_utc_token["expires_at"].replace(tzinfo=None)
print("Falsely expired?", is_expired)  # Evaluates to True prematurely
```

### 4. Corrective Action Taken
Enforced strict timezone normalization across all date operations: all timestamps are parsed and compared as UTC-aware datetimes (`datetime.now(timezone.utc)`).

### 5. Regression Test Specification
A parameterized test running assertions against mock tokens created across arbitrary timezone offsets (`UTC+12`, `UTC-8`, `UTC+0`), asserting that active tokens evaluate to `is_expired == False` regardless of the host environment's local clock.

---

## Incident Report 2: Priority Ordering Inversion in Task Scheduling Queue

### 1. Symptom as First Observed
High-priority operational maintenance tickets with priority score `100` were consistently scheduled *after* low-priority tickets with score `20` in production batch runs.

### 2. Actual Root Cause
Ticket payloads ingested from JSON APIs retained priority scores as string literals (`"100"`, `"20"`). Standard Python sorting compared ASCII character codes alphabetically: `"1"` comes before `"2"`, so `"100"` was ranked lower than `"20"`.

### 3. Minimal Reproduction
```python
records = [{"task": "Urgent", "priority": "100"}, {"task": "Minor", "priority": "20"}]
sorted_tasks = sorted(records, key=lambda x: x["priority"])
print([t["task"] for t in sorted_tasks])  # Yields ['Urgent', 'Minor'] in ascending sort
```

### 4. Corrective Action Taken
Cast the comparison key to integer (`key=lambda x: int(x["priority"])`) and added strict Pydantic/dataclass schema coercion on API ingestion boundaries.

### 5. Regression Test Specification
A test asserting that a list of stringified numeric priorities `["1", "10", "2", "20", "100"]` sorts strictly into numerical order: `["1", "2", "10", "20", "100"]`.

---

## Incident Report 3: Cross-User Settings Overwrite in Multi-Tenant Profiles

### 1. Symptom as First Observed
When Customer A opted out of marketing emails in their profile dashboard, marketing emails were abruptly halted for all new signups throughout the entire platform.

### 2. Actual Root Cause
The user provisioning function used `DEFAULT_PROFILE_TEMPLATE.copy()` to generate new accounts. Because `dict.copy()` creates a shallow clone, the nested `"preferences"` dictionary was shared by reference across all user profile instances in the process memory.

### 3. Minimal Reproduction
```python
TEMPLATE = {"user": "default", "settings": {"email": True}}
user1 = TEMPLATE.copy()
user2 = TEMPLATE.copy()
user1["settings"]["email"] = False
print("User 2 email setting affected:", user2["settings"]["email"])  # Prints False!
```

### 4. Corrective Action Taken
Replaced `dict.copy()` with `copy.deepcopy()` or factory functions that instantiate a new nested dictionary structure on every invocation.

### 5. Regression Test Specification
A test that instantiates two users from the default template, modifies a nested preference in user 1, and verifies that `id(user1["preferences"]) != id(user2["preferences"])` and user 2 retains default values.

---

## Incident Report 4: Ledger Discrepancies in Micro-Payment Clearinghouse

### 1. Symptom as First Observed
Nightly reconciliation between transaction processing logs and bank deposit summaries showed an unexplained drift of several cents ($0.04 to $0.12) each evening.

### 2. Actual Root Cause
Transaction fee percentages were calculated using IEEE-754 binary floating-point numbers (`float`). Repeated addition of fractional decimal numbers (such as `0.10` or `0.05`) introduced binary rounding approximations that accumulated across 100,000+ daily transactions.

### 3. Minimal Reproduction
```python
total = 0.0
for _ in range(10):
    total += 0.10
print("Total float:", total)  # 0.9999999999999999, not 1.00
print("Drift check:", total == 1.0)  # False!
```

### 4. Corrective Action Taken
Refactored financial ledgers to use Python's standard `decimal.Decimal` with explicit `ROUND_HALF_UP` quantization to `0.01`.

### 5. Regression Test Specification
A test aggregating an array of 1,000 micro-fee entries of `0.10` and asserting `result == Decimal("100.00")` with zero floating point drift.

---

## Incident Report 5: Corrupted Template Token Extraction in Notification Service

### 1. Symptom as First Observed
SMS notifications sent to users rendered with mangled text: `Hello {{first_name, your balance is $50.00}}` instead of interpolating both the recipient's first name and account balance.

### 2. Actual Root Cause
The extraction engine utilized a greedy regular expression `r"\{\{(.*)\}\}"`. The quantifier `.*` consumed everything from the very first `{{` to the very last `}}` on the line, bridging across multiple independent template tokens.

### 3. Minimal Reproduction
```python
import re
text = "Welcome {{name}}, your code is {{code}}!"
matches = re.findall(r"\{\{(.*)\}\}", text)
print("Greedy matches:", matches)  # ['name}}, your code is {{code']
```

### 4. Corrective Action Taken
Changed regex quantifier to non-greedy `r"\{\{(.*?)\}\}"` (or character-class constrained `r"\{\{([^}]+)\}\}"`).

### 5. Regression Test Specification
A test passing template strings with 3+ placeholders on a single line and asserting that `extract_template_variables_fixed` extracts each token cleanly as separate list elements.

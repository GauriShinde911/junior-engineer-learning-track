# Unfamiliar Codebase Bug Fix (Independent Challenge)

A hands-on challenge demonstrating how to inherit an unfamiliar codebase with a reported defect, capture expected behavior with a specification, write failing tests first, and fix the defect with full regression coverage.

---

## Challenge Summary

- **Module**: `buggy_module.py` (E-Commerce Checkout Engine)
- **Specification**: [`SPECIFICATION.md`](./SPECIFICATION.md)
- **Test Suite**: `test_buggy_module.py`

### The Defects Investigated
1. **Ticket #ENG-402**: Free shipping eligibility was previously checked against `raw_subtotal >= 50.0` instead of `discounted_subtotal >= 50.0`. If a customer ordered $52.00 of goods with a 15% discount ($44.20), they were erroneously given free shipping.
2. **Ticket #ENG-403**: Silver tier customers spending exactly $200.00 were denied the gold tier discount because the code checked `subtotal > 200.0` rather than `>= 200.0`.

---

## Test-First Engineering Sequence

1. **Analyze Requirements**:
   Read `SPECIFICATION.md` to understand the domain model, business constraints, and exact ticket reports.

2. **Pin Down Behavior with Failing Tests First**:
   Before modifying any production logic in `buggy_module.py`, we authored `test_buggy_module.py`:
   - `test_regression_eng_402_free_shipping_disallowed_when_discount_drops_under_50()`
   - `test_regression_eng_403_silver_upgrade_at_exact_boundary()`
   - Boundary tests for promo codes, empty carts, and negative values.
   Running pytest at this stage reproduces the exact failures and pins the contract.

3. **Refactor & Fix**:
   Updated `buggy_module.py` to evaluate shipping after all discounts are subtracted and adjusted the silver upgrade comparison to `>= 200.00`.

4. **Verify All Tests Pass**:
   Run the test suite to confirm both specification requirements and bug fixes pass without side effects.

---

## Running the Tests

To execute this test suite:

```bash
pytest 06-pytest-testing/independent/unfamiliar_codebase_fix/ -v
```

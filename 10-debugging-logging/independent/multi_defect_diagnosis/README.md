# Multi-Defect Diagnosis Challenge: Order Fulfillment Pipeline

This project contains an order fulfillment and inventory management pipeline implemented in two versions:
1. `broken_app/`: The original system planted with 3 realistic defects across different files (`config.py`, `inventory.py`, `pricing.py`).
2. `fixed_app/`: The remediated production version accompanied by regression tests.

---

## Architecture Overview

```
multi_defect_diagnosis/
├── broken_app/
│   ├── data/catalog.json
│   ├── config.py
│   ├── inventory.py
│   ├── pricing.py
│   └── main.py
├── fixed_app/
│   ├── data/catalog.json
│   ├── config.py
│   ├── inventory.py
│   ├── pricing.py
│   └── main.py
├── DIAGNOSIS_REPORT.md
├── test_independent.py
└── README.md
```

---

## How to Run

### 1. Running the Broken App
To observe the path and boundary failures:
```bash
python 10-debugging-logging/independent/multi_defect_diagnosis/broken_app/main.py
```

### 2. Running the Fixed App
To run the corrected pipeline:
```bash
python 10-debugging-logging/independent/multi_defect_diagnosis/fixed_app/main.py
```

### 3. Running Automated Tests
Run pytest across the independent challenge test suite:
```bash
python -m pytest 10-debugging-logging/independent/multi_defect_diagnosis/test_independent.py -v
```

---

## Summary of Defects & Discovery Process
1. **Config Path & Env Var**: Discovered by running from outside the project directory and setting `BATCH_LIMIT`. Traced to working-directory relative paths and unparsed environment variables.
2. **Partial Inventory Mutation**: Discovered by inspecting inventory stock balances after an order failed due to out-of-stock items. Fixed with two-phase atomic validation.
3. **Threshold Boundary & Tax**: Discovered by testing an order of exactly $100.00 and auditing tax line-items on discounted orders. Fixed using inclusive comparison (`>= 100.0`) and assessing tax on the net subtotal.

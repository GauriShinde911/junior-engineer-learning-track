"""
defect_4.py - Defect Scenario 4: Floating Point Precision Drift in Accounting

Symptom:
Financial audit reports report unbalanced ledger discrepancies of $0.01 or fractional
fractions of a cent after processing thousands of micro-fee transactions.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Union


def sum_ledger_transactions_buggy(amounts: List[float]) -> float:
    """
    BUGGY IMPLEMENTATION:
    Uses standard IEEE-754 binary float addition.
    0.1 + 0.2 != 0.3 in IEEE floats, causing cumulative drift.
    """
    total = 0.0
    for amt in amounts:
        total += amt
    return total


def sum_ledger_transactions_fixed(amounts: List[Union[str, float]]) -> Decimal:
    """
    CORRECTED IMPLEMENTATION:
    Uses Python's standard `decimal.Decimal` module with exact base-10 arithmetic
    and fixed two-decimal-place quantization.
    """
    total = Decimal("0.00")
    for amt in amounts:
        # Convert float to str first to avoid initial binary float imprecision
        d_val = Decimal(str(amt)) if isinstance(amt, float) else Decimal(amt)
        total += d_val
    
    # Quantize to standard currency 2 decimal places
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


if __name__ == "__main__":
    micro_fees = [0.10] * 10  # Ten 10-cent transactions = $1.00
    print("Buggy float sum:", sum_ledger_transactions_buggy(micro_fees))
    print("Fixed Decimal sum:", sum_ledger_transactions_fixed(micro_fees))

import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path
import pytest

# Add exercise directory to sys.path
EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "10.5-root-cause-analysis"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from defect_1 import is_token_expired_fixed, is_token_expired_buggy
from defect_2 import sort_by_priority_fixed, sort_by_priority_buggy
from defect_3 import create_user_profile_fixed, create_user_profile_buggy
from defect_4 import sum_ledger_transactions_fixed, sum_ledger_transactions_buggy
from defect_5 import extract_template_variables_fixed, extract_template_variables_buggy


# =====================================================================
# Defect 1: Timezone Awareness Regression Tests
# =====================================================================

def test_token_expiration_timezone_safe():
    now_utc = datetime.now(timezone.utc)
    active_token = {"expires_at": now_utc + timedelta(hours=2)}
    expired_token = {"expires_at": now_utc - timedelta(seconds=1)}

    assert is_token_expired_fixed(active_token) is False
    assert is_token_expired_fixed(expired_token) is True


# =====================================================================
# Defect 2: Numerical Sorting Regression Tests
# =====================================================================

def test_priority_sorting_numerical():
    items = [
        {"task": "Archival", "priority": "100"},
        {"task": "Security Fix", "priority": "2"},
        {"task": "Minor Bug", "priority": "20"},
        {"task": "Emergency Outage", "priority": "1"},
        {"task": "Routine Cleanup", "priority": "10"},
    ]
    sorted_items = sort_by_priority_fixed(items)
    priorities = [int(i["priority"]) for i in sorted_items]
    assert priorities == [1, 2, 10, 20, 100]


# =====================================================================
# Defect 3: Deep Copy Mutation Isolation Regression Tests
# =====================================================================

def test_user_profile_mutation_isolation():
    u1 = create_user_profile_fixed("user_alice", {"email_alerts": False})
    u2 = create_user_profile_fixed("user_bob", {})

    # Alice opted out; Bob should retain the default True
    assert u1["preferences"]["email_alerts"] is False
    assert u2["preferences"]["email_alerts"] is True
    assert id(u1["preferences"]) != id(u2["preferences"])


# =====================================================================
# Defect 4: Decimal Accounting Precision Regression Tests
# =====================================================================

def test_financial_ledger_no_floating_point_drift():
    # 1,000 transactions of $0.10 each must equal exactly $100.00
    transactions = [0.10] * 1000
    total = sum_ledger_transactions_fixed(transactions)
    assert total == Decimal("100.00")
    assert isinstance(total, Decimal)


# =====================================================================
# Defect 5: Non-Greedy Regex Token Extraction Regression Tests
# =====================================================================

def test_template_variable_extraction_discrete_tokens():
    template = "Invoice for {{customer_name}}: Your total is {{amount_due}} due on {{due_date}}."
    extracted = extract_template_variables_fixed(template)
    assert extracted == ["customer_name", "amount_due", "due_date"]

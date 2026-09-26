import sys
from pathlib import Path
import pytest

# Add exercise directory to sys.path to load modules from folder with dots/hyphens
EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "10.1-debugging-method"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from broken_program_1 import calculate_invoice_buggy, calculate_invoice_fixed
from broken_program_2 import register_user_event_buggy, register_user_event_fixed
from broken_program_3 import (
    transfer_inventory_batch_buggy,
    transfer_inventory_batch_fixed,
    InsufficientStockError,
    InvalidItemError,
)


# =====================================================================
# Program 1 Regression Tests: Invoice Tax Calculation
# =====================================================================

def test_program_1_buggy_overcharges_tax_on_discount():
    items = [
        {"name": "Laptop Stand", "price": 100.0, "quantity": 1},
        {"name": "Mousepad", "price": 40.0, "quantity": 1},
    ]
    # Gross: $140, Discount 20% ($28), Net: $112. Tax rate 10%
    # Buggy computes tax on gross (140 * 0.10 = 14.00), total 126.00
    buggy_res = calculate_invoice_buggy(items, discount_percent=20.0, tax_rate=0.10)
    assert buggy_res["tax_amount"] == 14.00
    assert buggy_res["total"] == 126.00


def test_program_1_fixed_applies_tax_to_net_discounted_amount():
    items = [
        {"name": "Laptop Stand", "price": 100.0, "quantity": 1},
        {"name": "Mousepad", "price": 40.0, "quantity": 1},
    ]
    # Expected: Net $112, Tax $11.20, Total $123.20
    fixed_res = calculate_invoice_fixed(items, discount_percent=20.0, tax_rate=0.10)
    assert fixed_res["gross_subtotal"] == 140.00
    assert fixed_res["discount_amount"] == 28.00
    assert fixed_res["tax_amount"] == 11.20
    assert fixed_res["total"] == 123.20


def test_program_1_fixed_zero_discount_boundary():
    items = [{"name": "Keyboard", "price": 50.0, "quantity": 2}]
    # Gross 100, Discount 0, Net 100, Tax 8% -> 8.00, Total 108.00
    fixed_res = calculate_invoice_fixed(items, discount_percent=0.0, tax_rate=0.08)
    assert fixed_res["tax_amount"] == 8.00
    assert fixed_res["total"] == 108.00


# =====================================================================
# Program 2 Regression Tests: Mutable Default Argument Isolation
# =====================================================================

def test_program_2_buggy_leaks_tags_between_calls():
    # Calling buggy function sequentially without tags causes cross-contamination
    event_a = register_user_event_buggy("user_alice", "login")
    event_b = register_user_event_buggy("user_bob", "logout")
    
    # Buggy version shares the underlying list
    assert "action:login" in event_b["tags"]
    assert event_a["tags"] is event_b["tags"]


def test_program_2_fixed_creates_isolated_tag_lists():
    event_a = register_user_event_fixed("user_carol", "login")
    event_b = register_user_event_fixed("user_dave", "checkout")
    
    assert event_a["tags"] == ["source:api", "action:login"]
    assert event_b["tags"] == ["source:api", "action:checkout"]
    assert event_a["tags"] is not event_b["tags"]


def test_program_2_fixed_does_not_mutate_caller_list():
    caller_tags = ["priority:high"]
    event = register_user_event_fixed("user_eve", "upload", tags=caller_tags)
    
    # Caller tags should not have been mutated in place
    assert caller_tags == ["priority:high"]
    assert event["tags"] == ["priority:high", "source:api", "action:upload"]


# =====================================================================
# Program 3 Regression Tests: Atomic Batch Inventory Transfer
# =====================================================================

def test_program_3_buggy_leaves_corrupted_state_on_partial_failure():
    source = {"ITEM_A": 10, "ITEM_B": 10, "ITEM_C": 2}
    target = {"ITEM_A": 0, "ITEM_B": 0, "ITEM_C": 0}
    
    batch = [
        {"sku": "ITEM_A", "quantity": 5},
        {"sku": "ITEM_B", "quantity": 5},
        {"sku": "ITEM_C", "quantity": 10},  # Fails!
    ]
    
    with pytest.raises(InsufficientStockError):
        transfer_inventory_batch_buggy(source, target, batch)
        
    # Bug: Source and Target were modified for ITEM_A and ITEM_B despite failure
    assert source["ITEM_A"] == 5
    assert target["ITEM_A"] == 5


def test_program_3_fixed_preserves_atomic_integrity_on_failure():
    source = {"ITEM_A": 10, "ITEM_B": 10, "ITEM_C": 2}
    target = {"ITEM_A": 0, "ITEM_B": 0, "ITEM_C": 0}
    initial_source = source.copy()
    initial_target = target.copy()
    
    batch = [
        {"sku": "ITEM_A", "quantity": 5},
        {"sku": "ITEM_B", "quantity": 5},
        {"sku": "ITEM_C", "quantity": 10},  # Fails!
    ]
    
    with pytest.raises(InsufficientStockError):
        transfer_inventory_batch_fixed(source, target, batch)
        
    # Fixed: No partial state mutation occurred
    assert source == initial_source
    assert target == initial_target


def test_program_3_fixed_successful_batch_transfer():
    source = {"ITEM_A": 10, "ITEM_B": 20}
    target = {"ITEM_A": 2, "ITEM_B": 5}
    
    batch = [
        {"sku": "ITEM_A", "quantity": 4},
        {"sku": "ITEM_B", "quantity": 15},
    ]
    
    transfer_inventory_batch_fixed(source, target, batch)
    assert source == {"ITEM_A": 6, "ITEM_B": 5}
    assert target == {"ITEM_A": 6, "ITEM_B": 20}

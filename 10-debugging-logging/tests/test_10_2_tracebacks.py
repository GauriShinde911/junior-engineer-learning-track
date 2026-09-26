import sys
from pathlib import Path
import pytest

# Add exercise directory to sys.path to load modules from folder with dots/hyphens
EXERCISE_DIR = Path(__file__).resolve().parent.parent / "exercises" / "10.2-tracebacks"
if str(EXERCISE_DIR) not in sys.path:
    sys.path.insert(0, str(EXERCISE_DIR))

from traceback_exercises import (
    get_user_primary_email,
    compute_average_metric,
    format_order_summary,
    get_pipeline_stage,
    dispatch_notification,
)


def test_key_error_on_missing_email():
    invalid_profile = {"name": "Alex", "contact": {"phone": "555-0100"}}
    with pytest.raises(KeyError) as exc_info:
        get_user_primary_email(invalid_profile)
    assert "email" in str(exc_info.value)


def test_zero_division_error_on_empty_metrics():
    with pytest.raises(ZeroDivisionError) as exc_info:
        compute_average_metric("cpu_utilization", [])
    assert "division by zero" in str(exc_info.value)


def test_type_error_on_invalid_concatenation():
    with pytest.raises(TypeError) as exc_info:
        format_order_summary("ORD-1001", 12)
    assert "can only concatenate str" in str(exc_info.value)


def test_index_error_on_out_of_bounds_pipeline_stage():
    stages = ["checkout", "payment", "shipment"]
    with pytest.raises(IndexError) as exc_info:
        get_pipeline_stage(stages, 5)
    assert "index out of range" in str(exc_info.value)


def test_attribute_error_on_none_notifier():
    recipient = {"name": "Jordan", "id": "USR-44"}
    with pytest.raises(AttributeError) as exc_info:
        dispatch_notification(recipient, None)
    assert "'NoneType' object has no attribute 'send'" in str(exc_info.value)

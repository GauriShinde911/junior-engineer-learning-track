"""Unit tests for Exercise 9.2 multi-step wizard state machine and validation.

================================================================================
TESTING NOTE: STREAMLIT UI vs. STATE LOGIC
Streamlit form rendering (`st.form`, `st.text_input`, `st.form_submit_button`)
requires an active Streamlit server context. However, the multi-step state machine,
session transitions, and input validation rules are implemented cleanly in the
`RegistrationWizard` class and can be thoroughly unit tested in isolation.
- COVERED: Step-to-step state transitions, input validation algorithms (names,
  email regex, positive costs), data persistence between steps, record storage.
- NOT COVERED: Visual DOM form elements and widget submit event plumbing.
================================================================================
"""

import sys
from pathlib import Path
import pytest

exercise_dir = Path(__file__).resolve().parent.parent / "exercises" / "9.2-forms-state"
sys.path.insert(0, str(exercise_dir))

from app import RegistrationWizard, AssetRegistrationData


@pytest.fixture
def wizard():
    return RegistrationWizard()


def test_wizard_initial_state(wizard):
    """Verifies default starting step and empty model."""
    assert wizard.current_step == RegistrationWizard.STEP_ENTER_DETAILS
    assert wizard.data.asset_name == ""
    assert wizard.registered_records == []


def test_step1_validation_rejects_invalid_inputs(wizard):
    """Verifies that short names, blank departments, and zero/negative costs fail."""
    # Name too short
    valid, msg = wizard.validate_step1("ab", "Engineering", 1000.0)
    assert valid is False
    assert "at least 3 characters" in msg

    # Missing department
    valid, msg = wizard.validate_step1("Server", "", 1000.0)
    assert valid is False
    assert "Department" in msg

    # Negative or zero cost
    valid, msg = wizard.validate_step1("Server", "Engineering", 0.0)
    assert valid is False
    assert "greater than $0.00" in msg


def test_transition_to_step2_persists_data(wizard):
    """Verifies successful transition to step 2 captures input values."""
    success, msg = wizard.transition_to_step2(
        name="Dell Server",
        department="Engineering",
        category="Hardware",
        cost=4500.0
    )
    assert success is True
    assert msg == ""
    assert wizard.current_step == RegistrationWizard.STEP_CONFIRMATION
    assert wizard.data.asset_name == "Dell Server"
    assert wizard.data.department == "Engineering"
    assert wizard.data.estimated_cost == 4500.0


def test_step2_email_validation(wizard):
    """Verifies email regex enforcement."""
    # Advance to step 2 first
    wizard.transition_to_step2("MacBook Pro", "Operations", "Hardware", 2500.0)

    # Invalid emails
    for invalid_email in ["notanemail", "test@", "user@domain", ""]:
        valid, msg = wizard.validate_step2(invalid_email)
        assert valid is False
        assert "valid Approver Email" in msg

    # Valid email
    valid, msg = wizard.validate_step2("approver@company.org")
    assert valid is True
    assert msg == ""


def test_complete_registration_saves_record(wizard):
    """Verifies step 3 completion registers record and moves to completion step."""
    wizard.transition_to_step2("MacBook Pro", "Operations", "Hardware", 2500.0)
    success, msg = wizard.complete_registration(
        approver_email="manager@company.org",
        notes="Urgent developer workstation replacement."
    )
    assert success is True
    assert wizard.current_step == RegistrationWizard.STEP_COMPLETED
    assert len(wizard.registered_records) == 1

    rec = wizard.registered_records[0]
    assert rec["asset_name"] == "MacBook Pro"
    assert rec["approver_email"] == "manager@company.org"
    assert rec["estimated_cost"] == 2500.0


def test_back_navigation_preserves_data(wizard):
    """Verifies navigating back to Step 1 preserves data."""
    wizard.transition_to_step2("Monitor 4K", "Finance", "Hardware", 600.0)
    assert wizard.current_step == RegistrationWizard.STEP_CONFIRMATION

    wizard.back_to_step1()
    assert wizard.current_step == RegistrationWizard.STEP_ENTER_DETAILS
    # Data is not lost
    assert wizard.data.asset_name == "Monitor 4K"
    assert wizard.data.department == "Finance"


def test_reset_wizard_readies_for_new_entry(wizard):
    """Verifies reset resets form inputs while maintaining registered history."""
    wizard.transition_to_step2("Monitor 4K", "Finance", "Hardware", 600.0)
    wizard.complete_registration("lead@company.org", "Approved")

    assert len(wizard.registered_records) == 1
    assert wizard.current_step == RegistrationWizard.STEP_COMPLETED

    wizard.reset()
    assert wizard.current_step == RegistrationWizard.STEP_ENTER_DETAILS
    assert wizard.data.asset_name == ""
    # Registered history remains intact
    assert len(wizard.registered_records) == 1

"""9.2 Streamlit Forms & State — Multi-Step Asset Registration Workflow.

================================================================================
FORMS AND SESSION STATE ARCHITECTURE
================================================================================
1. `st.session_state`:
   A session-scoped dictionary that persists Python objects across script reruns.
   Without `session_state`, any interaction resets all local variables.
2. `st.form`:
   By default, interacting with any input widget triggers an immediate script rerun.
   `st.form` batches inputs together, blocking execution until the user clicks
   `st.form_submit_button`.
3. Callbacks (`on_click`, `on_change`):
   Execute BEFORE the main script reruns from top to bottom, making them ideal
   for state transitions, input validation, and resetting fields.
================================================================================
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Tuple
import streamlit as st


# ==============================================================================
# Pure State Machine & Validation Layer (Testable without Streamlit UI)
# ==============================================================================

@dataclass
class AssetRegistrationData:
    asset_name: str = ""
    department: str = ""
    category: str = "Hardware"
    estimated_cost: float = 0.0
    approver_email: str = ""
    notes: str = ""


class RegistrationWizard:
    """Manages the multi-step state machine and transition validations."""

    STEP_ENTER_DETAILS = 1
    STEP_CONFIRMATION = 2
    STEP_COMPLETED = 3

    def __init__(self) -> None:
        self.current_step: int = self.STEP_ENTER_DETAILS
        self.data: AssetRegistrationData = AssetRegistrationData()
        self.registered_records: List[Dict[str, Any]] = []

    def validate_step1(self, name: str, department: str, cost: float) -> Tuple[bool, str]:
        """Validates basic asset specifications."""
        if not name or len(name.strip()) < 3:
            return False, "Asset Name must be at least 3 characters long."
        if not department or department.strip() == "":
            return False, "Please select a valid Department."
        if cost <= 0:
            return False, "Estimated Cost must be greater than $0.00."
        return True, ""

    def validate_step2(self, email: str) -> Tuple[bool, str]:
        """Validates approver email during confirmation step."""
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not email or not re.match(email_pattern, email.strip()):
            return False, "Please enter a valid Approver Email address."
        return True, ""

    def transition_to_step2(self, name: str, department: str, category: str, cost: float) -> Tuple[bool, str]:
        valid, msg = self.validate_step1(name, department, cost)
        if not valid:
            return False, msg
        self.data.asset_name = name.strip()
        self.data.department = department.strip()
        self.data.category = category
        self.data.estimated_cost = float(cost)
        self.current_step = self.STEP_CONFIRMATION
        return True, ""

    def back_to_step1(self) -> None:
        self.current_step = self.STEP_ENTER_DETAILS

    def complete_registration(self, approver_email: str, notes: str) -> Tuple[bool, str]:
        valid, msg = self.validate_step2(approver_email)
        if not valid:
            return False, msg
        self.data.approver_email = approver_email.strip()
        self.data.notes = notes.strip()

        # Save to records
        self.registered_records.append({
            "asset_name": self.data.asset_name,
            "department": self.data.department,
            "category": self.data.category,
            "estimated_cost": self.data.estimated_cost,
            "approver_email": self.data.approver_email,
            "notes": self.data.notes
        })
        self.current_step = self.STEP_COMPLETED
        return True, ""

    def reset(self) -> None:
        """Resets form wizard for a new registration entry."""
        self.current_step = self.STEP_ENTER_DETAILS
        self.data = AssetRegistrationData()


# ==============================================================================
# UI Presentation Layer
# ==============================================================================

def init_session_state() -> None:
    """Initializes persistent wizard state in st.session_state."""
    if "wizard" not in st.session_state:
        st.session_state.wizard = RegistrationWizard()


def render_step1(wizard: RegistrationWizard) -> None:
    """Renders Step 1: Asset Details using st.form to batch inputs."""
    st.subheader("Step 1 of 3: Enter Asset Specifications")

    with st.form(key="step1_asset_details_form"):
        asset_name = st.text_input(
            "Asset Name / Description *",
            value=wizard.data.asset_name,
            placeholder="e.g. Dell PowerEdge Server Rack 01"
        )

        col1, col2 = st.columns(2)
        departments = ["", "Engineering", "Operations", "Finance", "Security", "Marketing"]
        dept_idx = departments.index(wizard.data.department) if wizard.data.department in departments else 0
        department = col1.selectbox("Department *", options=departments, index=dept_idx)

        categories = ["Hardware", "Software License", "Cloud Infrastructure", "Peripherals"]
        cat_idx = categories.index(wizard.data.category) if wizard.data.category in categories else 0
        category = col2.selectbox("Category", options=categories, index=cat_idx)

        cost = st.number_input(
            "Estimated Cost ($ USD) *",
            min_value=0.0,
            value=float(wizard.data.estimated_cost),
            step=100.0,
            format="%.2f"
        )

        submitted = st.form_submit_button("Next: Review & Approval ➔", use_container_width=True)

        if submitted:
            success, error_msg = wizard.transition_to_step2(asset_name, department, category, cost)
            if success:
                st.rerun()
            else:
                st.error(error_msg)


def render_step2(wizard: RegistrationWizard) -> None:
    """Renders Step 2: Confirmation and Approver Assignment."""
    st.subheader("Step 2 of 3: Confirm Details & Assign Approver")

    # Display read-only summary card
    with st.container(border=True):
        st.markdown("**Review Specified Asset:**")
        col1, col2 = st.columns(2)
        col1.write(f"**Asset:** {wizard.data.asset_name}")
        col1.write(f"**Department:** {wizard.data.department}")
        col2.write(f"**Category:** {wizard.data.category}")
        col2.write(f"**Cost:** ${wizard.data.estimated_cost:,.2f}")

    with st.form(key="step2_confirmation_form"):
        approver = st.text_input(
            "Designated Approver Email *",
            value=wizard.data.approver_email,
            placeholder="manager@company.org"
        )
        notes = st.text_area(
            "Operational Justification / Notes",
            value=wizard.data.notes,
            placeholder="Required for Q4 infrastructure scaling."
        )

        btn_col1, btn_col2 = st.columns(2)
        submit_btn = btn_col2.form_submit_button("Submit Asset Registration ✔", use_container_width=True)

        if submit_btn:
            success, err_msg = wizard.complete_registration(approver, notes)
            if success:
                st.rerun()
            else:
                st.error(err_msg)

    # Back navigation outside form
    if st.button("⬅ Back to Edit Details"):
        wizard.back_to_step1()
        st.rerun()


def render_step3(wizard: RegistrationWizard) -> None:
    """Renders Step 3: Success Confirmation and Registry View."""
    st.success("🎉 Asset successfully registered and submitted for approval!")

    st.subheader("Registered Asset Summary")
    st.json({
        "Asset Name": wizard.data.asset_name,
        "Department": wizard.data.department,
        "Category": wizard.data.category,
        "Cost": f"${wizard.data.estimated_cost:,.2f}",
        "Approver": wizard.data.approver_email,
        "Notes": wizard.data.notes or "N/A"
    })

    if wizard.registered_records:
        st.subheader("All Session Registrations")
        st.dataframe(wizard.registered_records, use_container_width=True)

    if st.button("➕ Register Another Asset", use_container_width=True):
        wizard.reset()
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="Multi-Step Asset Wizard", page_icon="📝")
    st.title("📝 Multi-Step Asset Registration")
    st.caption("Demonstrates persistent session_state, st.form batching, and state machine transitions.")

    init_session_state()
    wizard: RegistrationWizard = st.session_state.wizard

    # Progress bar mapping
    step_progress = {
        RegistrationWizard.STEP_ENTER_DETAILS: 0.33,
        RegistrationWizard.STEP_CONFIRMATION: 0.66,
        RegistrationWizard.STEP_COMPLETED: 1.0
    }
    st.progress(step_progress.get(wizard.current_step, 0.33))

    if wizard.current_step == RegistrationWizard.STEP_ENTER_DETAILS:
        render_step1(wizard)
    elif wizard.current_step == RegistrationWizard.STEP_CONFIRMATION:
        render_step2(wizard)
    elif wizard.current_step == RegistrationWizard.STEP_COMPLETED:
        render_step3(wizard)


if __name__ == "__main__":
    main()

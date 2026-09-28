"""
service.py - Project Records Service Layer

Enforces business rules, project code validation, and coordinates record lifecycle
with deliverable document storage.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from repository import ProjectRecordRepository

PROJECT_CODE_PATTERN = re.compile(r"^PRJ-\d{4}$")
ALLOWED_PHASES = ["Planning", "In Development", "Testing", "Completed", "Archived"]
ALLOWED_DOC_CATEGORIES = ["DesignSpec", "SecurityReview", "AuditLog", "TestReport"]


class ProjectRecordsService:
    """Business service governing engineering project governance in SharePoint."""

    def __init__(self, repository: ProjectRecordRepository):
        self.repository = repository

    def create_project(
        self,
        project_code: str,
        title: str,
        lead_engineer: str,
        start_date: str,
        budget: float = 0.0,
    ) -> Dict[str, Any]:
        """Validate and register a new engineering project record."""
        if not PROJECT_CODE_PATTERN.match(project_code):
            raise ValueError(f"Invalid project code format '{project_code}'. Expected format: PRJ-XXXX")

        if budget < 0:
            raise ValueError("Project budget cannot be negative.")

        # Check for duplicate project code
        existing = self.repository.get_by_project_code(project_code)
        if existing:
            raise ValueError(f"Project with code '{project_code}' already exists.")

        record = {
            "title": title,
            "project_code": project_code,
            "lead_engineer": lead_engineer,
            "start_date": start_date,
            "budget": budget,
            "phase": "Planning",
            "compliance_approved": False,
        }
        return self.repository.save_item(record)

    def upload_deliverable(
        self,
        project_code: str,
        filename: str,
        content: bytes,
        category: str,
    ) -> Dict[str, Any]:
        """Upload a project deliverable document and associate metadata."""
        if category not in ALLOWED_DOC_CATEGORIES:
            raise ValueError(
                f"Invalid document category '{category}'. Allowed: {ALLOWED_DOC_CATEGORIES}"
            )

        project = self.repository.get_by_project_code(project_code)
        if not project:
            raise ValueError(f"Project '{project_code}' does not exist.")

        metadata = {
            "ProjectCode": project_code,
            "DocCategory": category,
            "SignoffStatus": "Pending",
        }
        folder = f"{project_code}/{category.lower()}s"

        return self.repository.store_document(
            filename=filename,
            content=content,
            folder_path=folder,
            metadata=metadata,
        )

    def advance_phase(self, project_code: str, next_phase: str) -> Dict[str, Any]:
        """Transition project to the next operational phase."""
        if next_phase not in ALLOWED_PHASES:
            raise ValueError(f"Invalid phase '{next_phase}'. Allowed: {ALLOWED_PHASES}")

        project = self.repository.get_by_project_code(project_code)
        if not project:
            raise ValueError(f"Project '{project_code}' not found.")

        # Ensure completed/archived projects require compliance approval
        if next_phase in ("Completed", "Archived") and not project.get("compliance_approved"):
            raise ValueError(
                f"Cannot advance to '{next_phase}': project '{project_code}' lacks compliance approval."
            )

        updated_fields = {"phase": next_phase}
        return self.repository.save_item(updated_fields, item_id=project["id"])

    def approve_compliance(self, project_code: str) -> Dict[str, Any]:
        """Mark a project as compliance approved."""
        project = self.repository.get_by_project_code(project_code)
        if not project:
            raise ValueError(f"Project '{project_code}' not found.")

        return self.repository.save_item(
            {"compliance_approved": True}, item_id=project["id"]
        )

    def get_project_summary(self, project_code: str) -> Dict[str, Any]:
        """Retrieve project record details."""
        project = self.repository.get_by_project_code(project_code)
        if not project:
            raise ValueError(f"Project '{project_code}' not found.")
        return project

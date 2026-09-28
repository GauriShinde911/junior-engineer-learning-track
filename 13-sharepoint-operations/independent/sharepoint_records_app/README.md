# Independent Project: Engineering Project Records App

A complete, domain-driven SharePoint records and deliverables management system implementing full CRUD, document archival, and compliance governance.

---

## 1. Overview

This project provides an automated lifecycle management service for corporate engineering projects. It tracks project milestones, budgets, and compliance approval states in a SharePoint List (`ProjectRecords`) while organizing binary deliverable documents (specifications, security reviews, test reports) within a SharePoint Document Library (`ProjectDeliverables`).

---

## 2. Architecture & File Structure

```text
sharepoint_records_app/
├── SCHEMA_SPEC.md              # Target SharePoint list and library specification
├── repository.py               # Concrete repository implementing SharePointRepositoryInterface
├── service.py                  # Domain service enforcing business validation and phase rules
├── test_repository_mocked.py   # Mocked unit tests for CRUD, deliverables, and error paths
└── README.md                   # This document (usage and testing guide)
```

---

## 3. Running Unit Tests

To run the full suite of mocked integration tests:

```bash
python -m pytest 13-sharepoint-operations/independent/sharepoint_records_app/test_repository_mocked.py -v
```

All tests execute against mocked Microsoft Graph API responses, verifying business logic, validation rules, and document metadata preservation with zero network or Azure credentials required.

---

## 4. Usage Example (Python Service API)

```python
from repository import ProjectRecordRepository
from service import ProjectRecordsService
from list_item_client import SharePointListItemClient
from document_client import SharePointDocumentClient

# Initialize clients (with credentials from .env)
list_client = SharePointListItemClient(
    tenant_id="<tenant_id>", client_id="<client_id>", client_secret="<secret>"
)
doc_client = SharePointDocumentClient(
    tenant_id="<tenant_id>", client_id="<client_id>", client_secret="<secret>"
)

repo = ProjectRecordRepository(
    site_id="<site_id>",
    list_id="<list_id>",
    drive_id="<drive_id>",
    list_client=list_client,
    doc_client=doc_client,
)
service = ProjectRecordsService(repository=repo)

# 1. Create a project
project = service.create_project(
    project_code="PRJ-1044",
    title="Autonomous Robotics Core",
    lead_engineer="lead@company.com",
    start_date="2026-10-01",
    budget=50000.0,
)

# 2. Upload a design deliverable
with open("robotics_spec.pdf", "rb") as f:
    service.upload_deliverable(
        project_code="PRJ-1044",
        filename="robotics_spec.pdf",
        content=f.read(),
        category="DesignSpec",
    )

# 3. Approve compliance and complete project
service.approve_compliance("PRJ-1044")
service.advance_phase("PRJ-1044", "Completed")
```

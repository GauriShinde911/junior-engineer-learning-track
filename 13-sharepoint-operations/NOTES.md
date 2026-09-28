# Skill 13: SharePoint Operations

## Overview
This skill covers interacting with Microsoft SharePoint as an external enterprise data and document management platform. It treats SharePoint not as an end-user web application, but as a cloud data store and content repository accessible programmatically via the Microsoft Graph REST API and modern Azure Active Directory (Entra ID) authentication.

> **Curriculum Mapping Note**: This folder corresponds to **Section 9 ("SharePoint Operations")** of the source curriculum PDF. Because folders `01-python-fundamentals` through `12-documentation` were already sequenced and established in this repository, this topic is numbered locally as **`13-sharepoint-operations`** to preserve repo progression.

---

## Subsection Map and Index

| Section | Topic | Summary | Reference |
|---|---|---|---|
| **13.1** | [Concepts](exercises/13.1-concepts/NOTES.md) | SharePoint object hierarchies (Sites, Lists, Libraries, Columns, Views) and architectural mapping. | [13.1 NOTES.md](exercises/13.1-concepts/NOTES.md) |
| **13.2** | [Data Operations](exercises/13.2-data-operations/NOTES.md) | Graph API list item CRUD, OData filtering, and internal vs display name field mapping. | [13.2 NOTES.md](exercises/13.2-data-operations/NOTES.md) |
| **13.3** | [Document Operations](exercises/13.3-document-operations/NOTES.md) | DriveItem binary uploads/downloads, folder creation, and two-phase metadata preservation. | [13.3 NOTES.md](exercises/13.3-document-operations/NOTES.md) |
| **13.4** | [Integration Layer](exercises/13.4-integration-layer/NOTES.md) | Abstract repository contracts (ABC), concrete Graph implementation, and decoupled domain services. | [13.4 NOTES.md](exercises/13.4-integration-layer/NOTES.md) |
| **13.5** | [Permissions & Failures](exercises/13.5-permissions-failures/NOTES.md) | Least privilege (`Sites.Selected`), simulating 403 Forbidden, 429 Throttling, and network drops. | [13.5 NOTES.md](exercises/13.5-permissions-failures/NOTES.md) |
| **Independent** | [Records App](independent/sharepoint_records_app/README.md) | Autonomous implementation of an engineering project records and deliverable submission system. | [Project README](independent/sharepoint_records_app/README.md) |

---

## Testing & Live Site Verification
- **Automated Tests**: All client, repository, and service classes have comprehensive unit test suites using `pytest-mock` to mock Microsoft Graph API responses. Zero live cloud credentials are required to run automated tests.
- **Live Validation**: To validate against a real Microsoft 365 tenant, follow the instructions in [MANUAL_STEPS.md](MANUAL_STEPS.md).

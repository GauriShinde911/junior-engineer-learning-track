# 13. SharePoint Operations

## Overview
Interacting with Microsoft SharePoint as an external enterprise data and document platform using Microsoft Graph REST APIs, MSAL authentication, field mapping, document lifecycle management, and repository abstractions.

---

## Folder Structure

```text
13-sharepoint-operations/
├── exercises/          <- Guided practice modules (13.1 through 13.5)
├── independent/        <- Project records challenge application
├── MANUAL_STEPS.md     <- Guide for live validation against a real SharePoint site
├── requirements.txt    <- Dependencies (requests, msal, pytest-mock, python-dotenv)
├── .env.example        <- Environment variable template
└── README.md           <- Overview & instructions
```

---

## Instructions

1. **Guided Exercises (`exercises/`)**:
   - `13.1-concepts`: Structural objects, training site specification, and object mapping guide.
   - `13.2-data-operations`: Graph API client for list CRUD, OData filtering, and field mapping.
   - `13.3-document-operations`: Uploading/downloading files, folder creation, and metadata preservation.
   - `13.4-integration-layer`: Abstract repository contract, concrete implementation, and service layer.
   - `13.5-permissions-failures`: Simulating 403 Forbidden, 429 Throttling, and network failure modes.

2. **Independent Challenge (`independent/`)**:
   - `sharepoint_records_app`: Complete engineering project records and deliverable submission service built against `SCHEMA_SPEC.md`.

3. **Testing**:
   Run all mocked unit tests:
   ```bash
   pytest 13-sharepoint-operations/
   ```

# SharePoint Schema Specification: Engineering Project Records App

This specification document outlines the list and document library requirements for the Engineering Project Records System (`ProjectRecordsApp`).

---

## 1. List Schema: `ProjectRecords`

**Purpose**: Maintains corporate engineering project registrations, budgets, and compliance milestones.

### Column Definitions
| Display Name | Internal Name | Type | Required | Constraints / Allowed Choices |
|---|---|---|---|---|
| Project Title | `Title` | Single line of text | Yes | Max 255 characters |
| Project Code | `ProjectCode` | Single line of text | Yes | Enforce unique, regex: `^PRJ-\d{4}$` (e.g. `PRJ-2026`) |
| Lead Engineer | `LeadEngineer` | Single line of text | Yes | Engineer email or corporate UPN |
| Total Budget | `Budget` | Currency | No | USD, non-negative, default: `0.00` |
| Project Phase | `Phase` | Choice | Yes | `Planning`, `In Development`, `Testing`, `Completed`, `Archived` (Default: `Planning`) |
| Start Date | `StartDate` | Date and Time | Yes | ISO Date (`YYYY-MM-DD`) |
| Compliance Approved | `ComplianceApproved` | Yes/No (Boolean) | No | Default: `No` |

---

## 2. Document Library: `ProjectDeliverables`

**Purpose**: Stores engineering design documents, audit certifications, and test reports organized by project.

### Directory Organization
```text
ProjectDeliverables/
└── {ProjectCode}/
    ├── specifications/
    ├── compliance/
    └── test_reports/
```

### Custom Document Metadata
| Display Name | Internal Name | Type | Required | Choices / Description |
|---|---|---|---|---|
| Associated Project | `ProjectCode` | Single line of text | Yes | Foreign key reference matching `ProjectRecords.ProjectCode` |
| Document Category | `DocCategory` | Choice | Yes | Choices: `DesignSpec`, `SecurityReview`, `AuditLog`, `TestReport` |
| Signoff Status | `SignoffStatus` | Choice | Yes | Choices: `Pending`, `Approved`, `Rejected` (Default: `Pending`) |

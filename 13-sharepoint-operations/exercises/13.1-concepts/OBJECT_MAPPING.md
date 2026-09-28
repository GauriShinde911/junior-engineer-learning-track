# SharePoint Object Mapping Guide

A practical engineering reference for choosing the correct SharePoint structural object based on operational and architectural requirements.

---

## 1. Quick-Reference: SharePoint Structural Objects

| Object Type | Primary Purpose | When to Choose | Common Anti-Pattern |
|---|---|---|---|
| **Site Collection / Site** | Security, governance, and administration boundary. | High-level business division, distinct external team access, or distinct storage quotas. | Creating a new site for every small project or sub-folder. |
| **SharePoint List** | Tabular relational/structured records (non-binary metadata). | Storing entity records, task items, asset logs, lookup tables (akin to a relational database table). | Uploading Excel spreadsheets to track tabular rows manually. |
| **Document Library** | Binary file storage enriched with columnar metadata and versioning. | Storing PDFs, Word documents, images, code tarballs, configuration snapshots. | Using regular lists with attachments when documents require independent lifecycles. |
| **Column / Field** | Typed attribute defining a single data point on a list or library item. | Enforcing schema typing (Text, Choice, Currency, Person, Lookup). | Stuffing multiple delimited values into a single freeform text column. |
| **View** | Saved query defining filtering, sorting, grouping, and visible columns. | Giving different user personas tailored perspectives on the same underlying dataset. | Creating separate duplicate lists just to view subsets of data. |
| **Folder** | Physical filesystem-like containment inside a document library. | Managing bulk inherited permissions or matching legacy directory structures. | Using 6+ nested folder levels instead of searchable metadata columns. |
| **Permission Level / Group** | Access control definitions (Read, Edit, Full Control). | Enforcing role-based access control (RBAC) across sites, lists, or folders. | Granting direct ad-hoc user permissions to individual list items. |

---

## 2. Requirement → Object Mapping Examples

### Scenario 1: Tracking Hardware Asset Records
- **Business Requirement**: The IT team needs to track 5,000 laptops, including serial number, assigned owner, purchase price, and warranty expiration.
- **Selected Object**: **SharePoint List** with custom columns (`Single line of text`, `Person`, `Currency`, `Date`).
- **Rationale**: The data is purely structured metadata without distinct attached files. A SharePoint List provides relational filtering, indexing on `SerialNumber`, and programmatic REST/Graph API CRUD.

### Scenario 2: Archiving Vendor PDF Contracts with Signing Dates
- **Business Requirement**: Legal must store signed vendor contracts in PDF format, categorized by vendor name and contract expiration date, with audit logging.
- **Selected Object**: **Document Library** with custom metadata columns (`VendorName` [Choice], `ContractExpiry` [Date]).
- **Rationale**: Contracts are binary files requiring automatic major/minor version history, check-in/check-out locks, and document-level search indexing.

### Scenario 3: Separating Internal R&D Files from External Contractor View
- **Business Requirement**: External contract developers need access to project specifications, but must never view internal patent filings or payroll rates.
- **Selected Object**: **Site Collection** (or separate dedicated Document Library with unique permission inheritance).
- **Rationale**: Cleanest security boundary. Sub-item permission breaking is notoriously fragile; separating sensitive domains into distinct sites guarantees zero leakage via search or shared group memberships.

### Scenario 4: Presenting "Only Critical Tickets Assigned to Me"
- **Business Requirement**: Technicians need an immediate dashboard showing open repairs assigned specifically to the logged-in engineer.
- **Selected Object**: **SharePoint View** with dynamic filter (`AssignedTo` equals `[Me]` AND `Status` not equal `Closed`).
- **Rationale**: A view alters how existing data is queried and rendered without duplicating records or executing custom client-side code.

### Scenario 5: Storing Hierarchical Architecture Blueprints by System
- **Business Requirement**: Engineering teams maintain hundreds of CAD diagrams organized by physical facility building and floor level.
- **Selected Object**: **Document Library with 2-level Folders** (`/Building-A/Floor-1/`) supplemented by `SystemType` metadata.
- **Rationale**: Combines intuitive directory browsing for engineers dragging files from desktops with metadata filtering for API search automation.

### Scenario 6: Enforcing Standard Document Headers & Metadata Across Multiple Libraries
- **Business Requirement**: Standard Operating Procedures (SOPs) across five different departmental sites must always include `ReviewCycle`, `ApprovedBy`, and `EffectiveDate`.
- **Selected Object**: **Site Content Type** (published via Content Type Hub).
- **Rationale**: Defines a centralized schema template that can be subscribed to by multiple libraries across the tenant, ensuring schema consistency.

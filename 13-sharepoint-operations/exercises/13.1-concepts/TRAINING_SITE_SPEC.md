# SharePoint Training Site Specification

**Site Name**: Engineering Operations Hub (`EngOpsHub`)  
**Template**: Team Site (Microsoft 365 connected group, private)  
**Target URL**: `https://<tenant>.sharepoint.com/sites/EngOpsHub`  
**Purpose**: Centralized training workspace for asset tracking, engineering maintenance logs, and technical documentation management.

---

## 1. Site Structure & Permissions

### Permission Groups
| Group Name | Permission Level | Membership / Role |
|---|---|---|
| `EngOpsHub Owners` | Full Control | Site administrators, DevOps lead |
| `EngOpsHub Members` | Edit (Contribute + list edit) | Active engineers, operational technicians |
| `EngOpsHub Visitors` | Read | Internal auditors, executive stakeholders |

*Note: Broken permission inheritance is disabled at the site root. Sub-level libraries inherit permissions by default, with custom item-level ACLs applied only to restricted contracts.*

---

## 2. SharePoint Lists Specification

### 2.1 List: `HardwareAssets`
Tracks physical and virtual hardware allocated to engineering personnel.

#### Columns
| Display Name | Internal Name | Type | Required | Settings / Constraints |
|---|---|---|---|---|
| Asset Title | `Title` | Single line of text | Yes | Max 255 chars (e.g. "MacBook Pro M3 Max 16-inch") |
| Asset Tag | `AssetTag` | Single line of text | Yes | Enforce unique values, format: `ENG-HW-\d{5}` |
| Category | `Category` | Choice | Yes | Choices: `Laptop`, `Workstation`, `Server`, `Networking`, `Peripherals` |
| Purchase Date | `PurchaseDate` | Date and Time | Yes | Date only |
| Purchase Cost | `PurchaseCost` | Currency | No | Currency format: USD, 2 decimal places |
| Status | `Status` | Choice | Yes | Choices: `In Service`, `In Maintenance`, `Decommissioned`, `Reserved` (Default: `In Service`) |
| Assigned To | `AssignedTo` | Person or Group | No | Single selection, Show field: Name |
| Serial Number | `SerialNumber` | Single line of text | Yes | Enforce unique values |

#### Views
1. **All Assets (Default)**: Shows all columns sorted by `AssetTag` ascending.
2. **Active Laptops & Workstations**:
   - Filter: `Category` equals `Laptop` OR `Category` equals `Workstation` AND `Status` equals `In Service`.
   - Sort: `AssignedTo` ascending.
3. **Pending Maintenance**:
   - Filter: `Status` equals `In Maintenance`.

---

### 2.2 List: `MaintenanceLog`
Captures hardware repairs, maintenance requests, and technician sign-offs.

#### Columns
| Display Name | Internal Name | Type | Required | Settings / Constraints |
|---|---|---|---|---|
| Ticket Summary | `Title` | Single line of text | Yes | Short title of repair |
| Ticket ID | `TicketID` | Single line of text | Yes | Unique index, format: `MAINT-\d{6}` |
| Related Asset | `AssetLookup` | Lookup | Yes | Source list: `HardwareAssets`, Target column: `AssetTag` |
| Severity | `Severity` | Choice | Yes | Choices: `Low`, `Medium`, `High`, `Critical` |
| Reported Date | `ReportedDate` | Date and Time | Yes | Date and Time (default: `[Today]`) |
| Issue Details | `IssueDetails` | Multiple lines of text | Yes | Plain text |
| Resolved | `Resolved` | Yes/No (Boolean) | No | Default: `No` |
| Technician | `Technician` | Person or Group | No | Single selection |

#### Views
1. **Open Critical Incidents**:
   - Filter: `Resolved` equals `No` AND `Severity` equals `Critical`.
   - Sort: `ReportedDate` descending.

---

## 3. Document Libraries Specification

### Library: `EngineeringManuals`
Stores technical operational manuals, architecture diagrams, and hardware specification sheets.

#### Custom Metadata Columns
| Display Name | Internal Name | Type | Required | Settings / Constraints |
|---|---|---|---|---|
| Manual Version | `ManualVersion` | Single line of text | Yes | Semantic version (e.g. `1.2.0`) |
| Manufacturer | `Manufacturer` | Choice | Yes | Choices: `Apple`, `Dell`, `Cisco`, `Supermicro`, `Internal` |
| Security Classification | `SecurityClassification` | Choice | Yes | Choices: `Public`, `Internal Engineering`, `Confidential` |
| Document Owner | `DocOwner` | Person or Group | Yes | Single selection |

#### Folder Hierarchy
```text
EngineeringManuals/
├── Hardware/
│   ├── Apple/
│   ├── Dell/
│   └── NetworkGear/
├── Runbooks/
│   ├── ProductionServices/
│   └── DisasterRecovery/
└── VendorAgreements/       (Restricted to Owners group)
```

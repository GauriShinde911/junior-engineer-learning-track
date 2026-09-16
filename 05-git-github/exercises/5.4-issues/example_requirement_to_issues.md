# Example: Decomposing a Business Requirement into Actionable GitHub Issues

This document illustrates how a junior software engineer translates a vague business request from product managers into well-scoped, unambiguous engineering tasks using vertical slicing and clear acceptance criteria.

---

## The Raw High-Level Requirement
> *"Our operations managers need to export filtered inventory records into Excel and CSV spreadsheets directly from the dashboard so they can share stock counts with suppliers and accounting."*

---

## Decomposed GitHub Issues

### Issue #1: [Backend] Build CSV Export Streaming Service
- **Type**: `enhancement`, `backend`
- **Estimate**: 1 day

#### User Story
**As an** operations team member  
**I want** to download inventory items formatted as a standardized CSV file  
**So that** I can import stock counts into spreadsheets and external accounting software.

#### Acceptance Criteria
- [ ] Implement `export_inventory_csv(items: list[dict], output_stream)` in `exports/csv_exporter.py`.
- [ ] Columns included in order: `id`, `sku`, `name`, `category`, `quantity`, `unit_price`, `total_valuation`.
- [ ] Currency values formatted as two decimal places (`#.00`).
- [ ] Handles commas and quotes in product names cleanly using Python's standard `csv` library.
- [ ] Unit tests verify proper header generation, data formatting, and empty dataset handling.

#### Implementation Notes
- Use Python's built-in `csv.writer` with `io.StringIO` to enable memory-efficient stream generation.

---

### Issue #2: [Backend] Implement Multi-Sheet Excel Report Generator
- **Type**: `enhancement`, `backend`
- **Estimate**: 2 days

#### User Story
**As an** executive manager  
**I want** to download a formatted `.xlsx` workbook with both raw data and category pivot summaries  
**So that** I can present inventory valuations in weekly financial syncs.

#### Acceptance Criteria
- [ ] Implement `build_excel_inventory_report(items: list[dict], output_path: Path) -> Path` in `exports/excel_exporter.py`.
- [ ] Sheet 1 (`"Inventory Details"`): Formatted table with dark blue headers, zebra striping, currency formatting on price/valuation columns, and frozen top row.
- [ ] Sheet 2 (`"Category Summary"`): Aggregate table showing `category`, `total_items`, `total_units`, and `total_value`.
- [ ] Auto-fit column widths based on maximum string lengths.
- [ ] Unit tests verify workbook creation, sheet names, and cell values using `openpyxl`.

#### Implementation Notes
- Use `openpyxl` for workbook generation and styling. Do not require LibreOffice or Excel installed on server.

---

### Issue #3: [API] Add Export Endpoints with Filter Query Parameters
- **Type**: `feature`, `api`
- **Estimate**: 1-2 days

#### User Story
**As an** API client  
**I want** dedicated HTTP endpoints `/api/v1/inventory/export?format={csv|xlsx}&category={cat}&min_stock={n}`  
**So that** users can trigger downloads based on their active dashboard filters.

#### Acceptance Criteria
- [ ] Add route `GET /api/v1/inventory/export` accepting query params: `format` (required: `csv` or `xlsx`), `category` (optional), `min_stock` (optional), `max_stock` (optional).
- [ ] Returns HTTP 400 Bad Request with clear JSON error if `format` is not in `['csv', 'xlsx']`.
- [ ] Sets appropriate HTTP headers:
  - CSV: `Content-Type: text/csv`, `Content-Disposition: attachment; filename="inventory_YYYYMMDD.csv"`
  - Excel: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `Content-Disposition: attachment; filename="inventory_YYYYMMDD.xlsx"`
- [ ] Integration tests verify parameter validation, error responses, and HTTP response headers.

#### Implementation Notes
- Reuse existing filter logic from `AssetRepository.search()`.

---

### Issue #4: [Observability] Add Audit Logging for Export Actions
- **Type**: `security`, `observability`
- **Estimate**: 0.5 days

#### User Story
**As a** compliance officer  
**I want** every data export event logged with user ID, timestamp, export format, and row count  
**So that** we maintain audit trails for sensitive commercial data downloads.

#### Acceptance Criteria
- [ ] Emit structured JSON log event `INVENTORY_DATA_EXPORTED` upon successful download generation.
- [ ] Log entry includes: `timestamp`, `user_id`, `client_ip`, `format`, `row_count`, `elapsed_ms`.
- [ ] Unit test verifies logger is called with expected telemetry fields on export completion.

---

## Why This Breakdown Works

1. **Independent & Testable**: Issue #1 and Issue #2 can be built and tested completely in parallel by different engineers.
2. **Clear Boundaries**: The API routing (Issue #3) depends on exporter interfaces, keeping business logic strictly decoupled from HTTP transport.
3. **No Hidden Assumptions**: A junior engineer can pick up any of these issues and immediately know when their task is finished by reviewing the acceptance criteria checkboxes.

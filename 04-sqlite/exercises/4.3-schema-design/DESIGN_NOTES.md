# Schema Design Justification: E-Commerce & Order Management

This document details the architectural rationale, entity boundaries, referential constraints, and indexing strategy applied in `schema.sql`.

---

## 1. Normalization & Entity Boundaries

The schema achieves Third Normal Form (3NF) to eliminate data redundancy and prevent update/delete anomalies:

- **Customers**: Contains only buyer identity information (`email`, `full_name`, `phone`, `tier`). If a customer updates their phone number or tier, it is modified in a single row without touching historical orders.
- **Orders**: Represents the transactional event header (`order_number`, `customer_id`, `status`, `total_amount`). It stores no customer names or product descriptions, only the `customer_id` foreign key.
- **Order Items**: Resolves the 1-to-many relationship between orders and purchased items. Each row represents a specific line item with frozen historical pricing (`unit_price` at the exact moment of sale).

---

## 2. Primary & Foreign Keys Rationale

| Table | Primary Key | Foreign Key | Constraint Behavior | Rationale |
|---|---|---|---|---|
| `customers` | `id` (INTEGER AUTOINCREMENT) | - | - | Surrogate key provides lightweight 64-bit integer IDs for relational joins. |
| `orders` | `id` (INTEGER AUTOINCREMENT) | `customer_id` -> `customers(id)` | `ON DELETE RESTRICT` | Prevents deleting customer accounts that have associated financial order records (audit compliance). |
| `order_items` | `id` (INTEGER AUTOINCREMENT) | `order_id` -> `orders(id)` | `ON DELETE CASCADE` | Line items have no independent identity outside their parent order; deleting a draft/cancelled order removes its items. |

---

## 3. Data Integrity & Constraints

- **Unique Constraints**:
  - `customers.email`: Prevents duplicate account creation.
  - `orders.order_number`: Protects against duplicate invoice generation across distributed workers.
- **Check Constraints**:
  - `order_items.quantity > 0`: Prevents invalid, negative, or zero quantity orders.
  - `orders.status IN ('pending', 'processing', 'completed', 'cancelled')`: Restricts status values to a validated finite state machine.
- **Generated Column (`line_total`)**:
  - Defined as `REAL GENERATED ALWAYS AS (quantity * unit_price) STORED`.
  - Guarantees arithmetic consistency without requiring manual application calculation or risk of human error.

---

## 4. Indexing Strategy & Tradeoffs

Indexes introduce write overhead during inserts and updates, so each index must be justified by high-frequency query patterns:

1. `idx_orders_customer_id`:
   - **Use Case**: Queries fetching customer purchase histories (`WHERE customer_id = ?`).
   - **Impact**: Replaces full table scans with logarithmic B-Tree lookups ($O(\log N)$).
2. `idx_orders_status`:
   - **Use Case**: Fulfillment worker dashboards polling pending orders (`WHERE status = 'pending'`).
3. `idx_order_items_order_id`:
   - **Use Case**: Joining orders with line items during order details rendering.
4. `idx_order_items_sku`:
   - **Use Case**: Inventory reorder reports aggregating sales by SKU over time.

---

## 5. Audit Timestamps

All core tables include `created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP` and `updated_at`. This provides fundamental observability for tracking record aging, diagnosing transaction lag, and supporting future data replication or incremental syncing.

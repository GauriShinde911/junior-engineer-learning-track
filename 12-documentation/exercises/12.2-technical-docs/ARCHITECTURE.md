# System Architecture Document: Order Processing & Notification Pipeline

This document provides a technical design overview of the Order Processing and Notification Pipeline (`order-pipeline`). It describes the system architecture, component boundaries, data flow, dependencies, and key engineering trade-offs.

---

## 1. System Overview

The Order Processing & Notification Pipeline is an internal backend service responsible for validating incoming customer purchase requests, persisting finalized transactions, and dispatching asynchronous confirmation notifications.

### High-Level Architecture

```text
[ Client Applications ]
          │  (HTTP / JSON)
          ▼
┌────────────────────────────────────────────────────────┐
│                   Ingestion Gateway                    │
│   • Request parsing & schema validation               │
│   • Authentication & rate limiting                     │
└─────────────────────────┬──────────────────────────────┘
                          │ Validated Payload
                          ▼
┌────────────────────────────────────────────────────────┐
│                   Order Core Service                   │
│   • Inventory availability verification                │
│   • Pricing calculation & tax computation              │
│   • State transition management (PENDING -> PLACED)    │
└───────────────┬──────────────────────────┬─────────────┘
                │                          │
   Order Record │                          │ Emitted Event
                ▼                          ▼
┌─────────────────────────┐   ┌──────────────────────────┐
│      Order Storage      │   │    Event Message Bus     │
│   • Primary transactional│   │   • In-memory / Redis    │
│     datastore (Postgres)│   │     pub-sub channel      │
└─────────────────────────┘   └────────────┬─────────────┘
                                           │
                                           ▼
                              ┌──────────────────────────┐
                              │  Notification Worker     │
                              │   • Email/SMS formatting │
                              │   • Idempotent delivery  │
                              └──────────────────────────┘
```

---

## 2. Component Breakdown & Responsibilities

| Component | Module / Service | Responsibilities | Failure Boundary |
|---|---|---|---|
| **Ingestion Gateway** | `gateway/router.py` | Validates HTTP headers, parses JSON request bodies against JSONSchema, rejects malformed payloads with HTTP 400. | Stateless. Crashes or reboots do not cause data loss. |
| **Order Core** | `core/processor.py` | Enforces business rules (e.g. stock limits, promotional codes), calculates totals, writes transactional state to DB. | Synchronous processing. Unhandled exceptions roll back database transactions. |
| **Persistence Layer** | `db/repository.py` | Handles database connections, query execution, connection pooling, and optimistic concurrency locks. | Backed by Postgres with transactional isolation level `READ COMMITTED`. |
| **Event Bus** | `events/publisher.py` | Decouples order completion from downstream actions by publishing `OrderPlacedEvent` payloads. | Non-blocking. If event bus is unreachable, order is persisted and marked for outbox retry. |
| **Notification Worker**| `workers/notify.py` | Consumes events, renders localized notification templates, and communicates with external email/SMS providers. | Asynchronous. Downstream provider outages are isolated; retries use exponential backoff. |

---

## 3. End-to-End Data Flow

1. **Submission**: A client submits a `POST /api/v1/orders` request containing customer ID, line items, and payment token.
2. **Ingestion Validation**: The Ingestion Gateway validates field data types, required keys, and payload constraints.
3. **Core Processing**:
   - The Core Service queries inventory for availability.
   - Calculates itemized subtotal, discounts, and regional taxes.
4. **Atomic Persistence**:
   - Inside an atomic database transaction, the order record is inserted with status `PLACED`, inventory balances are decremented, and an outbox event record is created.
5. **Event Emission**: The event publisher broadcasts `OrderPlacedEvent` (containing `order_id`, `customer_id`, `total_cents`, `timestamp`).
6. **Async Delivery**: The Notification Worker picks up the event, formats an email receipt, and dispatches it via SMTP.
7. **Client Response**: The HTTP client receives a synchronous `201 Created` response containing the generated `order_id` and order summary.

---

## 4. Technology Stack & Dependencies

- **Language / Runtime**: Python 3.11+
- **HTTP Layer**: FastAPI / ASGI (uvicorn)
- **Data Persistence**: PostgreSQL (SQLAlchemy ORM + Alembic migrations)
- **Asynchronous Task Queue**: Redis + Celery / RQ
- **Validation**: Pydantic v2

---

## 5. Key Architectural Decisions & Rationale

### Decision 1: Transactional Outbox Pattern for Notifications
- **Context**: When an order is placed, an email notification must be sent. Directly calling external email APIs inside the HTTP request handler introduces unacceptable latency and risks dual-write inconsistencies (e.g. DB commit fails after email is sent, or email fails after DB commit).
- **Decision**: The Core Service writes the order and an outbox event into the same relational database transaction. A separate asynchronous worker polls or streams from the outbox to dispatch notifications.
- **Trade-off**: Increases database write volume slightly and adds minor delivery latency (sub-second), but guarantees that no customer receives an email for a failed order and no placed order fails to trigger a receipt.

### Decision 2: Optimistic Locking for Inventory Decrements
- **Context**: Multiple concurrent requests may attempt to purchase the last unit of an inventory item.
- **Decision**: Use database row versioning (`WHERE version = :expected_version`) rather than heavy pessimistic table locks (`SELECT ... FOR UPDATE`).
- **Trade-off**: High-contention flash sales may result in occasional retry cycles on conflict, but general throughput is significantly higher and avoids thread pool starvation.

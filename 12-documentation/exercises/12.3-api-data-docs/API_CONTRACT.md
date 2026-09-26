# API Contract: Subscription & Billing Management Service

**Version**: `1.0.0`  
**Base URL**: `https://api.billing.internal.acme.com/v1`  
**Protocol**: HTTPS / REST  
**Authentication**: Bearer Token via standard HTTP Header: `Authorization: Bearer <API_TOKEN>`

---

## 1. Global Conventions

### Common Request Headers
| Header | Type | Required | Description |
|---|---|---|---|
| `Authorization` | String | Yes | `Bearer <JWT_OR_API_KEY>` |
| `Content-Type` | String | Conditional | `application/json` (required on POST, PUT, PATCH) |
| `X-Request-ID` | String (UUIDv4) | Optional | Client correlation ID for distributed tracing |

### Standard Error Response Format
All `4xx` and `5xx` error responses adhere to the RFC 7807 problem details specification:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested subscription ID was not found.",
    "status": 404,
    "timestamp": "2026-09-26T14:15:00Z",
    "details": [
      {
        "field": "subscription_id",
        "issue": "No active or cancelled subscription matches 'sub_99999'."
      }
    ]
  }
}
```

---

## 2. Endpoints

### 2.1 Create Subscription

Creates a recurring billing subscription for an existing customer account.

- **Method**: `POST`
- **Path**: `/subscriptions`

#### Request Payload Schema
```json
{
  "customer_id": "cust_8281a9",
  "plan_id": "plan_pro_monthly",
  "payment_method_id": "pm_tok_visa_4242",
  "billing_cycle_anchor": "immediate",
  "auto_renew": true,
  "promo_code": "AUTUMN2026"
}
```

#### Request Field Definitions
| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `customer_id` | String | Yes | Prefix `cust_`, alphanumeric | Unique identifier of the verified customer |
| `plan_id` | String | Yes | Enum: `plan_starter_monthly`, `plan_pro_monthly`, `plan_enterprise_annual` | Tier package identifier |
| `payment_method_id`| String | Yes | Prefix `pm_` | Pre-validated tokenized payment instrument |
| `billing_cycle_anchor` | String | No | Enum: `immediate`, `next_month_first` (Default: `immediate`) | When initial billing occurs |
| `auto_renew` | Boolean| No | Default: `true` | Automatic recurring renewal flag |
| `promo_code` | String | No | Max length: 32 chars | Promotional discount code |

#### Response: `201 Created`
```json
{
  "data": {
    "subscription_id": "sub_a982103f",
    "customer_id": "cust_8281a9",
    "plan_id": "plan_pro_monthly",
    "status": "active",
    "currency": "USD",
    "amount_cents": 4900,
    "current_period_start": "2026-09-26T14:15:00Z",
    "current_period_end": "2026-10-26T14:15:00Z",
    "auto_renew": true,
    "created_at": "2026-09-26T14:15:00Z"
  }
}
```

#### Error Behaviors
- **`400 Bad Request`** (`INVALID_PAYLOAD`): Malformed JSON syntax or missing required field (`customer_id` or `plan_id`).
- **`402 Payment Required`** (`CARD_DECLINED`): Payment instrument was rejected by the card network.
- **`409 Conflict`** (`ACTIVE_SUBSCRIPTION_EXISTS`): Customer already holds an active subscription for this plan.
- **`422 Unprocessable Entity`** (`INVALID_PROMO_CODE`): The supplied `promo_code` has expired or reached redemption cap.

---

### 2.2 Retrieve Subscription

Retrieves the current status and metadata of a specific subscription.

- **Method**: `GET`
- **Path**: `/subscriptions/{subscription_id}`

#### Parameters
| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `subscription_id` | Path | String | Yes | Target identifier (e.g. `sub_a982103f`) |

#### Response: `200 OK`
```json
{
  "data": {
    "subscription_id": "sub_a982103f",
    "customer_id": "cust_8281a9",
    "plan_id": "plan_pro_monthly",
    "status": "active",
    "currency": "USD",
    "amount_cents": 4900,
    "current_period_start": "2026-09-26T14:15:00Z",
    "current_period_end": "2026-10-26T14:15:00Z",
    "auto_renew": true,
    "created_at": "2026-09-26T14:15:00Z"
  }
}
```

#### Error Behaviors
- **`404 Not Found`** (`RESOURCE_NOT_FOUND`): The provided `subscription_id` does not exist in the tenant workspace.

---

### 2.3 Cancel Subscription

Terminates an ongoing subscription, either immediately or at the conclusion of the billing cycle.

- **Method**: `POST`
- **Path**: `/subscriptions/{subscription_id}/cancel`

#### Request Payload
```json
{
  "cancellation_timing": "end_of_period",
  "reason_code": "CUSTOMER_REQUESTED",
  "feedback_comment": "Migrating to on-premise infrastructure."
}
```

#### Request Field Definitions
| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `cancellation_timing` | String | Yes | Enum: `immediate`, `end_of_period` | When cancellation takes effect |
| `reason_code` | String | Yes | Enum: `CUSTOMER_REQUESTED`, `NON_PAYMENT`, `FRAUD` | Categorized business rationale |
| `feedback_comment` | String | No | Max length: 500 chars | Free-text customer feedback |

#### Response: `200 OK`
```json
{
  "data": {
    "subscription_id": "sub_a982103f",
    "status": "cancelling",
    "effective_cancellation_date": "2026-10-26T14:15:00Z",
    "refund_issued_cents": 0
  }
}
```

---

### 2.4 List Invoices

Returns paginated list of billing invoices for a customer.

- **Method**: `GET`
- **Path**: `/invoices`

#### Query Parameters
| Parameter | In | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `customer_id` | Query | String | Yes | - | Customer account identifier |
| `status` | Query | String | No | `all` | Filter: `paid`, `open`, `void`, `all` |
| `limit` | Query | Integer | No | `20` | Results per page (1 to 100) |
| `starting_after`| Query | String | No | `null` | Cursor identifier for pagination |

#### Response: `200 OK`
```json
{
  "data": [
    {
      "invoice_id": "inv_1092837",
      "subscription_id": "sub_a982103f",
      "amount_due_cents": 4900,
      "amount_paid_cents": 4900,
      "status": "paid",
      "invoice_pdf_url": "https://billing.internal.acme.com/receipts/inv_1092837.pdf",
      "created_at": "2026-09-26T14:15:05Z"
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

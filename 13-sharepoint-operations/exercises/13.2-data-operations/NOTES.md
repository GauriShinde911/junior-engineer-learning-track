# 13.2 SharePoint List Data Operations

## Core Concept
Programmatic data operations against SharePoint Lists allow backend applications to create, query, update, and delete tabular records through REST endpoints. Interacting with list data requires authenticating against Azure AD, handling OData filtering, and isolating application business logic from SharePoint's internal schema quirks.

## Key Tools and Graph API Concepts
- **`msal.ConfidentialClientApplication`**: Handles OAuth 2.0 Client Credentials Grant flow (`https://graph.microsoft.com/.default` scope) for app-only authentication.
- **Graph `/sites/{site-id}/lists/{list-id}/items`**: REST endpoint pattern used to execute CRUD operations on SharePoint list records.
- **`$expand=fields`**: OData query parameter instructing Microsoft Graph to project custom column values instead of just system metadata.
- **`$filter` / `$select`**: OData query parameters for server-side evaluation of conditional predicates and column projection.

## Practical Theory: Internal Field Names vs Display Names
When an administrator creates a column in the SharePoint web UI (e.g., "Purchase Date"), SharePoint assigns an immutable "Internal Name" (e.g., `PurchaseDate` or `OData__x0050_urchaseDate`). Renaming the column later changes only the display title; the API will fail if requests do not use the original internal name. A dedicated field mapping layer bridges application domain models with SharePoint's internal naming, choice constraints, and ISO-8601 date expectations.

## Connection to What Was Built
This folder provides `list_item_client.py` for full CRUD operations via Microsoft Graph v1.0, paired with `field_mapper.py` for bidirectional type and name conversions. The accompanying `test_list_item_client.py` uses mocked HTTP responses to verify success, not-found, validation, throttling, and authentication error paths.

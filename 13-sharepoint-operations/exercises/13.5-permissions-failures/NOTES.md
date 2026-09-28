# 13.5 Permissions, Throttling, and Failure Management

## Core Concept
Integrating with enterprise cloud platforms like SharePoint introduces real-world operational failure modes including permission boundaries, API rate-limiting (throttling), and network interruptions. Engineering resilient integrations requires adhering to the Principle of Least Privilege and designing client software to gracefully diagnose, back off from, and handle these failure conditions.

## Key Permissions & Error Concepts
- **Principle of Least Privilege**: Granting only the exact minimal permissions required for an application to perform its duties, avoiding broad tenant-wide administrative access.
- **Application vs Delegated Permissions**: Application permissions run as an autonomous background daemon/service account, while Delegated permissions execute on behalf of a signed-in interactive human user.
- **`Sites.Selected` Scope**: Microsoft Graph's least-privilege permission model that restricts an application to explicitly granted site collections rather than every site in the tenant (`Sites.ReadWrite.All`).
- **HTTP 429 Throttling**: A server-side rate limit signal accompanied by a `Retry-After` header indicating how many seconds the client must pause before retrying.

## Practical Theory: Why Tenant-Wide Scopes Are Dangerous
Historically, developers registered Azure AD apps with `Sites.ReadWrite.All`, granting the application secret the ability to read and overwrite every document, list, and confidential file across the entire enterprise tenant. If that client secret leaked, the entire company was compromised. Modern cloud architectures mandate scoped permissions (`Sites.Selected`) and robust handling of 403s and 429 throttling.

## Connection to What Was Built
This folder provides `access_failure_simulation.py`, which simulates 403 Forbidden, 429 Throttling (with header inspection), and transport disconnects without live Azure calls. The accompanying `TROUBLESHOOTING_NOTES.md` provides an operational diagnostic guide to distinguish authorization, capacity, and network failures.

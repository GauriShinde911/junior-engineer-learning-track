# 8.3 Sessions & Role-Based Access — Concepts & Reference

## Core Concepts
HTTP is fundamentally stateless. Managing user sessions requires issuing a temporary, cryptographically unpredictable token upon successful login. The server maps this token to the authenticated user and validates both session validity and role permissions on every subsequent request.

## Authentication vs. Authorization
- **Authentication (401 Unauthorized)**: Answers *"Who are you?"* Verifies identity using credentials (passwords, MFA). If credentials fail or a session token is missing or expired, access is denied with an authentication error.
- **Authorization (403 Forbidden)**: Answers *"What are you allowed to do?"* Assumes identity is verified, but checks whether the user's assigned role or permissions allow the requested action.

## Session Expiry & Service-Layer Enforcement
- **Why Sessions Need Expiration (TTL)**: Tokens can be leaked via network eavesdropping, browser vulnerabilities, or shoulder surfing. Bounding token lifetime (e.g., 30 minutes) limits the window during which stolen credentials or hijacked sessions can be abused.
- **Service-Layer Access Control**: Never rely on frontend UI hiding (e.g., disabling a "Delete User" button) for security. Attackers can call backend APIs directly. Every sensitive service operation must independently verify caller permissions.

## Key Functions Used
- `secrets.token_urlsafe(32)`: Generates a cryptographically strong, unguessable random token (256 bits of entropy) resistant to brute-force enumeration.
- `time.time()`: Captures POSIX timestamps to evaluate session creation time against the expiration threshold (`expires_at = now + ttl`).
- `@require_roles(...)`: Service decorator that encapsulates authentication verification and role validation before executing business logic.

## Applied Implementation in this Folder
In [`auth_service.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.3-sessions/auth_service.py), `AuthService` issues cryptographically secure tokens with TTL timestamps and invalidates expired sessions. In [`role_based_access.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.3-sessions/role_based_access.py), `ApplicationPortalService` enforces role checks directly on methods, permitting regular users to view profiles while strictly restricting audit logs and administrative operations to admins.

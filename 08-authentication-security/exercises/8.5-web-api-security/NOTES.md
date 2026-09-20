# 8.5 Web & API Security — Concepts & Reference

## Core Concepts
Web applications and APIs are public-facing attack surfaces. Defending them requires an interlocking defense-in-depth model: strict input validation, authorization verification on every request, protection against client-side script injection (XSS) and forged requests (CSRF), and automated dependency vulnerability monitoring.

## Input Validation: Allow-Lists vs. Deny-Lists
- **Allow-Listing (Positive Validation)**: Define explicitly what is permitted (e.g., characters matching `^[a-zA-Z0-9_-]+$`, max length 64, specific enum values). Any input not matching the pattern is rejected. This is the gold standard of secure coding.
- **Deny-Listing (Negative Validation)**: Attempting to check for known bad characters (e.g., blocking `<script>` or `../`). Deny-lists inevitably fail because attackers use alternate encodings, null bytes, or novel syntax to bypass naive filters.

## Common Web Vulnerabilities
- **XSS (Cross-Site Scripting)**: Unsanitized user content rendered into the browser executes as attacker JavaScript, stealing cookies and session tokens. Remediated via output encoding, `HttpOnly` cookies, and CSP headers.
- **CSRF (Cross-Site Request Forgery)**: Malicious third-party sites submit forged requests leveraging the user's existing browser cookies. Remediated using anti-CSRF tokens and `SameSite` cookie attributes.
- **Path Traversal & Injection**: Using raw inputs in database queries or filesystem paths. Remediated using parameterized statements and isolated tenant namespaces.

## Key Controls Used
- `re.match(pattern, string)`: Enforces positive allow-list validation on filenames, emails, and identifiers.
- `set(payload.keys()) - ALLOWED_FIELDS`: Rejects unexpected fields to prevent mass assignment vulnerabilities.
- `_get_authenticated_user(auth_token)`: Verifies caller identity and extracts role before dispatching business logic.

## Applied Implementation in this Folder
In [`hardened_sample_app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.5-web-api-security/hardened_sample_app.py), each vulnerability from Exercise 8.1 is neutralized: passwords use bcrypt hashes, role modifications require authenticated admin tokens, document reads enforce alphanumeric allow-lists within user-scoped namespaces, and profile updates reject mass-assignment tampering.

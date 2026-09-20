# Authentication & Application Security — Skill Overview

Security in professional software engineering is not a cosmetic feature added before shipping; it is an architectural foundation. A robust application must inherently prevent unauthorized access, resist credential harvesting, enforce privilege boundaries at the service layer, and shield sensitive operational data across execution, logs, and storage.

This module provides hands-on mastery of secure coding practices in Python, moving systematically from vulnerability discovery to cryptographic protections, session architectures, secrets management, and regression testing.

---

## Module Roadmap & Curriculum Index

| Subsection | Focus Area | One-Line Summary | Reference Guide |
|---|---|---|---|
| **8.1** | **Security Basics** | Evaluates the CIA Triad, Principle of Least Privilege, and common architectural anti-patterns through a deliberately vulnerable sample app. | [8.1 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.1-security-basics/NOTES.md) |
| **8.2** | **Password Security** | Implements salted, slow one-way cryptographic password hashing and verification using `bcrypt`, completely eliminating plaintext credential storage. | [8.2 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.2-password-security/NOTES.md) |
| **8.3** | **Sessions & RBAC** | Designs cryptographically unguessable session tokens (`secrets`), time-to-live (TTL) expiration, and service-layer role authorization. | [8.3 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.3-sessions/NOTES.md) |
| **8.4** | **Secrets & Safe Logging** | Adheres to 12-Factor config principles with `python-dotenv` and prevents log credential leaks (CWE-532) via automated recursive redaction. | [8.4 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.4-secrets-configuration/NOTES.md) |
| **8.5** | **Web & API Security** | Hardens web services against path traversal, XSS/CSRF, mass assignment, and dependency vulnerabilities with strict allow-list input validation. | [8.5 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.5-web-api-security/NOTES.md) |
| **Challenge** | **Vulnerable App Hardening** | Full security assessment and remediation of a multi-vulnerability banking service backed by an automated regression test suite. | [Challenge README.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/independent/vulnerable_app_hardening/README.md) |

---

## Core Security Commandments

1. **Never Store or Compare Passwords in Plaintext**: Always hash using a slow, salted algorithm (`bcrypt`, `Argon2id`).
2. **Never Hardcode Secrets**: Store keys in environment variables; ensure `.env` is gitignored and provide `.env.example`.
3. **Enforce Authorization at the Service Layer**: Never rely on client-side hiding or URL obscurity.
4. **Scrub Sensitive Data from Logs**: Redact passwords, bearer tokens, and keys before writing to log sinks.
5. **Validate with Positive Allow-Lists**: Restrict inputs to known-good patterns rather than filtering known-bad sequences.

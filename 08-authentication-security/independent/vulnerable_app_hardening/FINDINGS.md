# Security Vulnerability Findings Report

This document details the security vulnerabilities discovered during the manual code audit of [`vulnerable_app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/independent/vulnerable_app_hardening/vulnerable_app.py).

---

## Executive Summary

| Finding ID | Vulnerability Title | Severity | Principle Violated | CWE |
|---|---|---|---|---|
| **VULN-01** | Hardcoded Application Secret Key | High | Confidentiality | CWE-798 |
| **VULN-02** | Plaintext Password Storage and Authentication | Critical | Confidentiality | CWE-256 |
| **VULN-03** | Predictable Session Identifiers Without Expiration | Critical | Confidentiality & Integrity | CWE-330 / CWE-613 |
| **VULN-04** | Insecure Direct Object Reference (IDOR) on Financial Statements | High | Confidentiality & Least Privilege | CWE-639 |
| **VULN-05** | Mass Assignment Enabling Administrative Privilege Escalation | High | Integrity & Least Privilege | CWE-915 |
| **VULN-06** | Plaintext Password and Token Exposure in Application Logs | High | Confidentiality | CWE-532 |

---

## Detailed Findings & Technical Analysis

### VULN-01: Hardcoded Master Secret Key
- **Location**: `SECRET_KEY = "hardcoded_master_secret_key_banking_system_12345"`
- **Severity**: High (CVSS 7.5) | **Principle**: Confidentiality
- **Description**: The signing secret key is embedded directly into module source code. Any user, contractor, or CI/CD system with source access possesses the key.
- **Remediation**: Load the secret key dynamically from environment variables using `python-dotenv` and enforce validation on startup.

---

### VULN-02: Plaintext Password Storage and Authentication
- **Location**: `USERS_TABLE` dictionary and `login_user()`
- **Severity**: Critical (CVSS 9.8) | **Principle**: Confidentiality
- **Description**: User passwords are stored as plaintext strings and evaluated using raw equality checks. A database dump or log snapshot compromises all credentials immediately.
- **Remediation**: Hash passwords using a slow, salted cryptographic algorithm (`bcrypt`) and verify using `bcrypt.checkpw()`. Plaintext passwords must never be stored.

---

### VULN-03: Predictable Session Identifiers Without Expiration
- **Location**: `token = f"sess-{random.randint(1000, 9999)}"` in `login_user()`
- **Severity**: Critical (CVSS 9.1) | **Principle**: Confidentiality & Integrity
- **Description**: Session tokens have only 9,000 possible values, making brute-force session hijacking trivial. Furthermore, sessions never expire, enabling permanent replay attacks.
- **Remediation**: Generate session tokens using cryptographically secure random generators (`secrets.token_urlsafe(32)`) providing 256 bits of entropy. Attach a TTL expiration timestamp (`expires_at = now + ttl`) and reject expired sessions.

---

### VULN-04: Insecure Direct Object Reference (IDOR) on Financial Statements
- **Location**: `get_account_statement()`
- **Severity**: High (CVSS 8.5) | **Principle**: Confidentiality & Least Privilege
- **Description**: The function verifies that the caller has a valid session token, but fails to check whether the authenticated user is the legal owner of `account_id`. Any authenticated user can read any other customer's financial statement.
- **Remediation**: Enforce an ownership check: verify that the account's `owner` matches the authenticated username derived from the session token (or allow only administrators with explicit authorization).

---

### VULN-05: Mass Assignment Enabling Administrative Privilege Escalation
- **Location**: `register_user()`
- **Severity**: High (CVSS 8.8) | **Principle**: Integrity & Least Privilege
- **Description**: Unfiltered payload binding allows client registration requests to set `is_admin=True` or `role='admin'`, granting administrative rights to any newly registered account.
- **Remediation**: Implement strict allow-listing for registration inputs (only `password`, `full_name`, `email`), explicitly forcing `is_admin=False` and `role='customer'`.

---

### VULN-06: Plaintext Password and Token Exposure in Application Logs
- **Location**: `logger.info(f"AUDIT LOGIN SUCCESS: user={username}, password={password}, token={token}")`
- **Severity**: High (CVSS 7.7) | **Principle**: Confidentiality
- **Description**: Successful authentication events print the customer's raw password and active session token into log streams. Anyone with log access gains full account takeover capabilities.
- **Remediation**: Scrub sensitive fields using an automated redaction formatter before writing log entries.

# Security Risk Assessment & Findings: Insecure Sample App

This document analyzes the deliberate architectural and code-level vulnerabilities identified in [`insecure_sample_app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.1-security-basics/insecure_sample_app.py). Each finding is categorized by security domain, impact, and violation of foundational security principles (CIA Triad & Principle of Least Privilege).

---

## Summary of Findings

| ID | Vulnerability | Severity | Principle Violated | CWE Mapping |
|---|---|---|---|---|
| **SEC-01** | Hardcoded Cryptographic Secret Key | High | Confidentiality | CWE-798: Use of Hard-coded Credentials |
| **SEC-02** | Plaintext Password Storage & Comparison | Critical | Confidentiality | CWE-256: Plaintext Storage of Sensitive Information |
| **SEC-03** | Broken Access Control / Privilege Escalation | Critical | Integrity & Least Privilege | CWE-285: Improper Authorization |
| **SEC-04** | Arbitrary Resource Access (IDOR / Path Traversal) | High | Confidentiality & Integrity | CWE-639: Insecure Direct Object Reference |
| **SEC-05** | Mass Assignment in Profile Updates | Medium | Integrity & Least Privilege | CWE-915: Improper Modification of Dynamically-Determined Object Attributes |

---

## Detailed Risk Analysis

### SEC-01: Hardcoded Cryptographic Secret Key
- **Location**: `JWT_SECRET_KEY = "hardcoded_secret_key_xyz_12345"`
- **Violated Principle**: **Confidentiality**
- **Risk & Impact**:
  Secrets committed to source code repositories are permanently visible in version history. Anyone with read access to the repo (including contractors, third-party CI/CD runners, or compromised developer laptops) can forge session tokens, decrypt sensitive application data, or impersonate arbitrary users.
- **Remediation**:
  Extract secrets out of source code into environment variables or secrets management vaults (e.g., `.env` ignored by Git, AWS Secrets Manager, HashiCorp Vault).

---

### SEC-02: Plaintext Password Storage & Comparison
- **Location**: `USERS_DB` dictionary and `authenticate_user_insecure()`
- **Violated Principle**: **Confidentiality**
- **Risk & Impact**:
  If the application database or an error log dumps user records, all accounts are compromised instantly. Furthermore, because users frequently reuse passwords across platforms, a breach here compromises user accounts across other services. Standard string comparison (`==`) is also vulnerable to side-channel timing attacks.
- **Remediation**:
  Never store plaintext passwords. Passwords must be hashed using a slow, salted cryptographic algorithm (e.g., `bcrypt` or `Argon2id`). Verification must use constant-time comparison.

---

### SEC-03: Broken Access Control / Privilege Escalation
- **Location**: `update_user_role_insecure()`
- **Violated Principle**: **Integrity & Principle of Least Privilege**
- **Risk & Impact**:
  The function takes a `caller` parameter but performs zero authorization checks to determine if `caller` holds the `admin` role. An unprivileged user can escalate their own account to administrator status, gaining total control over system resources and data.
- **Remediation**:
  Enforce explicit role-based access control (RBAC) at the service boundary. Verify that the authenticated caller holds the required permission before mutating privileges.

---

### SEC-04: Arbitrary Resource Access (IDOR / Path Traversal)
- **Location**: `read_document_insecure()`
- **Violated Principle**: **Confidentiality & Integrity**
- **Risk & Impact**:
  The function blindly trusts user-supplied keys (`doc_path`) and fetches resources without verifying that the requesting user owns the document or is authorized to view it. An attacker can access sensitive system documents (such as `system/secrets.txt`).
- **Remediation**:
  Establish strict trust boundaries: validate and sanitize object identifiers against an allow-list or scoped user namespace, and check ownership before returning data.

---

### SEC-05: Mass Assignment in Profile Updates
- **Location**: `process_profile_update_insecure()`
- **Violated Principle**: **Integrity & Principle of Least Privilege**
- **Risk & Impact**:
  The application uses `user.update(profile_data)` without filtering input keys. An attacker can pass `{"role": "admin"}` in their profile payload to quietly elevate privileges or tamper with immutable internal state.
- **Remediation**:
  Define explicit allow-lists for updateable fields (e.g., only `email` and `bio`), discarding or rejecting any unexpected attributes.

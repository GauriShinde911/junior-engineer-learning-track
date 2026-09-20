# Web & API Security Review

This document reviews the primary attack vectors confronting modern web applications and APIs, contrasting the vulnerabilities discovered in Exercise 8.1 with the defensive controls implemented in [`hardened_sample_app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.5-web-api-security/hardened_sample_app.py).

---

## 1. Injection Vulnerabilities (SQL, Command, Path Traversal)
- **The Risk**: Occurs when untrusted user input is directly concatenated into commands, queries, or file paths without prior parameterization or validation.
  - *SQL Injection*: Concatenating strings into SQL queries allows attackers to execute arbitrary SQL commands (bypassing auth, dumping databases, dropping tables).
  - *Path Traversal (`../`)*: Using unvalidated filenames allows attackers to traverse directory boundaries and read sensitive files outside intended directories (`/etc/passwd`, system configuration files).
- **The Defense**:
  - Never concatenate untrusted strings into queries or system commands.
  - Use parameterized queries or ORMs with prepared statements for database operations.
  - Use strict allow-lists (e.g. `^[a-zA-Z0-9_-]+$`) and scope file lookups to tenant-isolated namespaces rather than raw filesystem paths.

---

## 2. Cross-Site Scripting (XSS) vs. Cross-Site Request Forgery (CSRF)

| Feature | Cross-Site Scripting (XSS) | Cross-Site Request Forgery (CSRF) |
|---|---|---|
| **Mechanism** | Attacker injects malicious JavaScript into a site viewed by other users. | Attacker tricks a victim's browser into sending unauthorized commands to a vulnerable site where the victim is logged in. |
| **Trust Model** | Exploits the user's trust in the website. | Exploits the website's trust in the user's browser. |
| **Impact** | Stolen session tokens, keystroke logging, DOM manipulation, credential harvesting. | Unauthorized state-changing actions executed on behalf of the victim (e.g., password change, funds transfer). |
| **Primary Defenses** | Context-aware output encoding (HTML/JS escaping), Content-Security-Policy (CSP) headers, storing tokens in `HttpOnly` cookies. | Anti-CSRF tokens (Synchronizer Token Pattern), `SameSite=Strict` or `SameSite=Lax` cookie flags, verifying `Origin` / `Referer` headers. |

---

## 3. HTTPS & Security Response Headers
Transport Layer Security (TLS/HTTPS) encrypts data in flight, preventing eavesdropping and tampering across public networks. Alongside HTTPS, modern APIs and web servers configure standardized HTTP response headers to harden the client environment:
- **Strict-Transport-Security (HSTS)**: Forces browsers to communicate exclusively over HTTPS, preventing SSL-stripping man-in-the-middle attacks.
- **Content-Security-Policy (CSP)**: Restricts the domains from which scripts, images, and styles can be loaded, drastically reducing XSS exploitability.
- **X-Content-Type-Options: nosniff**: Instructs browsers not to guess (MIME-sniff) the response content type, preventing script execution disguised as images or text.
- **X-Frame-Options: DENY**: Prevents the application from being embedded inside an `<iframe>`, preventing Clickjacking attacks.

---

## 4. Dependency Hygiene & Supply Chain Security
Modern applications incorporate hundreds of open-source third-party libraries. If any package contains a known Common Vulnerability and Exposure (CVE), attackers can exploit it without ever touching your bespoke code.
- **Hygiene Practices**:
  - Pin dependency versions explicitly in `requirements.txt`.
  - Continuously scan dependencies using automated tools such as `pip-audit`, GitHub Dependabot, or Snyk.
  - Periodically upgrade and test dependencies to ensure timely patch adoption.

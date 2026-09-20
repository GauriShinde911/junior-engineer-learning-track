# Independent Project: Vulnerable App Hardening

This project demonstrates a full security audit, vulnerability assessment, and remediation engineering cycle for a Python backend service.

## Project Structure

```
independent/vulnerable_app_hardening/
├── vulnerable_app.py          # Intentionally vulnerable mini banking app
├── FINDINGS.md                # Comprehensive security audit & CVE mapping
├── fixed_app.py               # Enterprise-hardened application implementation
├── test_regression_checks.py  # Automated regression suite proving all fixes
└── README.md                  # Usage & instructions
```

## Vulnerabilities Identified & Fixed

1. **VULN-01**: Hardcoded Application Secret Key (CWE-798) → Resolved via dynamic environment configuration.
2. **VULN-02**: Plaintext Password Storage (CWE-256) → Resolved with salted `bcrypt` hashing and verification.
3. **VULN-03**: Predictable Session IDs Without Expiration (CWE-330, CWE-613) → Resolved with `secrets.token_urlsafe(32)` and TTL checks.
4. **VULN-04**: Insecure Direct Object Reference / IDOR (CWE-639) → Resolved with strict account ownership validation.
5. **VULN-05**: Mass Assignment Privilege Escalation (CWE-915) → Resolved via input allow-listing.
6. **VULN-06**: Plaintext Password & Token Exposure in Logs (CWE-532) → Resolved via automatic log scrubbing.

## Running Regression Tests

Run the automated regression test suite using `pytest`:

```bash
pytest 08-authentication-security/independent/vulnerable_app_hardening/test_regression_checks.py -v
```

All 6 regression test cases verify that the vulnerabilities cannot recur in `fixed_app.py`.

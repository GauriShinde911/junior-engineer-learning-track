# 8.1 Security Basics — Concepts & Reference

## Core Concepts
Application security is about designing software so that unauthorized parties cannot access sensitive information, modify protected state, or deny service to legitimate users. Rather than an afterthought or decorative layer, security principles must be woven into every architecture and data path.

## Foundational Principles
- **CIA Triad**:
  - **Confidentiality**: Ensuring data is accessible only to authorized entities (preventing unauthorized reading, eavesdropping, or data leaks).
  - **Integrity**: Protecting data and system state against unauthorized tampering, modification, or unauthorized elevation.
  - **Availability**: Guaranteeing systems and resources remain accessible and functional for authorized users when needed.
- **Principle of Least Privilege (PoLP)**: Every user, process, and component should have only the minimum access rights and permissions required to perform its specific task—nothing more.
- **Trust Boundaries**: The dividing line where data changes trust levels (e.g., from an untrusted public HTTP request to internal service logic). All data crossing a trust boundary must be validated and sanitized.

## Key Vulnerability Classes Highlighted
- **Hardcoded Secrets (CWE-798)**: Placing keys or credentials in code leaves them exposed in version control history.
- **Plaintext Passwords (CWE-256)**: Storing unhashed credentials directly exposes user secrets in the event of any data leak.
- **Broken Access Control (CWE-285)**: Failing to enforce authorization at the service layer allows users to act outside their intended permissions.
- **Mass Assignment (CWE-915)**: Blindly binding client input into application models allows attackers to modify internal attributes like user roles.

## Applied Implementation in this Folder
In [`insecure_sample_app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.1-security-basics/insecure_sample_app.py), deliberate vulnerabilities were modeled to illustrate each CIA and privilege violation. [`RISK_FINDINGS.md`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.1-security-basics/RISK_FINDINGS.md) systematically reviews each flaw, assessing risk impact and providing actionable remediation patterns.

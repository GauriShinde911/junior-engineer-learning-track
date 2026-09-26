# Documentation Review & Quality Checklist

> **Automated Test Substitution Notice**:  
> Technical documentation quality, clarity, and completeness cannot be validated through unit test frameworks like `pytest`. In place of automated unit test suites, this checklist defines concrete, objective Pass/Fail criteria for each subsection's deliverables based on curriculum standards. Every deliverable must satisfy 100% of its checklist criteria during peer review.

---

## 12.1 Project README (`exercises/12.1-readme/README.md`)

- [ ] **Clean-Clone Reproducibility**: Can another engineer clone the repository onto a fresh machine and run `sample_app` using *only* this document, without asking questions or encountering missing command steps?
- [ ] **Explicit Prerequisites**: Are runtime versions (Python 3.8+), supported operating systems, and external tools explicitly declared?
- [ ] **Configuration Transparency**: Are all environment variables (e.g. `TASK_TRACKER_DATA`) and default storage locations documented with cross-platform terminal examples (Bash, PowerShell, CMD)?
- [ ] **Complete Subcommand Reference**: Does every CLI subcommand (`add`, `list`, `complete`) have documented syntax, argument descriptions, and realistic terminal outputs?
- [ ] **Predictable Failure Modes**: Are common error outputs (e.g. invalid task ID) documented alongside resolution steps?

---

## 12.2 Technical Design & Architecture (`exercises/12.2-technical-docs/ARCHITECTURE.md`)

- [ ] **Understandable Without Walkthrough**: Can a new team member understand the system's structural layout and responsibilities without requiring a verbal walkthrough?
- [ ] **Clear Boundary Mapping**: Does the document clearly identify which component owns validation, transactional persistence, message dispatch, and notification delivery?
- [ ] **End-to-End Traceability**: Is the data flow traced step-by-step from client HTTP request through persistent storage to asynchronous consumer delivery?
- [ ] **Architectural Decision Records (ADRs)**: Does the document explain at least one non-obvious engineering decision (e.g., Transactional Outbox Pattern, optimistic locking) including the trade-offs and alternatives rejected?

---

## 12.3 API & Data Contracts (`exercises/12.3-api-data-docs/API_CONTRACT.md`)

- [ ] **Independent Integration Feasibility**: Could a frontend or external team implement a client against this specification without access to backend source code?
- [ ] **Strict Typing & Constraints**: Is every field typed with exact formatting rules, regex constraints, default values, and enum sets?
- [ ] **Exhaustive Status Codes**: Are error responses documented for invalid inputs (`400`), unauthorized requests (`401`), non-existent resources (`404`), conflicts (`409`), and validation errors (`422`)?
- [ ] **Standard Error Format**: Does the error schema adhere to a recognized convention (such as RFC 7807 problem details) with machine-readable error codes?

---

## 12.4 Operations Runbook (`exercises/12.4-runbooks/RUNBOOK.md`)

- [ ] **Actionable On-Call Usability**: Can an on-call engineer follow the runbook at 3:00 AM under pressure to deploy or recover the service?
- [ ] **Step-by-Step Deployment Procedure**: Are pre-flight checks, backup commands, dependency updates, and migration invocations explicitly written out?
- [ ] **Symptom-Driven Failure Scenarios**: Are at least 3 realistic production failure scenarios provided with exact diagnosis commands and corrective actions?
- [ ] **Deterministic Rollback Script**: Does the rollback section detail how to revert application binaries and database schema migrations safely?
- [ ] **Time-Bound Escalation Path**: Does the document specify clear time limits (e.g. 15 minutes) and contact roles for escalating unresolved incidents?

---

## 12.5 Change Documentation & Release Notes (`exercises/12.5-change-documentation/CHANGELOG.md`)

- [ ] **Version Traceability**: Can a user or auditor determine exactly what changed between any two release versions?
- [ ] **Semantic Versioning Compliance**: Do release tags follow Semantic Versioning (`MAJOR.MINOR.PATCH`) standards?
- [ ] **Standard Keep a Changelog Format**: Are changes grouped under standardized sections (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`)?
- [ ] **User Impact Summary**: Does each version include a plain-language summary explaining operational impact to users?
- [ ] **Actionable Migration Instructions**: Are breaking changes accompanied by specific migration scripts, SQL commands, or configuration conversions?

---

## Independent Challenge: Handover Pack (`independent/handover_documentation_pack/`)

- [ ] **Zero-Comment Subject**: Does `undocumented_app/main.py` serve as a realistic legacy/undocumented codebase with zero explanatory comments?
- [ ] **Four-Document Completeness**: Are all four core documentation deliverables present: `README.md`, `ARCHITECTURE.md`, `DEPLOYMENT.md`, and `TROUBLESHOOTING.md`?
- [ ] **Second-Person Validation Handover**: Does `HANDOVER_NOTE.md` explicitly state that genuine validation requires a second engineer to follow the documentation pack without author assistance?

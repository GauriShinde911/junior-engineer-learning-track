# Skill 12: Technical Documentation

## Overview
Technical documentation is the discipline of communicating software intent, architecture, operational procedures, and interfaces to other human beings. High-quality documentation transforms working code into maintainable, supportable, and collaborative software assets. It eliminates tribal knowledge, prevents production outages, accelerates team onboarding, and establishes clear contracts between independent services and teams.

> **Testing Note**: Documentation clarity and completeness cannot be validated by unit test runners like `pytest`. In place of automated test files, refer to [tests/DOC_REVIEW_CHECKLIST.md](tests/DOC_REVIEW_CHECKLIST.md) for objective, checklist-based review criteria.

---

## Subsection Map and Index

| Section | Topic | Summary | Reference |
|---|---|---|---|
| **12.1** | [Project README](exercises/12.1-readme/NOTES.md) | Authoring zero-assumption project entry points covering prerequisites, setup, configuration, and usage. | [12.1 NOTES.md](exercises/12.1-readme/NOTES.md) |
| **12.2** | [Technical Docs](exercises/12.2-technical-docs/NOTES.md) | Capturing system architecture, component boundaries, end-to-end data flow, and design trade-offs (ADRs). | [12.2 NOTES.md](exercises/12.2-technical-docs/NOTES.md) |
| **12.3** | [API & Data Docs](exercises/12.3-api-data-docs/NOTES.md) | Specifying exhaustive interface contracts with strict types, request/response examples, and error behaviors. | [12.3 NOTES.md](exercises/12.3-api-data-docs/NOTES.md) |
| **12.4** | [Operations Runbooks](exercises/12.4-runbooks/NOTES.md) | Writing actionable deployment runbooks, failure troubleshooting recipes, rollbacks, and escalation paths. | [12.4 NOTES.md](exercises/12.4-runbooks/NOTES.md) |
| **12.5** | [Change Documentation](exercises/12.5-change-documentation/NOTES.md) | Tracking version history, semantic release notes, user-impact summaries, and breaking migration guides. | [12.5 NOTES.md](exercises/12.5-change-documentation/NOTES.md) |
| **Independent** | [Handover Documentation Pack](independent/handover_documentation_pack/README.md) | Delivering a complete 4-document handover pack (`README`, `ARCHITECTURE`, `DEPLOYMENT`, `TROUBLESHOOTING`) for an undocumented app. | [Project README](independent/handover_documentation_pack/README.md) |

---

## Quality and Review Criteria
Every document in this skill folder is written against the principle of **Zero Assumed Context**: assume the reader is a competent engineer who has never seen this repository before and has a clean, unconfigured machine. For review standards across each subsection, consult [tests/DOC_REVIEW_CHECKLIST.md](tests/DOC_REVIEW_CHECKLIST.md).

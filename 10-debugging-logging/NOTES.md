# 10. Debugging & Logging — Module Overview & Index

This skill folder transitions software development from ad-hoc, trial-and-error guessing into an evidence-driven engineering discipline. Professional engineers do not modify code randomly hoping tests pass; they systematically reproduce issues, isolate the call stack, gather objective runtime evidence, hypothesize root causes, apply targeted surgical fixes, and prevent regressions using automated tests and structured observability.

---

## Curriculum Index & Subsection Overviews

1. [**10.1 Debugging Method**](exercises/10.1-debugging-method/NOTES.md)
   Teaches the scientific debugging loop (Reproduce -> Isolate -> Hypothesize -> Inspect Evidence -> Fix -> Verify) across tax calculations, mutable default argument traps, and non-atomic state mutations.

2. [**10.2 Reading Tracebacks**](exercises/10.2-tracebacks/NOTES.md)
   Covers bottom-up stack trace analysis, locating the exact failure frame, diagnosing 5 standard exceptions (`KeyError`, `ZeroDivisionError`, `TypeError`, `IndexError`, `AttributeError`), and tracing caller chains.

3. [**10.3 Application Logging**](exercises/10.3-logging/NOTES.md)
   Establishes production observability using Python standard library `logging`, proper severity levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`), structured message context, `logger.exception()`, and strict secret masking.

4. [**10.4 Runtime Diagnosis**](exercises/10.4-runtime-diagnosis/NOTES.md)
   Distinguishes application code bugs from environment failures (unset variables, unactivated virtualenvs) and infrastructure outages (DNS failures, connection refusals, timeouts).

5. [**10.5 Root Cause Analysis (RCA)**](exercises/10.5-root-cause-analysis/NOTES.md)
   Differentiates outward symptoms from fundamental root causes using the "5 Whys" method, producing minimal reproductions and automated regression tests across 5 real defect scenarios.

- [**Independent Challenge: Multi-Defect Diagnosis**](independent/multi_defect_diagnosis/README.md)
  Diagnoses and resolves 3 independent, planted defects across configuration, atomic inventory management, and pricing threshold calculations in a multi-file fulfillment pipeline.

---

## Core Principles

- **Evidence First**: Inspect runtime variables, memory addresses, and network connectivity before forming hypotheses.
- **Tracebacks Bottom-Up**: Read the exception type and the bottom-most frame first, then walk backward up the call chain.
- **Observability Over Guessing**: Use structured logs with levels and context rather than ephemeral print statements.
- **Never Treat Symptoms**: Solve the underlying defect and safeguard against recurrence with automated regression tests.

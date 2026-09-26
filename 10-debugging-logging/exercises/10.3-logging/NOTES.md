# 10.3 Application Logging & Observability

## Core Concepts
Logging provides a persistent, structured window into what software is doing in production without interrupting program execution. Print statements are ephemeral, unlevelled, and cannot be routed to files or aggregation platforms. Standard logging allows developers to categorize events by severity, attach machine-readable context, capture exception tracebacks, and configure log sinks without altering code.

## Key Tools & Functions
- `logging.getLogger(name)`: Instantiates or retrieves a namespaced logger instance adhering to the dot-separated logger hierarchy.
- `logging.DEBUG / INFO / WARNING / ERROR / CRITICAL`: Standard severity levels representing granular diagnostics, milestones, warnings, and faults.
- `logger.exception(msg, *args)`: Logs an ERROR level record while automatically capturing and appending the current `sys.exc_info()` stack trace.
- `caplog` (pytest fixture): Captures log records emitted during test execution, enabling assertions on level, message, and logger name.

## Exception Logging vs Plain Error Logs
Calling `logger.error("Something went wrong: " + str(e))` records only the exception message, discarding the call stack and leaving engineers blind to where the error occurred. Calling `logger.exception(...)` inside an `except` block automatically records both the contextual message and the full traceback, allowing rapid root-cause isolation.

## Security & Secret Hygiene
Never log raw credentials, session tokens, API keys, or personally identifiable information (PII/PCI). Always mask credit card numbers (e.g. keeping only the last 4 digits) and drop authorization tokens from diagnostic outputs.

## Connection to Exercises
In `unlogged_app.py`, operations executed without visibility. In `logged_app.py`, we implemented `LoggedPaymentService` using structured log statements across all four standard levels, sanitized sensitive credentials (passwords, tokens, CVVs), and used `logger.exception()` to record gateway transaction failures.

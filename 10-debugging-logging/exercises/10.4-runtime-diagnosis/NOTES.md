# 10.4 Runtime Diagnosis: Environment & Infrastructure

## Core Concepts
Not every production crash is caused by a code bug. Software operates inside a stack of execution layers: application code, runtime interpreter, operating system environment variables, local filesystem mounts, and external network infrastructure. Runtime diagnosis is the discipline of systematically isolating which layer failed before changing application logic.

## Key Diagnostic Functions
- `os.getenv(var, default)`: Safely inspects runtime process environment variables without raising unhandled exceptions.
- `socket.gethostbyname(hostname)`: Tests whether DNS resolution succeeds before attempting socket connections.
- `socket.create_connection((host, port), timeout)`: Verifies low-level TCP handshake reachability and identifies timeouts vs connection refusal.
- `sys.prefix != sys.base_prefix`: Reliably determines if the executing Python process is inside an activated virtual environment.
- `importlib.import_module(name)`: Programmatically tests dynamic module loading and isolates missing dependencies.

## Categorizing Runtime Failures
- **Code Failure**: Malformed SQL query syntax, index errors, bad function logic. Fix: Edit and test application code.
- **Environment Failure**: Unset API keys in `.env`, inactive virtualenv, incompatible Python runtime version. Fix: Shell configuration and virtualenv activation.
- **Infrastructure Failure**: DNS server timeout, closed firewall port, database server offline, volume mount missing. Fix: Network, DevOps, and cloud configuration.

## Connection to Exercises
In `broken_config_env.py`, we simulated missing environment paths and bad JSON configurations. In `broken_network_env.py`, we differentiated DNS failures from socket timeouts and connection refusals. In `broken_dependency_env.py`, we diagnosed unactivated virtualenvs and version incompatibilities, codified in `DIAGNOSIS_NOTES.md`.

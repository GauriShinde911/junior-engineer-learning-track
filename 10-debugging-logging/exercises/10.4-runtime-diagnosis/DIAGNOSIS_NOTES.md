# Runtime Diagnosis: Triage & Root Cause Isolation (10.4)

When an application crashes at runtime, jumping straight into code changes often wastes hours if the failure is actually environmental or infrastructural. A junior engineer must distinguish between three distinct categories:
- **Code Cause**: Bugs in application logic, type mismatches, bad algorithms.
- **Environment Cause**: Misconfigured environment variables, inactive virtual environments, missing local configuration files.
- **Infrastructure Cause**: DNS failures, closed firewall ports, unreachable services, unmounted volumes.

---

## 1. Configuration & Path Failures (`broken_config_env.py`)

### Symptom Observed
```text
ConfigurationError: Environment variable 'APP_CONFIG_PATH' is unset.
or
ConfigurationError: Config file not found at path '/etc/app/config.json'.
```

### Diagnostic Steps (Isolating Environment vs Code vs Infrastructure)
1. **Check Environment Variable**:
   - Inspect active shell environment: `echo $APP_CONFIG_PATH` (Linux/Mac) or `$env:APP_CONFIG_PATH` (PowerShell).
   - If empty -> **Environment Cause**. The process was started without sourcing `.env` or passing Docker `-e` arguments.
2. **Check Filesystem & Mount**:
   - If the variable is set to a path, run `ls -la "$APP_CONFIG_PATH"` or `Test-Path $env:APP_CONFIG_PATH`.
   - If the path does not exist on disk -> **Infrastructure Cause** (e.g. Kubernetes PersistentVolumeClaim failed to mount, or path was relative to a different working directory).
3. **Check File Integrity & Content**:
   - If file exists, validate permissions (`chmod/ACL`) and parse JSON syntax. If JSON syntax is invalid, it is a **Data/Config format defect**.

### Fix & Prevention
- Code: Implement graceful default fallbacks and startup assertions with actionable error messages rather than raw `KeyError`.
- Environment: Provide a checked-in `.env.example` file and validate all required environment variables at application boot.

---

## 2. Network & API Service Failures (`broken_network_env.py`)

### Symptom Observed
```text
NetworkServiceError: DNS resolution failed for host 'api.internal.service'
or
NetworkServiceError: Connection refused by 10.0.1.25:8080
or
NetworkServiceError: Connection timed out reaching 10.0.1.25:8080 after 1.0s
```

### Diagnostic Steps (Isolating Code vs Infrastructure)
1. **DNS Resolution Check**:
   - Run `nslookup api.internal.service` or `socket.gethostbyname()`.
   - If DNS resolution fails, the failure is **Infrastructure/Network** (bad DNS server, missing VPN, or domain typo).
2. **Port Reachability & Service Listening**:
   - Run `nc -zv <host> <port>` or PowerShell `Test-NetConnection -ComputerName <host> -Port <port>`.
   - If `Connection Refused`: Network and host are up, but the service process has crashed or is listening on a different port (**Service/Infrastructure**).
   - If `Connection Timed Out`: Packets are being silently dropped by a security group, firewall rule, or dead network route (**Network/Firewall**).

### Fix & Prevention
- Implement retries with exponential backoff and jitter for transient network failures.
- Set explicit socket timeouts to prevent threads from hanging indefinitely on dead connections.
- Implement circuit breakers to fail fast when downstream dependencies are down.

---

## 3. Dependency & Environment Conflicts (`broken_dependency_env.py`)

### Symptom Observed
```text
DependencyError: Module 'cryptography_accel' is not installed in interpreter '/usr/bin/python3'.
or
DependencyError: Module 'pydantic' version 1.10.0 is incompatible; requires >= 2.0.0.
```

### Diagnostic Steps (Isolating Virtualenv vs Code)
1. **Check Active Interpreter**:
   - Run `python -c "import sys; print(sys.executable, sys.prefix == sys.base_prefix)"`.
   - If `sys.prefix == sys.base_prefix`, the command was run in the global system Python rather than the project virtual environment (**Environment Cause: unactivated virtualenv**).
2. **Inspect Installed Packages**:
   - Run `pip list` or `python -m pip show <package>`.
   - Verify that the package exists in the active environment's `site-packages`.
3. **Verify Version Constraints**:
   - Check `mod.__version__` against version specifications in `pyproject.toml` or `requirements.txt`.

### Fix & Prevention
- Always activate the virtual environment (`. .venv/bin/activate` or `.venv\Scripts\Activate.ps1`).
- Lock exact dependency versions using lockfiles (`uv.lock` or `requirements.txt`).
- Add a runtime compatibility check at application startup to verify environment prerequisites.

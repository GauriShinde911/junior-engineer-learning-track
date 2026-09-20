# 8.4 Secrets & Configuration — Concepts & Reference

## Core Concepts
Secrets (API keys, database passwords, cryptographic tokens) must never be hardcoded into source code or tracked in version control. Modern applications follow the 12-Factor App methodology: strictly separating code from configuration, supplying secrets via environment variables at runtime, and protecting logs against inadvertent credential leaks.

## Secrets Management Hierarchy
- **Environment Variables**: System-level key-value pairs injected at application process startup (e.g., Docker environment, systemd, Kubernetes Secrets). The universal baseline for cloud-native software.
- **Local `.env` Files**: Convenient for local development. A local `.env` is parsed by libraries like `python-dotenv` into runtime environment variables, but must **always** be listed in `.gitignore`. A `.env.example` file is committed to document required variable keys with non-sensitive placeholder values.
- **Dedicated Secrets Managers**: Production systems often use centralized vaults (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault) that provide automatic rotation, fine-grained access policies, and audit logging.

## Safe Logging (CWE-532 Mitigation)
Application logs frequently aggregate to third-party dashboards (e.g., Datadog, CloudWatch, Splunk). If raw request payloads or error tracebacks print user passwords, tokens, or credit cards, those secrets are permanently exposed to log viewers and data breaches. Safe logging employs recursive scrubbing to mask sensitive keys before string formatting.

## Key Functions Used
- `dotenv.load_dotenv(dotenv_path)`: Parses local `.env` file key-values into `os.environ` if present.
- `os.environ.get(key, default)`: Safely extracts runtime configuration with fallback handling.
- `re.sub(pattern, replacement, string)`: Cleanses patterns like Bearer tokens and connection strings in raw log messages.

## Applied Implementation in this Folder
In [`config.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.4-secrets-configuration/config.py), `load_app_config()` verifies all mandatory environment variables and validates their formats before startup. In [`safe_logging.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.4-secrets-configuration/safe_logging.py), `SafeLogger` and `redact_sensitive_data()` recursively cleanse passwords, bearer tokens, and credentials from log streams.

# Local Encrypted Secret Vault CLI (`undocumented_app`)

A zero-dependency local secret and token management utility providing encrypted key-value storage with revision tracking and TTL (time-to-live) expiration.

---

## 1. Overview & Purpose

The Vault CLI (`vault`) is an offline developer utility designed to securely store and retrieve API keys, tokens, and local development credentials. Rather than leaving sensitive tokens in plaintext `.env` files or hardcoded scripts, Vault obfuscates and stores values on disk using a master encryption key, automatically enforcing credential expiration and revision counts.

---

## 2. Prerequisites

- **Operating System**: Linux, macOS, or Windows 10/11.
- **Python**: Python 3.8+ (tested on Python 3.11).
- **Dependencies**: None (uses standard library modules: `argparse`, `base64`, `hashlib`, `json`, `os`, `sys`, `time`, `datetime`, `pathlib`).

---

## 3. Installation & Getting Started

1. Navigate to the application folder:
   ```bash
   cd 12-documentation/independent/handover_documentation_pack/undocumented_app
   ```

2. Confirm Python can execute the CLI:
   ```bash
   python main.py --help
   ```

---

## 4. Configuration

The application is configured through environment variables:

| Environment Variable | Default Value | Description |
|---|---|---|
| `VAULT_SECRET_KEY` | `default-insecure-key-2026` | Master encryption key used to derive the 256-bit encryption key. **Must be overridden in production**. |
| `VAULT_STORAGE_PATH` | `vault.dat` (in working directory) | File path where the encrypted payload is persisted. |

### Setting Environment Variables

- **Linux / macOS**:
  ```bash
  export VAULT_SECRET_KEY="your-strong-random-master-password"
  export VAULT_STORAGE_PATH="$HOME/.local/share/vault.dat"
  ```
- **Windows (PowerShell)**:
  ```powershell
  $env:VAULT_SECRET_KEY = "your-strong-random-master-password"
  $env:VAULT_STORAGE_PATH = "$HOME\.vault.dat"
  ```

---

## 5. Command Reference & Usage

### 5.1 Storing a Secret (`set`)
Saves or overwrites a secret value. Each write increments the revision counter.

```bash
python main.py set <key> <value> [--ttl SECONDS]
```

- **Arguments**:
  - `key`: Alphanumeric identifier for the secret.
  - `value`: String value to encrypt and store.
  - `--ttl`: (Optional) Expiration window in seconds. Default: `0` (never expires).

**Examples**:
```bash
# Store permanent database password
python main.py set DB_PASSWORD "SecretPass123!"

# Store temporary access token expiring in 1 hour (3600 seconds)
python main.py set GITHUB_TOKEN "ghp_xxxxxxxxxxxx" --ttl 3600
```

**Output**:
```text
STORED DB_PASSWORD (rev 1)
```

---

### 5.2 Retrieving a Secret (`get`)
Fetches and decrypts the stored secret. Prints only the secret value to stdout, making it suitable for shell pipeline substitution.

```bash
python main.py get <key>
```

**Example**:
```bash
python main.py get DB_PASSWORD
```

**Output**:
```text
SecretPass123!
```

**Exit Codes**:
- `0`: Secret found and valid.
- `1`: Secret not found or expired (`NOT_FOUND <key>` printed to stderr).

---

### 5.3 Auditing Stored Secrets (`audit`)
Lists all registered keys, revisions, creation timestamps, and validity status without revealing secrets.

```bash
python main.py audit
```

**Output**:
```text
DB_PASSWORD | rev:1 | 2026-09-26T14:10:00Z | VALID
GITHUB_TOKEN | rev:2 | 2026-09-26T14:12:30Z | EXPIRED
```

---

### 5.4 Purging Expired Secrets (`purge`)
Removes all records whose TTL has elapsed, reclaiming space and cleaning up expired credentials.

```bash
python main.py purge
```

**Output**:
```text
PURGED 1 expired keys
```

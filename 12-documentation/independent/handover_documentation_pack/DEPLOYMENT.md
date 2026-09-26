# Deployment & Operations Guide: Local Secret Vault (`undocumented_app`)

This guide provides instructions for deploying, securing, and operating the Vault CLI tool on developer workstations and staging servers.

---

## 1. System Placement & Installation

### Option A: Linux / macOS (System-Wide CLI)

1. Deploy the script to an administrative tools directory:
   ```bash
   sudo mkdir -p /opt/vault
   sudo cp undocumented_app/main.py /opt/vault/vault.py
   sudo chmod 755 /opt/vault/vault.py
   ```

2. Create a global shell wrapper executable:
   ```bash
   sudo bash -c 'cat << "EOF" > /usr/local/bin/vault
   #!/usr/bin/env bash
   exec python3 /opt/vault/vault.py "$@"
   EOF'
   sudo chmod +x /usr/local/bin/vault
   ```

3. Verify installation:
   ```bash
   vault --help
   ```

---

### Option B: Windows Installation (PowerShell Profile)

1. Copy `main.py` into a user tools directory:
   ```powershell
   New-Item -ItemType Directory -Path "$env:LOCALAPPDATA\Vault" -Force
   Copy-Item "undocumented_app\main.py" "$env:LOCALAPPDATA\Vault\vault.py"
   ```

2. Add a persistent PowerShell function in `$PROFILE`:
   ```powershell
   Add-Content $PROFILE @"
   function vault {
       python "$env:LOCALAPPDATA\Vault\vault.py" `$args
   }
   "@
   ```

---

## 2. Security & Filesystem Permissions

Because `vault.dat` contains obfuscated secrets, strict filesystem access controls must be enforced:

1. **Dedicated User Directory**:
   Set `VAULT_STORAGE_PATH` to a private user directory rather than shared temp locations:
   ```bash
   export VAULT_STORAGE_PATH="$HOME/.config/vault/vault.dat"
   ```

2. **Restrict File Permissions (POSIX)**:
   Ensure only the owning user can read or write the secret vault:
   ```bash
   mkdir -p "$HOME/.config/vault"
   chmod 700 "$HOME/.config/vault"
   touch "$HOME/.config/vault/vault.dat"
   chmod 600 "$HOME/.config/vault/vault.dat"
   ```

3. **Master Key Management**:
   Do **not** leave `VAULT_SECRET_KEY` set to the default value. Inject a high-entropy key via the host environment or secure system keyring:
   ```bash
   export VAULT_SECRET_KEY=$(openssl rand -hex 32)
   ```

---

## 3. Automated Maintenance: Scheduled Secret Purging

To ensure expired credentials do not accumulate on disk, configure a scheduled purge task:

### On Linux (Cron):
Run `purge` daily at midnight:
```bash
crontab -e
# Add line:
0 0 * * * VAULT_STORAGE_PATH="$HOME/.config/vault/vault.dat" VAULT_SECRET_KEY="<key>" /usr/local/bin/vault purge >/dev/null 2>&1
```

### On Windows (Task Scheduler via PowerShell):
```powershell
$Action = New-ScheduledTaskAction -Execute "python" -Argument "`"$env:LOCALAPPDATA\Vault\vault.py`" purge"
$Trigger = New-ScheduledTaskTrigger -Daily -At 12:00AM
Register-ScheduledTask -TaskName "VaultPurgeExpired" -Action $Action -Trigger $Trigger
```

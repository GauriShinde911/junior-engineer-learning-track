# Troubleshooting Guide: Local Secret Vault (`undocumented_app`)

This guide diagnoses and remediates common failure modes encountered when managing secrets with the Vault CLI.

---

## 1. Quick Diagnostic Checklist

When the vault fails or returns unexpected results, verify these four parameters first:
1. `echo $VAULT_STORAGE_PATH`: Are you referencing the intended file?
2. `echo $VAULT_SECRET_KEY`: Has the master key changed since the secret was stored?
3. File permissions: Does your current operating system user own `vault.dat`?
4. Key expiration: Has the secret's TTL elapsed?

---

## 2. Common Failure Modes & Solutions

### Scenario 1: `NOT_FOUND <key>` Returned Unexpectedly
- **Symptom**: `python main.py get DB_KEY` outputs `NOT_FOUND DB_KEY` with exit status `1`, even though the key was recently stored.
- **Possible Causes**:
  1. **TTL Expiration**: The secret was set with `--ttl` and has passed its expiration window. Running `get` automatically purged it.
  2. **Storage Path Divergence**: You set the secret while working in a different terminal directory (storing to `./vault.dat`), but are retrieving it from another directory without `VAULT_STORAGE_PATH` set.
  3. **Master Key Changed**: If `VAULT_SECRET_KEY` differs from the key used during `set`, decryption yields garbled data, causing `_load()` to return an empty dictionary.
- **Remediation**:
  ```bash
  # Check if audit sees the key (if key wasn't purged)
  python main.py audit
  
  # Ensure storage path is explicit and absolute
  export VAULT_STORAGE_PATH="$HOME/.config/vault/vault.dat"
  python main.py get DB_KEY
  ```

---

### Scenario 2: Data Reset to Empty Dictionary / Secrets Vanished
- **Symptom**: Running `python main.py audit` returns `EMPTY` immediately after changing shell sessions.
- **Root Cause**:
  In `main.py`, `_load()` wraps decryption in a broad `try...except Exception: return {}`. If the master key `VAULT_SECRET_KEY` changes or is unset in a new shell session (falling back to `default-insecure-key-2026`), JSON decoding of the improperly decrypted ciphertext fails silently and treats the file as empty. If a user subsequently executes `set`, the existing file is overwritten with only the new key!
- **Remediation**:
  1. Always verify `VAULT_SECRET_KEY` matches the original key before running write commands.
  2. Maintain a backup of `vault.dat`:
     ```bash
     cp "$HOME/.config/vault/vault.dat" "$HOME/.config/vault/vault.dat.bak"
     ```
  3. Re-export the correct key:
     ```bash
     export VAULT_SECRET_KEY="<original-secret-key>"
     python main.py audit
     ```

---

### Scenario 3: `PermissionError: [Errno 13] Permission denied`
- **Symptom**: Executing `python main.py set ...` crashes with an unhandled Python traceback: `PermissionError: [Errno 13] Permission denied: 'vault.dat'`.
- **Root Cause**:
  The `vault.dat` file was created by `root` (e.g. during sudo execution) or another user account.
- **Remediation**:
  Reclaim file ownership:
  ```bash
  # Linux / macOS
  sudo chown $USER:$USER "$VAULT_STORAGE_PATH"
  chmod 600 "$VAULT_STORAGE_PATH"

  # Windows (PowerShell Administrator)
  takeown /f "$env:VAULT_STORAGE_PATH"
  ```

---

### Scenario 4: Special Characters Truncated or Mangled in Secret Values
- **Symptom**: Storing a value like `p@ss$word!` stores `p@ss` or triggers a bash history expansion error.
- **Root Cause**:
  The shell interprets characters like `$`, `!`, and spaces before passing the argument to `main.py`.
- **Remediation**:
  Enclose secret strings in single quotes `'...'` in Bash/Zsh or prevent string interpolation:
  ```bash
  python main.py set API_KEY 'AIzaSy$54!99_test'
  ```

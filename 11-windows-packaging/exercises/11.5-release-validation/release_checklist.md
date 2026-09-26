# Pre-Release Validation Checklist: Windows Executable

> **Target Artifact**: `wc-summary.exe` (or any PyInstaller-packaged Windows utility)  
> **Environment**: Clean Windows 10/11 target system (not the developer build machine)

Every packaged release must pass this checklist before distribution to end users. PyInstaller bundles depend on dynamic runtime extraction and platform libraries that may work on the developer's machine but fail in production environments.

---

## 1. Clean-Machine Smoke Tests

Run these on a machine **without Python or any development tools installed**:

- [ ] **Dependency Check**: Double-click or run from CMD. Does the application start without popping up a `"VCRUNTIME140.dll was not found"` or `"api-ms-win-crt-*.dll missing"` dialog?
- [ ] **CLI Help Flag**:
  ```powershell
  .\wc-summary.exe --help
  ```
  Expected: Prints clean argument usage, returns exit code 0.
- [ ] **Version Flag**:
  ```powershell
  .\wc-summary.exe --version
  ```
  Expected: Prints exact version (e.g., `wc-summary 1.0.0`), returns exit code 0.
- [ ] **Core Functionality Test**:
  ```powershell
  .\wc-summary.exe test_file.txt
  ```
  Expected: Correctly outputs line, word, and character counts with formatted output.
- [ ] **Missing Input Error Handling**:
  ```powershell
  .\wc-summary.exe non_existent_file.txt
  ```
  Expected: Clean error message printed to `stderr`, graceful exit with code 1 (no Python stack trace dump).

---

## 2. Permissions and Filesystem Validation

- [ ] **Standard User Execution**: Run as a restricted user account without administrative privileges. Verify no UAC prompt appears for basic execution.
- [ ] **Program Files Integrity**: Place binary inside `C:\Program Files\wc-summary\`. Run the utility. Verify it does not attempt to write temporary files or logs into `C:\Program Files\`, which causes an immediate `PermissionError`.
- [ ] **Per-User State Isolation**: Verify any cache, configuration, or log files are created within `%APPDATA%` or `%LOCALAPPDATA%`.

---

## 3. Logging and Diagnostics Check

- [ ] **Log Location**: Confirm log files are created in the expected directory (e.g. `%LOCALAPPDATA%\wc-summary\logs\`).
- [ ] **No Traceback Leaks**: Unhandled errors should log diagnostics to disk or stderr without exposing internal source paths (like `C:\Users\Admin\.gemini\...`).
- [ ] **Console vs Window Mode**: If built with `--noconsole`, confirm no empty black console window flickers upon launch. If built as a console app, confirm stdout/stderr redirection works properly:
  ```powershell
  .\wc-summary.exe test.txt > output.txt 2> error.txt
  ```

---

## 4. Antivirus and Endpoint Security Considerations

- [ ] **Windows SmartScreen**: Unsigned executables will trigger `"Windows protected your PC / Unknown Publisher"` SmartScreen warnings.
  - *Mitigation*: For production releases, sign the binary with a valid EV (Extended Validation) code-signing certificate via `signtool.exe`.
- [ ] **Antivirus Heuristic False Positives**: PyInstaller bootloaders (especially `--onefile` mode which unpacks files into `%TEMP%\_MEIxxxxxx`) are frequently flagged by generic heuristic scanners (e.g. Windows Defender, CrowdStrike).
  - *Mitigation*: Prefer `--onedir` distribution for internal enterprise tools, or submit false-positive dispute reports to Microsoft Security Intelligence.
- [ ] **Corporate Proxy & Group Policy**: Test on a domain-joined machine to ensure AppLocker or Software Restriction Policies do not block execution from `%TEMP%`.

---

## 5. Rollback Plan

If a release fails smoke testing, triggers endpoint security blocks, or introduces critical defects in the field:

1. **Immediate Halt**: Remove the download artifact from the internal distribution share or GitHub Releases page.
2. **Restore Previous Stable Version**:
   - For manual installations, revert the deployment directory from the backup:
     ```powershell
     Remove-Item "C:\Program Files\wc-summary" -Recurse -Force
     Rename-Item "C:\Program Files\wc-summary-backup" "wc-summary"
     ```
3. **Notify Users**: Send immediate notice advising users to retain the previous version (`vX.Y.Z-1`).
4. **Post-Mortem & Tag Invalidation**: Tag the failed release in Git as `vX.Y.Z-broken` and document the exact failure mode before repacking.

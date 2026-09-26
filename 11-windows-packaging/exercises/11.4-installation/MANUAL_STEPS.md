# Manual Steps: Testing Installation and Uninstallation on Windows

> **Why this document exists**: File system installations, permissions, shortcut creation, and uninstallation behaviors interact directly with the Windows shell, User Account Control (UAC), and user profile directories. These cannot be fully simulated or validated in an automated headless environment. Follow these exact steps on a target Windows machine.

---

## Prerequisites

1. You have a built application folder (`dist\wc-summary\`) from exercise 11.2 or a portable zip archive.
2. A Windows 10/11 machine with standard user access and optionally local Administrator access.

---

## Phase 1: Test Per-User (Non-Admin) Installation

1. **Extract/Copy Artifacts**:
   - Open PowerShell (standard user, NOT Run as Administrator).
   - Create the target folder:
     ```powershell
     New-Item -ItemType Directory -Path "$env:LOCALAPPDATA\Programs\wc-summary" -Force
     ```
   - Copy all contents of `dist\wc-summary\` into this directory:
     ```powershell
     Copy-Item -Recurse -Force "dist\wc-summary\*" "$env:LOCALAPPDATA\Programs\wc-summary\"
     ```

2. **Create Desktop Shortcut**:
   - Run the shortcut script from `install_procedure.md` targeting `$env:LOCALAPPDATA\Programs\wc-summary\wc-summary.exe`.
   - Verify that `wc-summary.lnk` appears on your Desktop with the expected icon.

3. **Verify Execution**:
   - Double-click the shortcut or execute from PowerShell:
     ```powershell
     & "$env:LOCALAPPDATA\Programs\wc-summary\wc-summary.exe" --help
     ```
   - Confirm it outputs the help text without raising any missing DLL or UAC prompt dialogs.

4. **Verify Config Resolution**:
   - Create a test file: `sample.txt` with some lines of text.
   - Run:
     ```powershell
     & "$env:LOCALAPPDATA\Programs\wc-summary\wc-summary.exe" sample.txt
     ```
   - Confirm output is correctly formatted.

---

## Phase 2: Test System-Wide (Program Files) Installation

1. **Open Elevated PowerShell** ("Run as Administrator").
2. **Copy Files**:
   ```powershell
   New-Item -ItemType Directory -Path "C:\Program Files\wc-summary" -Force
   Copy-Item -Recurse -Force "dist\wc-summary\*" "C:\Program Files\wc-summary\"
   ```
3. **Verify Read-Only Enforcement**:
   - Open standard user PowerShell (non-elevated).
   - Try to write a file inside `C:\Program Files\wc-summary\`:
     ```powershell
     "test" | Out-File "C:\Program Files\wc-summary\test.txt"
     ```
   - Confirm this operation is **denied with an UnauthorizedAccessException**.
   - This validates that configuration and logs cannot be stored inside the installation directory, confirming the design requirements in 11.3!

---

## Phase 3: Test Uninstallation

1. **Ensure No Running Instances**:
   ```powershell
   Get-Process -Name wc-summary -ErrorAction SilentlyContinue | Stop-Process -Force
   ```

2. **Clean Up Files**:
   - For Per-User:
     ```powershell
     Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Programs\wc-summary"
     Remove-Item "$env:USERPROFILE\Desktop\wc-summary.lnk" -ErrorAction SilentlyContinue
     ```
   - For Machine-Wide (Elevated):
     ```powershell
     Remove-Item -Recurse -Force "C:\Program Files\wc-summary"
     Remove-Item "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\wc-summary.lnk" -ErrorAction SilentlyContinue
     ```

3. **Verify Clean Removal**:
   - Check that the directory no longer exists:
     ```powershell
     Test-Path "C:\Program Files\wc-summary"
     ```
   - Confirm it returns `False`.
   - Verify shortcuts are gone and do not leave orphaned dead icons.

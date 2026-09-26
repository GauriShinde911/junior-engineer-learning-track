# Installation Procedure: wc-summary v1.0.0

This document is the definitive installation procedure for `wc-summary.exe` on Windows 10/11 (x86-64). Follow it in order. It covers file placement, shortcut creation, versioning, updates, and uninstall.

---

## 1. Prerequisites

Before distributing, confirm on the build machine:

- [ ] The exe was produced by `pyinstaller build.spec` (11.2) on a Windows machine.
- [ ] The release validation checklist (11.5) has passed.
- [ ] The version number in `sample_cli.py` (`APP_VERSION`) matches the distribution label.

---

## 2. File Placement

**Portable / single-user (no admin rights required)**

Copy the `dist\wc-summary\` folder to any writable location, e.g.:
```
C:\Users\<username>\Apps\wc-summary\
```

**Machine-wide / multi-user (requires administrator)**

Copy to `Program Files`:
```
C:\Program Files\wc-summary\
```
This directory is read-only for standard users, which is correct — the application
binary must never be modified by users at runtime. Config files go to `%APPDATA%`
(per 11.3 pattern), not here.

**Do not** place the exe directly on the Desktop or in Downloads — these are not stable,
version-manageable locations.

---

## 3. External Configuration File

Before first launch, create the config file in one of these locations (see 11.3):

**Per-user (preferred):**
```
%APPDATA%\wc-summary\wc_config.json
```

**Beside the exe (portable installs):**
```
<install_dir>\wc_config.json
```

Minimum valid content:
```json
{}
```

To override defaults, add any keys from `DEFAULT_CONFIG` in `app_with_external_config.py`.

---

## 4. Desktop / Start Menu Shortcut

**PowerShell (run as admin for Start Menu, as user for Desktop):**

```powershell
$WshShell = New-Object -comObject WScript.Shell

# Desktop shortcut
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\wc-summary.lnk")
$Shortcut.TargetPath = "C:\Program Files\wc-summary\wc-summary.exe"
$Shortcut.WorkingDirectory = "C:\Program Files\wc-summary"
$Shortcut.Description = "Word Count Summary Tool v1.0.0"
$Shortcut.Save()

# Start Menu shortcut (machine-wide, requires admin)
$StartMenu = $WshShell.CreateShortcut(
    "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\wc-summary.lnk")
$StartMenu.TargetPath = "C:\Program Files\wc-summary\wc-summary.exe"
$StartMenu.WorkingDirectory = "C:\Program Files\wc-summary"
$StartMenu.Description = "Word Count Summary Tool"
$StartMenu.Save()
```

---

## 5. Versioning Scheme

`wc-summary` uses **semantic versioning**: `MAJOR.MINOR.PATCH`

| Segment | When it changes |
|---|---|
| MAJOR | Incompatible command-line flag changes or config schema breaks |
| MINOR | New features added in a backward-compatible way |
| PATCH | Bug fixes; no behaviour changes |

The version string is embedded in the exe (`--version` flag) and should match the
filename of the distributed zip: `wc-summary-1.0.0-win64.zip`.

---

## 6. Update Strategy

There is no auto-updater. Updates are distributed as a new zip/folder:

1. Build and validate the new version (11.2, 11.5).
2. Stop any running instances: `Stop-Process -Name wc-summary -ErrorAction SilentlyContinue`
3. Rename the old install folder as a backup: `Rename-Item "C:\Program Files\wc-summary" "wc-summary-1.0.0-backup"`
4. Copy the new `dist\wc-summary\` folder to `C:\Program Files\wc-summary`.
5. Update shortcuts if the exe path or name changed.
6. Verify: `wc-summary.exe --version`
7. Delete the backup once verified.

---

## 7. Uninstall Steps

1. Delete the install directory:
   ```powershell
   Remove-Item -Recurse -Force "C:\Program Files\wc-summary"
   ```
2. Delete shortcuts:
   ```powershell
   Remove-Item "$env:USERPROFILE\Desktop\wc-summary.lnk" -ErrorAction SilentlyContinue
   Remove-Item "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\wc-summary.lnk" -ErrorAction SilentlyContinue
   ```
3. Optionally remove per-user config:
   ```powershell
   Remove-Item -Recurse "$env:APPDATA\wc-summary" -ErrorAction SilentlyContinue
   ```
4. There is no registry entry or Windows Installer database to clean for a portable exe.
   If a proper NSIS or Inno Setup installer was used, run its uninstaller instead.

---

## 8. Notes for Future Installer Tooling

For production deployments, consider wrapping these steps in a proper Windows installer:
- **NSIS** (Nullsoft Scriptable Install System) — free, widely used, produces `.exe` installer.
- **Inno Setup** — simpler scripting than NSIS; good for small apps.
- **WiX Toolset** — produces `.msi` packages; integrates with Windows Installer service for
  proper add/remove programs registry entries.

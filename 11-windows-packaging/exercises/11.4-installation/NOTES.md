# 11.4 Windows Installation

## Core Concept
Distributing a Windows binary involves more than providing a raw `.exe` file. A complete deployment strategy defines filesystem placement, user permissions, shell integration (desktop and Start Menu shortcuts), semantic versioning, side-by-side or in-place upgrade mechanics, and clean uninstallation procedures.

## Key Tools and Concepts
- **Per-User vs System-Wide Installation**: Per-user installs (`%LOCALAPPDATA%\Programs`) require no elevation, while system-wide installs (`%ProgramFiles%`) require admin privileges and enforce read-only execution directories.
- **WScript.Shell ComObject**: A built-in Windows COM interface used in PowerShell scripts to create `.lnk` shortcut files with target paths, icons, and working directories.
- **In-Place Updates**: Replacing binaries while preserving user state, handled by stopping running instances, staging new binaries, and retaining user data in `%APPDATA%`.
- **Clean Uninstallation**: Removing application binaries, start menu items, and desktop shortcuts without leaving dead references or corrupting shared system components.

## Practical Theory: Why Placement Matters
Installing to `C:\Program Files` enforces standard Windows security: regular users cannot alter binaries or drop malicious DLLs into the program folder. However, this also means the application will crash if it tries to write logs, temp files, or config changes into its own installation folder. Separating code (`Program Files`) from user state (`%APPDATA%` / `%LOCALAPPDATA%`) is fundamental to Windows software architecture.

## Connection to What Was Built
This folder establishes a complete deployment blueprint for `wc-summary.exe`: `install_procedure.md` provides copy commands, PowerShell shortcut scripts, version numbering rules, and update steps; `MANUAL_STEPS.md` details testing these steps manually on a real Windows machine.

> **Note on Automated Tests**: This subsection covers OS installation and filesystem management procedures rather than Python unit logic. There are no automated pytest tests here; validation must be performed manually following `MANUAL_STEPS.md`.

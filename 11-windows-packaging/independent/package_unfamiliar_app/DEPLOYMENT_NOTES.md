# Deployment Notes: DataAuditor (Target App)

This document records all architectural assumptions, environment dependencies, and operational troubleshooting procedures for deploying the packaged `DataAuditor` application to Windows machines.

---

## 1. Architectural & Environment Assumptions

### Target Operating System
- **OS**: Windows 10 (version 1809+) or Windows 11, 64-bit (`x86_64`).
- **Python Runtime**: The application is packaged with PyInstaller and bundles CPython. The client machine does **not** require Python installed.
- **C Runtime**: Assumes the Microsoft Visual C++ Redistributable (2015-2022) is present. If missing on barebones Windows installs, the application will fail to start until `vc_redist.x64.exe` is installed.

### Privilege Model
- **Standard User Execution**: The application is explicitly architected to run under standard user privileges without triggering UAC elevation prompts.
- **Installation Directory**: Can be deployed to `C:\Program Files\DataAuditor` (machine-wide) or `%LOCALAPPDATA%\Programs\DataAuditor` (per-user).
- **Directory Mutability**: The application assumes that its installation directory is **strictly read-only** at runtime. It never writes temporary files, logs, or updated configs into `sys.executable`'s parent folder.

### Filesystem & State Locations
- **Logs**: Written to `%LOCALAPPDATA%\DataAuditor\logs\auditor.log`. The parent directory is created automatically on startup.
- **Config**: Resolved using a tiered fallback hierarchy:
  1. Explicit `--config <path>` flag.
  2. Environment variable `AUDITOR_CONFIG_PATH`.
  3. Adjacent `config.json` (for portable standalone zip distributions).
  4. Per-user standard location `%APPDATA%\DataAuditor\config.json`.
  5. Hardcoded sensible defaults (`DEFAULT_CONFIG`) if no file is present.

---

## 2. Troubleshooting Common Failure Modes

### Failure Mode 1: Missing VCRUNTIME140.dll or api-ms-win-crt-*.dll
- **Symptoms**: Double-clicking the `.exe` triggers a system dialog stating: `"The code execution cannot proceed because VCRUNTIME140.dll was not found."`
- **Cause**: PyInstaller-compiled binaries require the Universal C Runtime (CRT).
- **Resolution**:
  1. Download and run the official Microsoft Visual C++ Redistributable installer:
     ```powershell
     winget install Microsoft.VCRedist.2015+.x64
     ```
  2. Alternatively, bundle `vcruntime140.dll` alongside `DataAuditor.exe` in the deployment directory.

### Failure Mode 2: PermissionError on Logging or Output
- **Symptoms**: `[WARNING] Could not initialize file logging: [Errno 13] Permission denied` or crash when `--output` is specified.
- **Cause**: The application attempted to write to a protected directory (such as `C:\Program Files\` or root of `C:\`).
- **Resolution**:
  1. Verify `%LOCALAPPDATA%` points to a writable user profile.
  2. When using `--output`, pass a path inside the user's home directory (e.g. `--output $HOME\report.json`) or a writable folder.

### Failure Mode 3: Hidden Imports / ModuleNotFoundError
- **Symptoms**: Executable crashes immediately upon startup with `ModuleNotFoundError: No module named 'processor'`.
- **Cause**: PyInstaller failed to detect dynamic imports or submodules during AST analysis.
- **Resolution**:
  1. Check `build.spec` under `hiddenimports`.
  2. Ensure internal submodules (`config`, `logger`, `processor`) are explicitly listed in `hiddenimports`.
  3. Rebuild using `pyinstaller build.spec`.

### Failure Mode 4: Frozen Path Resolution (`_MEIPASS` vs `__file__`)
- **Symptoms**: Script works with `python main.py` but fails with `FileNotFoundError` when running as `.exe`.
- **Cause**: PyInstaller bundles unpack either into a temporary folder (`sys._MEIPASS` in `--onefile`) or beside the exe (`Path(sys.executable).parent` in `--onedir`). Code that relies on `__file__` breaks in onefile mode.
- **Resolution**:
  Always use the standard PyInstaller path detection idiom:
  ```python
  if getattr(sys, "frozen", False):
      base_dir = Path(sys.executable).parent
  else:
      base_dir = Path(__file__).resolve().parent
  ```

### Failure Mode 5: Windows Defender / SmartScreen "Unknown Publisher"
- **Symptoms**: Blue SmartScreen banner: `"Windows protected your PC"`.
- **Cause**: Executable lacks an Authenticode digital signature.
- **Resolution**:
  1. For testing: Click `"More info"` -> `"Run anyway"`.
  2. For enterprise release: Sign the binary using `signtool.exe` with a corporate code signing certificate.

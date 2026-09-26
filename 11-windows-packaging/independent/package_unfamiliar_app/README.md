# Independent Project: Packaging DataAuditor

A practical project demonstrating end-to-end Windows executable packaging for a multi-module Python application that handles external configuration and writes runtime logs.

---

## Project Structure

```
package_unfamiliar_app/
├── target_app/
│   ├── __init__.py       # Package marker
│   ├── main.py           # CLI entry point and argument parsing
│   ├── config.py         # Config file loading with fallback logic
│   ├── logger.py         # Safe user-directory logging
│   └── processor.py      # File auditing and SHA256 checksumming
├── build.spec            # PyInstaller build specification
├── DEPLOYMENT_NOTES.md   # Deployment assumptions & troubleshooting guide
└── README.md             # This document (usage and build instructions)
```

---

## 1. Running from Source

To run the application directly with Python:

```bash
# Basic run on current directory
python target_app/main.py

# Audit specific directory with verbose output
python target_app/main.py ./some_folder --verbose

# Save JSON report to disk
python target_app/main.py ./some_folder --output audit_report.json

# Use custom configuration file
python target_app/main.py ./some_folder --config custom_config.json
```

---

## 2. Packaging with PyInstaller

On a Windows build machine with `pyinstaller` installed:

```bash
# Run the spec file from this directory
pyinstaller build.spec --clean
```

This generates:
- `build/`: Temporary compilation artifacts (safe to delete).
- `dist/DataAuditor/`: Complete standalone folder containing `DataAuditor.exe` and bundled dependencies.

---

## 3. Running the Packaged Executable

```powershell
# Run the compiled binary
.\dist\DataAuditor\DataAuditor.exe --help

# Run an audit with output report
.\dist\DataAuditor\DataAuditor.exe "C:\Path\To\Audit" --output "$HOME\audit.json"
```

Refer to `DEPLOYMENT_NOTES.md` for runtime requirements, permission constraints, and troubleshooting tips.

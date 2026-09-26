# Skill 11: Windows Packaging and Distribution

## Overview
This skill covers transforming raw Python scripts into robust, standalone, and distributable Windows applications (`.exe`). It bridges the gap between running code inside a local development environment and delivering reliable software to end users without requiring them to install Python, configure virtual environments, or manage runtime dependencies.

Packaging is not simply running a compiler; it encompasses binary bundling, dynamic import resolution, configuration management outside the frozen bundle, filesystem permission models, OS installation mechanics, and clean-machine release validation.

> **Environment Reality Check**: PyInstaller produces native Windows PE binaries whose execution, installation, and endpoint behavior depend on the target Windows OS environment. Tasks requiring executable compilation, shortcut creation, filesystem ACL checks, and clean-machine smoke tests require manual execution on a real Windows system and cannot be fully automated inside a headless container.

---

## Subsection Map and Index

| Section | Topic | Summary | Reference |
|---|---|---|---|
| **11.1** | [Packaging Concepts](exercises/11.1-packaging-concepts/NOTES.md) | What packaging solves (standalone distribution) and doesn't solve (OS libraries, cross-platform portability). | [11.1 NOTES.md](exercises/11.1-packaging-concepts/NOTES.md) |
| **11.2** | [Executable Build](exercises/11.2-executable-build/NOTES.md) | Building binaries with PyInstaller, handling hidden imports, and configuring `.spec` files. | [11.2 NOTES.md](exercises/11.2-executable-build/NOTES.md) |
| **11.3** | [Configuration](exercises/11.3-configuration/NOTES.md) | Storing mutable configuration and user state outside read-only bundled executables. | [11.3 NOTES.md](exercises/11.3-configuration/NOTES.md) |
| **11.4** | [Installation](exercises/11.4-installation/NOTES.md) | Deploying binaries (`Program Files` vs user profile), shortcut generation, versioning, and uninstall. | [11.4 NOTES.md](exercises/11.4-installation/NOTES.md) |
| **11.5** | [Release Validation](exercises/11.5-release-validation/NOTES.md) | Pre-flight smoke tests, permission checks, SmartScreen / antivirus false-positive mitigations, and rollback. | [11.5 NOTES.md](exercises/11.5-release-validation/NOTES.md) |
| **Independent** | [Package Unfamiliar App](independent/package_unfamiliar_app/README.md) | End-to-end packaging of a modular multi-file auditing utility (`DataAuditor`) with external config and logging. | [Project README](independent/package_unfamiliar_app/README.md) |

---

## Testing & Verification Summary
- **Automated Tests**: Subsection 11.1 (`sample_cli.py`) and 11.3 (`app_with_external_config.py` vs `app_with_bad_config.py`) have automated `pytest` test suites verifying core application logic and configuration loading behaviors.
- **Manual Verification Procedures**: Subsections 11.2, 11.4, and 11.5 represent build, OS installation, and release validation procedures. These are documented with step-by-step instructions in their respective `MANUAL_STEPS.md` and `release_checklist.md` files for testing on real Windows hardware.

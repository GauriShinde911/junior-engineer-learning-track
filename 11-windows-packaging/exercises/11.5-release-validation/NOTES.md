# 11.5 Release Validation

## Core Concept
Packaging an executable does not guarantee it will run on an end-user's machine. Release validation is the discipline of testing compiled artifacts on a "clean machine" (a system without Python, C++ build tools, or developer dependencies) to catch missing DLLs, permissions traps, antivirus blocks, and configuration failures before shipping.

## Key Tools and Concepts
- **Clean Machine Testing**: Validating software in an isolated VM or standard user box to ensure all runtime dependencies are truly bundled.
- **Visual C++ Redistributable (`VCRUNTIME140.dll`)**: A common unbundled dependency that causes instant crashes on vanilla Windows systems if omitted.
- **SmartScreen and Code Signing**: Windows security features that block or warn users against running unsigned or newly encountered binaries.
- **Rollback Strategy**: A predetermined plan to immediately revert users to the prior stable release if a critical defect escapes into production.

## Practical Theory: Why "Works on My Machine" Fails with Binaries
Developers have system PATH entries, Python interpreters, Windows SDKs, and Visual C++ runtimes pre-installed. PyInstaller bootloaders often silently resolve missing DLLs from the developer's system directories during development. When moved to a user machine, these DLLs are absent, resulting in cryptic failure dialogs. Furthermore, heuristic antivirus engines frequently flag newly compiled `--onefile` unpacked executables as suspicious.

## Connection to What Was Built
This subsection provides `release_checklist.md`, a five-point pre-release verification protocol covering smoke tests, permissions, log file sanity, antivirus/SmartScreen mitigations, and a rollback protocol.

> **Note on Automated Tests**: Release validation requires an external, clean Windows operating system environment and cannot be automated in unit tests. There are no automated pytest tests in this subsection; consult `release_checklist.md` for verification.

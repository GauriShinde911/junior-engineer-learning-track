# Manual Steps: Running the Executable Build on a Real Windows Machine

> **Why this document exists**: PyInstaller builds are platform-specific and
> produce a native Windows PE binary. The build cannot be run inside this
> coding environment, and the resulting exe cannot be validated here.
> Every step below requires a real Windows 10/11 machine.

---

## Prerequisites

Before starting, verify:

- [ ] Windows 10 or 11 (x86-64)
- [ ] Python 3.11+ installed: `python --version`
- [ ] Git installed; repo cloned locally
- [ ] A virtual environment created and activated:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  pip install -r 11-windows-packaging/requirements.txt
  ```

---

## Step 1 — Run the Build

From a PowerShell prompt at the **repository root**:

```powershell
pip install pyinstaller
pyinstaller 11-windows-packaging/exercises/11.2-executable-build/build.spec `
    --distpath dist `
    --workpath build `
    --noconfirm
```

**Expected console output** ends with:
```
INFO: Building EXE from EXE-00.toc completed successfully.
INFO: Building COLLECT because COLLECT-00.toc is non existent
INFO: Building COLLECT COLLECT-00.toc completed successfully.
```

---

## Step 2 — Confirm the Output Exists

```powershell
Test-Path "dist\wc-summary\wc-summary.exe"   # must print True
(Get-Item "dist\wc-summary\wc-summary.exe").Length  # typically > 5 MB
```

---

## Step 3 — Run the Exe Standalone (Not Through Python)

```powershell
# From any directory — do NOT use python.exe to run it
dist\wc-summary\wc-summary.exe --version
```

Expected output:
```
wc-summary 1.0.0
```

```powershell
# Functional smoke test
echo "Hello world. Hello Python." > test_input.txt
dist\wc-summary\wc-summary.exe test_input.txt --top 2
```

Expected output (approximate):
```
wc-summary v1.0.0  —  test_input.txt
--------------------------------------------------
  Characters :          27
  Words      :           4
  Lines      :           1

  Top 2 words:
    1. hello                    2
    2. world                    1
```

---

## Step 4 — Validate on a Machine With No Python Installed

> This is the critical clean-machine test. It must be done on a separate
> Windows machine or a fresh VM that has **never had Python installed**.

1. Copy the entire `dist\wc-summary\` folder to the clean machine (USB, network share, or zip).
2. Double-click `wc-summary.exe` in Explorer — a console window should appear and close immediately (correct; it needs arguments).
3. Open cmd.exe or PowerShell and run:
   ```cmd
   wc-summary.exe --version
   ```
4. Confirm no "Python not found" or DLL errors appear.

---

## Step 5 — Check for Common Build Failures

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ModuleNotFoundError` at runtime | Hidden import missing from spec | Add the module name to `hiddenimports=` in `build.spec` |
| `FileNotFoundError` for a data asset | Data file not declared in `datas=` | Add `("path/to/file", "dest_folder")` to `datas=` |
| Antivirus quarantines the exe | Unsigned binary heuristic | See 11.5 release checklist; sign the exe with `signtool.exe` |
| Very slow first launch | `--onefile` mode extraction to `%TEMP%` | Switch spec to `--onedir` for production deployment |
| Missing DLL error (`VCRUNTIME140.dll`) | Visual C++ redistributable absent | Install VC++ Redistributable 2019+ on the target machine |

---

## What to Record After a Successful Build

- PyInstaller version used
- Python version used
- Windows version tested on
- Whether clean-machine test passed
- Size of the final `dist\wc-summary\` folder in MB

# -*- mode: python ; coding: utf-8 -*-
#
# build.spec — PyInstaller specification for sample_cli.py
#
# This spec file is used with:
#   pyinstaller build.spec
#
# It produces a one-dir build in dist/wc-summary/ by default.
# To switch to a single-file exe, change onefile=True in EXE() below.
#
# PyInstaller version: 6.x+
# Target OS: Windows 10 / 11 (x86-64)
# Python version: 3.11+
#

import sys
from pathlib import Path

# Absolute path to the exercises directory so the spec resolves correctly
# from any working directory.
SPEC_DIR = Path(SPECPATH)               # noqa: F821 — injected by PyInstaller
SRC = str(SPEC_DIR.parent / "11.1-packaging-concepts" / "sample_cli.py")

block_cipher = None

# ---------------------------------------------------------------------------
# Analysis — discovers imports and assets
# ---------------------------------------------------------------------------
a = Analysis(
    [SRC],
    pathex=[str(SPEC_DIR.parent / "11.1-packaging-concepts")],
    binaries=[],
    datas=[
        # No data files required by sample_cli.py itself, but the pattern
        # for adding them is shown below.  Uncomment and adjust as needed:
        # ("path/to/asset.json", "assets"),
    ],
    hiddenimports=[
        # sample_cli.py uses only the standard library, so no hidden imports
        # are required.  The pattern for declaring them is:
        # "module.name",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude modules that are definitely not needed, to slim the bundle.
        "tkinter",
        "unittest",
        "email",
        "http",
        "xml",
        "xmlrpc",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ---------------------------------------------------------------------------
# PYZ — compressed Python archive
# ---------------------------------------------------------------------------
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

# ---------------------------------------------------------------------------
# EXE — the final executable
# ---------------------------------------------------------------------------
exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # False for --onefile; True keeps one-dir layout
    name="wc-summary",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                # Set False if UPX is not installed
    console=True,            # CLI app — keep True; False hides the console window
    disable_windowed_traceback=False,
    target_arch=None,        # None = auto-detect; "x86_64" or "x86" for explicit cross
    codesign_identity=None,
    entitlements_file=None,
    icon=None,               # Set to "path/to/icon.ico" for a custom application icon
)

# ---------------------------------------------------------------------------
# COLLECT — assembles the one-dir output folder
# ---------------------------------------------------------------------------
coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="wc-summary",
)

# NOTE: To build a single-file .exe instead of a directory, replace the
# EXE + COLLECT pair above with:
#
#   exe = EXE(
#       pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
#       name="wc-summary",
#       debug=False, strip=False, upx=True, console=True,
#       ...
#   )
#
# (no COLLECT block needed in that case)

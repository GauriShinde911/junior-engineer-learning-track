# -*- mode: python ; coding: utf-8 -*-
#
# build.spec — PyInstaller specification for DataAuditor (target_app)
#
# Usage:
#   pyinstaller build.spec
#
# Produces a clean onedir distribution in dist/DataAuditor/

import sys
from pathlib import Path

block_cipher = None
spec_root = Path(SPECPATH)
target_app_dir = spec_root / "target_app"

a = Analysis(
    [str(target_app_dir / "main.py")],
    pathex=[str(target_app_dir), str(spec_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Explicitly declare modules imported inside target_app
        "config",
        "logger",
        "processor",
        "hashlib",
        "json",
        "logging"
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "scipy",
        "numpy",
        "pytest",
        "unittest"
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DataAuditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DataAuditor'
)

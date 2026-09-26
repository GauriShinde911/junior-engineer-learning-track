#!/usr/bin/env bash
# build.sh — Repeatable build script for sample_cli.py
#
# Run this script from the repo root or from this directory.
# It activates the virtual environment (if present), installs PyInstaller,
# and invokes the spec file.
#
# WINDOWS EQUIVALENT (run in PowerShell or cmd from this directory):
#   .venv\Scripts\Activate.ps1          # activate venv
#   pip install pyinstaller             # ensure PyInstaller is installed
#   pyinstaller exercises/11.2-executable-build/build.spec
#
# OUTPUT:
#   build/wc-summary/         — intermediate build artefacts
#   dist/wc-summary/          — final distributable folder
#     └── wc-summary.exe      — the standalone executable
#
# ────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SPEC_FILE="$SCRIPT_DIR/build.spec"

echo "=== wc-summary build ==="
echo "Repo root  : $REPO_ROOT"
echo "Spec file  : $SPEC_FILE"
echo ""

# ── 1. Activate virtual environment if one exists ────────────────────────────
if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
    echo "[1/4] Activating virtual environment..."
    # shellcheck disable=SC1091
    source "$REPO_ROOT/.venv/bin/activate"
else
    echo "[1/4] No .venv found — using system/global Python ($(python --version 2>&1))"
fi

# ── 2. Ensure PyInstaller is installed ──────────────────────────────────────
echo "[2/4] Checking PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "     PyInstaller not found — installing..."
    pip install --quiet pyinstaller
fi
echo "     PyInstaller $(python -c "import PyInstaller; print(PyInstaller.__version__)")"

# ── 3. Clean previous build artefacts ───────────────────────────────────────
echo "[3/4] Cleaning previous build artefacts..."
rm -rf "$REPO_ROOT/build/wc-summary" "$REPO_ROOT/dist/wc-summary"

# ── 4. Run PyInstaller with the spec file ────────────────────────────────────
echo "[4/4] Running PyInstaller..."
pyinstaller \
    --distpath "$REPO_ROOT/dist" \
    --workpath "$REPO_ROOT/build" \
    --noconfirm \
    "$SPEC_FILE"

echo ""
echo "=== Build complete ==="
echo "Output: $REPO_ROOT/dist/wc-summary/wc-summary.exe"
echo ""
echo "Quick smoke test (Windows):"
echo '  dist\wc-summary\wc-summary.exe --version'

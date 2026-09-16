"""
5.1 Git Basics: setup_sandbox.py
Initializes a self-contained, throwaway Git sandbox repository inside:
exercises/5.1-git-basics/sandbox/

Sets up starter files and historical commits via subprocess calls to git.
Never interacts with the outer parent repository.
"""

from pathlib import Path
import os
import shutil
import stat
import subprocess
import sys

SANDBOX_DIR = Path(__file__).resolve().parent / "sandbox"

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Junior Engineer",
    "GIT_AUTHOR_EMAIL": "engineer@example.com",
    "GIT_COMMITTER_NAME": "Junior Engineer",
    "GIT_COMMITTER_EMAIL": "engineer@example.com",
}


def _remove_readonly(func, path, excinfo):
    """Clear the readonly bit and re-attempt removal (needed for Windows git packs)."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Runs a git command inside the designated sandbox folder."""
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        env=GIT_ENV,
        check=True,
        capture_output=True,
        text=True,
    )


def setup_sandbox(target_dir: Path = SANDBOX_DIR) -> Path:
    """
    Initializes a fresh Git sandbox with starter files and initial commits.
    """
    if target_dir.exists():
        shutil.rmtree(target_dir, onerror=_remove_readonly)

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Initialize fresh local git repository
    run_git(["init", "-b", "main"], cwd=target_dir)

    # Configure local repo credentials
    run_git(["config", "user.name", "Junior Engineer"], cwd=target_dir)
    run_git(["config", "user.email", "engineer@example.com"], cwd=target_dir)

    # 2. Commit 1: Project Scaffold (README)
    readme = target_dir / "README.md"
    readme.write_text(
        "# Inventory Service API\n\nA lightweight HTTP microservice for inventory tracking.\n",
        encoding="utf-8",
    )
    run_git(["add", "README.md"], cwd=target_dir)
    run_git(["commit", "-m", "chore: initial project scaffold"], cwd=target_dir)

    # 3. Commit 2: Application Entrypoint (app.py)
    app_py = target_dir / "app.py"
    app_py.write_text(
        '"""Core inventory application module."""\n\n'
        'def get_inventory():\n'
        '    return [\n'
        '        {"id": 1, "sku": "ELEC-01", "name": "Wireless Mouse", "stock": 45},\n'
        '        {"id": 2, "sku": "ELEC-02", "name": "Mechanical Keyboard", "stock": 18},\n'
        '    ]\n\n'
        'if __name__ == "__main__":\n'
        '    print("Inventory Service started.")\n'
        '    for item in get_inventory():\n'
        '        print(f"[{item[\'sku\']}] {item[\'name\']} - Stock: {item[\'stock\']}")\n',
        encoding="utf-8",
    )
    run_git(["add", "app.py"], cwd=target_dir)
    run_git(["commit", "-m", "feat: implement get_inventory endpoint"], cwd=target_dir)

    # 4. Commit 3: Configuration Template (config.json)
    config_json = target_dir / "config.json"
    config_json.write_text(
        '{\n'
        '  "service_name": "inventory-api",\n'
        '  "port": 8080,\n'
        '  "log_level": "INFO"\n'
        '}\n',
        encoding="utf-8",
    )
    run_git(["add", "config.json"], cwd=target_dir)
    run_git(["commit", "-m", "feat: add application configuration template"], cwd=target_dir)

    return target_dir


if __name__ == "__main__":
    print(f"Setting up Git Basics sandbox at:\n  {SANDBOX_DIR}")
    repo_path = setup_sandbox(SANDBOX_DIR)
    log_res = run_git(["log", "--oneline"], cwd=repo_path)
    print("\nInitial Commit History in Sandbox:")
    print(log_res.stdout.strip())
    print("\nSandbox is ready for practice!")

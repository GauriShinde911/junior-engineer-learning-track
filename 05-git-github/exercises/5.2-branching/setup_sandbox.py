"""
5.2 Branching: setup_sandbox.py
Initializes a throwaway Git repository at exercises/5.2-branching/sandbox/
containing a baseline Python calculator library ready for feature branch workflows.
"""

from pathlib import Path
import os
import shutil
import stat
import subprocess

SANDBOX_DIR = Path(__file__).resolve().parent / "sandbox"

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Junior Engineer",
    "GIT_AUTHOR_EMAIL": "engineer@example.com",
    "GIT_COMMITTER_NAME": "Junior Engineer",
    "GIT_COMMITTER_EMAIL": "engineer@example.com",
}


def _remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        env=GIT_ENV,
        check=True,
        capture_output=True,
        text=True,
    )


def setup_sandbox(target_dir: Path = SANDBOX_DIR) -> Path:
    """Creates a base git repo with a calculator module ready for branch workflows."""
    if target_dir.exists():
        shutil.rmtree(target_dir, onerror=_remove_readonly)

    target_dir.mkdir(parents=True, exist_ok=True)

    # Initialize git repo
    run_git(["init", "-b", "main"], cwd=target_dir)
    run_git(["config", "user.name", "Junior Engineer"], cwd=target_dir)
    run_git(["config", "user.email", "engineer@example.com"], cwd=target_dir)

    # Base Files
    (target_dir / "README.md").write_text(
        "# Math Utilities Library\n\nStandard mathematical operations service.\n",
        encoding="utf-8",
    )

    (target_dir / "calculator.py").write_text(
        '"""Basic arithmetic module."""\n\n'
        'def add(a: float, b: float) -> float:\n'
        '    """Returns the sum of two numbers."""\n'
        '    return a + b\n\n'
        'def subtract(a: float, b: float) -> float:\n'
        '    """Returns the difference of two numbers."""\n'
        '    return a - b\n',
        encoding="utf-8",
    )

    (target_dir / "test_calculator.py").write_text(
        '"""Unit tests for calculator operations."""\n'
        'from calculator import add, subtract\n\n'
        'def test_addition():\n'
        '    assert add(2, 3) == 5\n'
        '    assert add(-1, 1) == 0\n\n'
        'def test_subtraction():\n'
        '    assert subtract(10, 4) == 6\n\n'
        'if __name__ == "__main__":\n'
        '    test_addition()\n'
        '    test_subtraction()\n'
        '    print("All initial tests passed.")\n',
        encoding="utf-8",
    )

    # Commit baseline
    run_git(["add", "."], cwd=target_dir)
    run_git(["commit", "-m", "chore: initial baseline math library"], cwd=target_dir)

    return target_dir


if __name__ == "__main__":
    print(f"Setting up Branching sandbox at:\n  {SANDBOX_DIR}")
    repo_path = setup_sandbox(SANDBOX_DIR)
    log_res = run_git(["log", "--oneline"], cwd=repo_path)
    print("\nInitial State on 'main':")
    print(log_res.stdout.strip())
    print("\nSandbox is ready for feature branching practice!")

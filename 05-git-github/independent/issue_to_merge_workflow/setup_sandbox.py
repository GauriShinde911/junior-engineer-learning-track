"""
independent/issue_to_merge_workflow/setup_sandbox.py
Initializes a throwaway Git sandbox repository at:
independent/issue_to_merge_workflow/sandbox/

The sandbox simulates a real backend codebase where you pick up Issue #87
(Rate Limiter), branch, implement, test, and practice the full merge workflow.
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
    """Creates a realistic starting codebase repo for the full issue-to-merge workflow."""
    if target_dir.exists():
        shutil.rmtree(target_dir, onerror=_remove_readonly)

    target_dir.mkdir(parents=True, exist_ok=True)

    # Init repo
    run_git(["init", "-b", "main"], cwd=target_dir)
    run_git(["config", "user.name", "Junior Engineer"], cwd=target_dir)
    run_git(["config", "user.email", "engineer@example.com"], cwd=target_dir)

    # Commit 1: Project scaffold
    (target_dir / "README.md").write_text(
        "# API Gateway Service\n\nCore request routing and middleware pipeline.\n",
        encoding="utf-8",
    )
    run_git(["add", "README.md"], cwd=target_dir)
    run_git(["commit", "-m", "chore: initial API gateway project scaffold"], cwd=target_dir)

    # Commit 2: Existing auth middleware (peer code context)
    (target_dir / "auth.py").write_text(
        '"""Authentication middleware placeholder."""\n\n'
        'def validate_token(token: str) -> bool:\n'
        '    """Stub: validate API bearer token."""\n'
        '    return bool(token and len(token) > 10)\n',
        encoding="utf-8",
    )
    run_git(["add", "auth.py"], cwd=target_dir)
    run_git(["commit", "-m", "feat: stub JWT token validation middleware"], cwd=target_dir)

    # Commit 3: Empty placeholder for rate limiter (Issue #87 starting point)
    (target_dir / "rate_limiter.py").write_text(
        '"""Rate limiter module.\n\nIssue #87: Implement sliding window rate limiter.\nThis file is the starting point — implementation required.\n"""\n',
        encoding="utf-8",
    )
    (target_dir / "test_rate_limiter.py").write_text(
        '"""Tests for rate_limiter.py.\n\nIssue #87: Add tests covering allowed/blocked/window-reset cases.\n"""\n',
        encoding="utf-8",
    )
    run_git(["add", "rate_limiter.py", "test_rate_limiter.py"], cwd=target_dir)
    run_git(["commit", "-m", "chore: scaffold rate_limiter module stubs for Issue #87"], cwd=target_dir)

    return target_dir


if __name__ == "__main__":
    print(f"Setting up Issue-to-Merge workflow sandbox at:\n  {SANDBOX_DIR}")
    repo_path = setup_sandbox(SANDBOX_DIR)
    log_res = run_git(["log", "--oneline"], cwd=repo_path)
    print("\nInitial Commit History:")
    print(log_res.stdout.strip())
    print("\nSandbox ready — open SCENARIO.md and follow the README to begin!")

"""
tests/test_setup_scripts.py

Pytest suite that verifies each subsection's setup_sandbox.py initializes a
valid Git repository with the expected state.  All sandboxes are created in a
temp directory — none are placed inside the outer tracked repo.
"""

import os
import stat
import subprocess
import tempfile
from pathlib import Path

import pytest

EXERCISES_DIR = Path(__file__).resolve().parent.parent / "exercises"
INDEPENDENT_DIR = Path(__file__).resolve().parent.parent / "independent"

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test Runner",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test Runner",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def _remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def run_git(args: list, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        env=GIT_ENV,
        check=True,
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# 5.1 Git Basics
# ---------------------------------------------------------------------------

class TestGitBasicsSandbox:
    def test_setup_creates_git_repo(self, tmp_path):
        import importlib.util

        script = EXERCISES_DIR / "5.1-git-basics" / "setup_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_51", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_51"
        mod.setup_sandbox(sandbox)

        assert (sandbox / ".git").is_dir(), "Expected a .git directory"

    def test_setup_has_initial_commits(self, tmp_path):
        import importlib.util

        script = EXERCISES_DIR / "5.1-git-basics" / "setup_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_51_b", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_51b"
        mod.setup_sandbox(sandbox)

        result = run_git(["log", "--oneline"], cwd=sandbox)
        commits = result.stdout.strip().splitlines()
        assert len(commits) >= 1, f"Expected at least 1 commit, got: {commits}"

    def test_sandbox_is_on_main_branch(self, tmp_path):
        import importlib.util

        script = EXERCISES_DIR / "5.1-git-basics" / "setup_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_51_c", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_51c"
        mod.setup_sandbox(sandbox)

        result = run_git(["branch", "--show-current"], cwd=sandbox)
        assert result.stdout.strip() == "main"


# ---------------------------------------------------------------------------
# 5.2 Branching
# ---------------------------------------------------------------------------

class TestBranchingSandbox:
    def test_setup_creates_git_repo(self, tmp_path):
        import importlib.util

        script = EXERCISES_DIR / "5.2-branching" / "setup_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_52", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_52"
        mod.setup_sandbox(sandbox)

        assert (sandbox / ".git").is_dir()

    def test_sandbox_starts_on_main_for_practice(self, tmp_path):
        """5.2 sandbox intentionally starts with only main — learner creates feature branches."""
        import importlib.util

        script = EXERCISES_DIR / "5.2-branching" / "setup_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_52_b", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_52b"
        mod.setup_sandbox(sandbox)

        # The learner creates branches themselves; sandbox correctly starts on main
        result = run_git(["branch", "--show-current"], cwd=sandbox)
        assert result.stdout.strip() == "main"

        log = run_git(["log", "--oneline"], cwd=sandbox)
        assert len(log.stdout.strip().splitlines()) >= 1, "Expected at least 1 baseline commit"


# ---------------------------------------------------------------------------
# 5.5 Conflict Resolution
# ---------------------------------------------------------------------------

class TestConflictSandbox:
    def test_conflict_sandbox_creates_repo(self, tmp_path):
        import importlib.util

        script = EXERCISES_DIR / "5.5-conflict-resolution" / "setup_conflict_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_55", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_55"
        # 5.5 uses setup_conflict_sandbox() as its entry point
        mod.setup_conflict_sandbox(sandbox)

        assert (sandbox / ".git").is_dir()

    def test_conflict_sandbox_has_at_least_two_branches(self, tmp_path):
        import importlib.util

        script = EXERCISES_DIR / "5.5-conflict-resolution" / "setup_conflict_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_55_b", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_55b"
        mod.setup_conflict_sandbox(sandbox)

        result = run_git(["branch", "--list"], cwd=sandbox)
        branches = [b.strip().lstrip("* ") for b in result.stdout.strip().splitlines() if b.strip()]
        assert len(branches) >= 2, f"Expected at least 2 branches, got: {branches}"


# ---------------------------------------------------------------------------
# Independent: Issue-to-Merge Workflow
# ---------------------------------------------------------------------------

class TestIndependentSandbox:
    def test_sandbox_creates_repo(self, tmp_path):
        import importlib.util

        script = INDEPENDENT_DIR / "issue_to_merge_workflow" / "setup_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_ind", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_ind"
        mod.setup_sandbox(sandbox)

        assert (sandbox / ".git").is_dir()

    def test_sandbox_has_rate_limiter_stub(self, tmp_path):
        import importlib.util

        script = INDEPENDENT_DIR / "issue_to_merge_workflow" / "setup_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_ind_b", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_ind_b"
        mod.setup_sandbox(sandbox)

        assert (sandbox / "rate_limiter.py").exists(), "rate_limiter.py stub missing"
        assert (sandbox / "test_rate_limiter.py").exists(), "test_rate_limiter.py stub missing"

    def test_sandbox_has_three_commits(self, tmp_path):
        import importlib.util

        script = INDEPENDENT_DIR / "issue_to_merge_workflow" / "setup_sandbox.py"
        spec = importlib.util.spec_from_file_location("setup_ind_c", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sandbox = tmp_path / "sandbox_ind_c"
        mod.setup_sandbox(sandbox)

        result = run_git(["log", "--oneline"], cwd=sandbox)
        commits = result.stdout.strip().splitlines()
        assert len(commits) == 3, f"Expected exactly 3 commits in independent sandbox, got: {commits}"

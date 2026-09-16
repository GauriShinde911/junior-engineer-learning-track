"""
5.5 Conflict Resolution: setup_conflict_sandbox.py
Initializes a sandbox Git repository containing two divergent branches that
deliberately modify the same lines of code in pricing.py, setting up a realistic
merge conflict scenario for hands-on resolution.
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


def setup_conflict_sandbox(target_dir: Path = SANDBOX_DIR) -> Path:
    """Sets up a Git repo with two conflicting branches off a shared baseline."""
    if target_dir.exists():
        shutil.rmtree(target_dir, onerror=_remove_readonly)

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Initialize repo
    run_git(["init", "-b", "main"], cwd=target_dir)
    run_git(["config", "user.name", "Junior Engineer"], cwd=target_dir)
    run_git(["config", "user.email", "engineer@example.com"], cwd=target_dir)

    # 2. Base commit on main
    (target_dir / "README.md").write_text(
        "# E-Commerce Pricing Service\n\nCalculates discounts and order totals.\n",
        encoding="utf-8",
    )

    base_pricing = (
        '"""E-commerce pricing calculation engine."""\n\n'
        'def calculate_discount(order_total: float, customer_tier: str) -> float:\n'
        '    """Calculates final discounted price based on customer membership."""\n'
        '    discount_rate = 0.0\n'
        '    # --- TIER DISCOUNT LOGIC START ---\n'
        '    if customer_tier == "standard":\n'
        '        discount_rate = 0.0\n'
        '    elif customer_tier == "member":\n'
        '        discount_rate = 0.05\n'
        '    # --- TIER DISCOUNT LOGIC END ---\n\n'
        '    discount_amount = round(order_total * discount_rate, 2)\n'
        '    return round(order_total - discount_amount, 2)\n'
    )
    (target_dir / "pricing.py").write_text(base_pricing, encoding="utf-8")

    test_pricing = (
        '"""Unit tests for pricing calculations."""\n'
        'from pricing import calculate_discount\n\n'
        'def test_standard():\n'
        '    assert calculate_discount(100.0, "standard") == 100.0\n\n'
        'def test_member():\n'
        '    assert calculate_discount(100.0, "member") == 95.0\n\n'
        'if __name__ == "__main__":\n'
        '    test_standard()\n'
        '    test_member()\n'
        '    print("Base tests passed.")\n'
    )
    (target_dir / "test_pricing.py").write_text(test_pricing, encoding="utf-8")

    run_git(["add", "."], cwd=target_dir)
    run_git(["commit", "-m", "chore: initial pricing engine and tests"], cwd=target_dir)

    # 3. Branch A: feature/vip-loyalty (adds VIP tier)
    run_git(["switch", "-c", "feature/vip-loyalty"], cwd=target_dir)
    vip_pricing = (
        '"""E-commerce pricing calculation engine."""\n\n'
        'def calculate_discount(order_total: float, customer_tier: str) -> float:\n'
        '    """Calculates final discounted price based on customer membership."""\n'
        '    discount_rate = 0.0\n'
        '    # --- TIER DISCOUNT LOGIC START ---\n'
        '    if customer_tier == "vip":\n'
        '        discount_rate = 0.20\n'
        '    elif customer_tier == "member":\n'
        '        discount_rate = 0.08\n'
        '    elif customer_tier == "standard":\n'
        '        discount_rate = 0.0\n'
        '    # --- TIER DISCOUNT LOGIC END ---\n\n'
        '    discount_amount = round(order_total * discount_rate, 2)\n'
        '    return round(order_total - discount_amount, 2)\n'
    )
    (target_dir / "pricing.py").write_text(vip_pricing, encoding="utf-8")
    run_git(["add", "pricing.py"], cwd=target_dir)
    run_git(["commit", "-m", "feat: add VIP tier (20%) and update member discount to 8%"], cwd=target_dir)

    # 4. Branch B: feature/seasonal-promo (adds Holiday tier on conflicting lines)
    run_git(["switch", "main"], cwd=target_dir)
    run_git(["switch", "-c", "feature/seasonal-promo"], cwd=target_dir)
    promo_pricing = (
        '"""E-commerce pricing calculation engine."""\n\n'
        'def calculate_discount(order_total: float, customer_tier: str) -> float:\n'
        '    """Calculates final discounted price based on customer membership."""\n'
        '    discount_rate = 0.0\n'
        '    # --- TIER DISCOUNT LOGIC START ---\n'
        '    if customer_tier == "holiday_special":\n'
        '        discount_rate = 0.25\n'
        '    elif customer_tier == "member":\n'
        '        discount_rate = 0.10\n'
        '    elif customer_tier == "standard":\n'
        '        discount_rate = 0.02\n'
        '    # --- TIER DISCOUNT LOGIC END ---\n\n'
        '    discount_amount = round(order_total * discount_rate, 2)\n'
        '    return round(order_total - discount_amount, 2)\n'
    )
    (target_dir / "pricing.py").write_text(promo_pricing, encoding="utf-8")
    run_git(["add", "pricing.py"], cwd=target_dir)
    run_git(["commit", "-m", "feat: add holiday_special tier (25%) and promo member rate (10%)"], cwd=target_dir)

    # 5. Return to main
    run_git(["switch", "main"], cwd=target_dir)

    return target_dir


if __name__ == "__main__":
    print(f"Setting up Conflict Resolution sandbox at:\n  {SANDBOX_DIR}")
    repo_path = setup_conflict_sandbox(SANDBOX_DIR)
    branches = run_git(["branch", "-a"], cwd=repo_path)
    print("\nCreated Branches in Sandbox:")
    print(branches.stdout.strip())
    print("\nReady! Check EXERCISE.md for conflict reproduction and resolution steps.")

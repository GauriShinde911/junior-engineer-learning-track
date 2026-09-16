# Exercise 5.1: Git Basics — Hands-On Practice

In this exercise, you will practice fundamental Git operations using a local throwaway sandbox.

> **Safety Warning**: Run all `git` commands in this exercise **strictly inside** the sandbox directory:
> `cd exercises/5.1-git-basics/sandbox`
> Never run practice commands in the outer repository!

---

## Step 0: Initialize the Sandbox

Generate a fresh sandbox repository:

```bash
python exercises/5.1-git-basics/setup_sandbox.py
cd exercises/5.1-git-basics/sandbox
```

Verify you are inside the sandbox with:
```bash
git status
git log --oneline
```
You should see `main` branch with three initial commits.

---

## Step 1: Inspect Status and Diffs

1. Open `app.py` in your editor and add a new helper function:
   ```python
   def get_item_by_sku(sku: str):
       for item in get_inventory():
           if item["sku"] == sku:
               return item
       return None
   ```
2. Check your working tree status:
   ```bash
   git status
   ```
   Notice that `app.py` is listed under **"Changes not staged for commit"**.
3. View unstaged line differences:
   ```bash
   git diff
   ```
   Green lines starting with `+` show your added lines.

---

## Step 2: Stage and Commit Changes

1. Stage `app.py` to the index:
   ```bash
   git add app.py
   ```
2. Re-check status:
   ```bash
   git status
   ```
   Notice that `app.py` is now under **"Changes to be committed"**.
3. View staged changes:
   ```bash
   git diff --staged
   ```
4. Commit your staged changes with a descriptive conventional commit message:
   ```bash
   git commit -m "feat: add get_item_by_sku lookup helper"
   ```
5. Verify the new commit in the log:
   ```bash
   git log --oneline -n 2
   ```

---

## Step 3: Create, Switch, and Merge a Feature Branch

1. Create and switch to a new branch called `feature/health-check`:
   ```bash
   git switch -c feature/health-check
   # (or: git checkout -b feature/health-check)
   ```
2. Append a health check function to `app.py`:
   ```python
   def health_check():
       return {"status": "ok", "uptime_seconds": 120}
   ```
3. Stage and commit on your branch:
   ```bash
   git add app.py
   git commit -m "feat: implement service health check route"
   ```
4. Switch back to the `main` branch:
   ```bash
   git switch main
   ```
5. Inspect `app.py` — notice that `health_check()` is not here because it only exists on your feature branch.
6. Merge your feature branch into `main`:
   ```bash
   git merge feature/health-check
   ```
   Git performs a Fast-Forward merge since `main` had no diverging commits.
7. Inspect the formatted commit tree:
   ```bash
   git log --graph --oneline --all
   ```

---

## Step 4: Deliberate Mistake & Safe Recovery

Mistakes happen constantly in daily development. Practice recovering from two common mistakes.

### Scenario A: Unstaging an Accidental Staged File
1. Create an unintended temporary scratch file:
   ```bash
   echo "SECRET_API_KEY=12345" > .env.secret
   git add .env.secret
   git status
   ```
2. You realize `.env.secret` should never be committed! Unstage it without losing the file content:
   ```bash
   git restore --staged .env.secret
   git status
   ```
   The file is safely unstaged. You can now delete it or add it to `.gitignore`.

### Scenario B: Undoing a Bad Commit (Keeping Your Code)
1. Make a quick change in `config.json` (e.g., change port to `9999`) and accidentally commit it to `main`:
   ```bash
   git commit -am "test: bad port change that broke local testing"
   git log --oneline -n 2
   ```
2. You need to undo that commit, but you don't want to destroy the code edits you made:
   ```bash
   git reset --soft HEAD~1
   ```
3. Run `git status`:
   The bad commit has disappeared from git history, but your changes are safely preserved in your staging area ready to be adjusted or discarded cleanly!
4. Discard the unstaged experiment:
   ```bash
   git restore config.json
   git status
   ```
   Working tree is completely clean again.

---

## Step 5: Verification Checklist

- [ ] Ran `git status` before and after staging.
- [ ] Practiced `git diff` and `git diff --staged`.
- [ ] Created and switched branches using `git switch -c`.
- [ ] Merged a feature branch into `main`.
- [ ] Successfully recovered from a bad commit using `git reset --soft HEAD~1`.

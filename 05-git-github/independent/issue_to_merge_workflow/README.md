# Issue-to-Merge Workflow: Independent Challenge

Practice the complete professional engineering workflow — from reading a GitHub Issue to merging a reviewed Pull Request — using only the team practices covered in subsections 5.1–5.5.

---

## Start Here

### 1. Read the Scenario
Open [`SCENARIO.md`](./SCENARIO.md) and read **Issue #87** fully. Understand:
- What is the `RateLimiter` class expected to do?
- What are the exact acceptance criteria?
- What are the test requirements?

### 2. Initialize the Sandbox Repo
```bash
python 05-git-github/independent/issue_to_merge_workflow/setup_sandbox.py
cd 05-git-github/independent/issue_to_merge_workflow/sandbox
```

---

## The Full Workflow (No Shortcuts)

### Phase 1: Branch Off Main
Create a feature branch following the convention `feat/<issue-id>-<short-description>`:
```bash
git switch -c feat/87-sliding-window-rate-limiter
```

### Phase 2: Implement in Small Commits

Build the implementation in two atomic commits — don't commit everything at once:

**Commit 1** — Core data structure and `is_allowed` method:
```bash
git add rate_limiter.py
git commit -m "feat(#87): implement RateLimiter sliding window core logic"
```

**Commit 2** — Tests covering all acceptance criteria scenarios:
```bash
git add test_rate_limiter.py
git commit -m "test(#87): add unit tests for allowed, blocked, and window-reset cases"
```

Verify tests pass in the sandbox:
```bash
python test_rate_limiter.py
```

### Phase 3: Keep Branch Current With Main
Simulate a teammate pushing a hotfix to `main` while you were working:
```bash
git switch main
echo "Fixed auth token length check." >> auth.py
git add auth.py
git commit -m "fix: improve auth token validation edge case"
git switch feat/87-sliding-window-rate-limiter
```

Now rebase your feature branch onto the latest `main`:
```bash
git rebase main
git log --graph --oneline -n 6
```

Verify tests still pass after rebase:
```bash
python test_rate_limiter.py
```

### Phase 4: Prepare & Open Pull Request (On a Real Remote)
If you have pushed this sandbox to GitHub:

1. Push the branch:
   ```bash
   git push -u origin feat/87-sliding-window-rate-limiter
   ```
2. Open a PR using the template from `exercises/5.3-pull-requests/PR_TEMPLATE.md`:
   - **Title**: `feat(#87): Implement sliding window rate limiter`
   - **Closes**: `#87`
   - Fill out the **"How Was This Tested?"** section with actual test output.
3. Request a peer review.

### Phase 5: Simulate a Review Comment & Revision

Your reviewer requests: *"Please add a docstring to `is_allowed` explaining the sliding window semantics."*

1. Open `rate_limiter.py` and add a detailed docstring.
2. Amend or add a new commit:
   ```bash
   git add rate_limiter.py
   git commit -m "docs(#87): add sliding window semantics docstring to is_allowed"
   git push origin feat/87-sliding-window-rate-limiter
   ```
3. Reply to the reviewer thread: *"Updated in latest commit — docstring now explains window eviction behavior."*
4. The reviewer approves.

### Phase 6: Merge & Cleanup

1. On GitHub, select **"Squash and Merge"**, confirm the squashed commit title is clean.
2. Click **"Delete branch"** on GitHub.
3. Locally, clean up:
   ```bash
   git switch main
   git pull origin main
   git branch -d feat/87-sliding-window-rate-limiter
   ```

---

## Definition of Done

You have successfully completed this challenge when:

- [ ] `rate_limiter.py` fully implements the `RateLimiter` class per `SCENARIO.md` acceptance criteria.
- [ ] `test_rate_limiter.py` tests pass: below-limit allowed, over-limit blocked, window-elapsed reset.
- [ ] Feature branch was rebased onto `main` before opening the PR.
- [ ] PR description references `Closes #87` and includes test evidence.
- [ ] Review comment was addressed in a separate follow-up commit.
- [ ] Branch was merged via Squash and Merge and deleted.

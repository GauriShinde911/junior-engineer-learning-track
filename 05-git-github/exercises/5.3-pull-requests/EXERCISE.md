# Exercise 5.3: The Professional Pull Request & Code Review Workflow

A Pull Request (PR) is not just a mechanism to merge code — it is an asynchronous peer review, automated testing gate, and architectural checkpoint before code enters production.

This exercise guides you through the full GitHub PR lifecycle.

---

## Phase 1: Branch Creation & Pushing to Remote

1. Ensure your local `main` branch is up to date with the remote:
   ```bash
   git switch main
   git pull origin main
   ```
2. Create a feature branch matching your team's naming convention (`feat/<short-description>` or `fix/<ticket-id>`):
   ```bash
   git switch -c feat/jwt-authentication
   ```
3. Implement your changes, add tests, and commit with meaningful messages:
   ```bash
   git add auth.py test_auth.py
   git commit -m "feat: implement JWT token generation and validation"
   ```
4. Push your branch to the remote repository, setting upstream tracking:
   ```bash
   git push -u origin feat/jwt-authentication
   ```

---

## Phase 2: Opening the Pull Request on GitHub

1. Navigate to your repository on GitHub. A prompt will appear: **"Compare & pull request"**.
2. **Base vs. Compare**:
   - `base`: `main` (the target branch receiving the code).
   - `compare`: `feat/jwt-authentication` (your feature branch).
3. **Fill out the PR description using `PR_TEMPLATE.md`**:
   - Title: `feat: Add JWT authentication and token validation middleware`
   - Link the issue: `Closes #42` (automatically closes the issue when merged!).
   - Detail the changes, test results, and check all boxes in the checklist.
4. If the work is still in progress, select **"Create Draft Pull Request"**. Once ready for review, click **"Ready for review"**.
5. Assign at least one teammate as a **Reviewer**.

---

## Phase 3: Continuous Integration (CI) Checks

Modern engineering teams run automated GitHub Actions workflows on every PR:
- Linting / Formatting (`flake8`, `black`, `ruff`)
- Automated Unit & Integration Tests (`pytest`)
- Security / Vulnerability Scans

Never merge a PR when CI checks are failing (red status indicator).

---

## Phase 4: Navigating the Code Review Process

Reviewers can submit three types of feedback:
1. **Comment**: General question or non-blocking suggestion (e.g., *"Consider renaming `tok` to `access_token` for clarity."*).
2. **Request Changes**: Critical issue or bug identified that must be resolved before merging.
3. **Approve**: Code satisfies standards and is cleared to merge.

### Responding to Review Comments Professionally
- Acknowledge feedback with curiosity, not defensiveness.
- If you agree: Make the code revision locally, commit it, and reply to the comment: *"Updated in commit abc1234."*
- If you disagree: Explain the engineering rationale politely with examples or benchmarks.

### Committing the Fix & Pushing Revisions
```bash
# Make requested changes in auth.py
git add auth.py
git commit -m "refactor: rename tok parameter to access_token per review"
git push origin feat/jwt-authentication
```
GitHub automatically updates the open Pull Request with your new commit. Mark the review thread as **"Resolved"**.

---

## Phase 5: Merging Strategies & Branch Cleanup

Once your PR has approved reviews and all green CI checks:

| Merge Strategy | What It Does | When To Use It |
|---|---|---|
| **Create a Merge Commit** (`--no-ff`) | Preserves every single commit + creates an explicit merge commit. | Complex multi-week features where individual commit history is vital. |
| **Squash and Merge** | Collapses all 5-10 feature commits into a single clean commit on `main`. | **Industry standard** for standard features and bug fixes; keeps `main` history clean. |
| **Rebase and Merge** | Replays individual commits onto `main` with no merge commit. | Teams that mandate a strict linear history with curated commits. |

1. Select **"Squash and Merge"** on GitHub.
2. Ensure the squashed commit title matches the feature title.
3. Confirm merge.
4. Click **"Delete branch"** to delete the remote feature branch.
5. Clean up your local environment:
   ```bash
   git switch main
   git pull origin main
   git branch -d feat/jwt-authentication
   ```

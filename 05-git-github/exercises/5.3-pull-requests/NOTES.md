# 5.3 Pull Requests & Code Review

A Pull Request (PR) is a GitHub mechanism proposing that changes from a feature branch be merged into a target base branch, providing a forum for automated testing, security scanning, and peer code review.

## Key Concepts & Terminology

- **Base Branch**: The target branch receiving changes (usually `main` or `develop`).
- **Compare Branch**: The feature/bugfix branch containing your new commits.
- **Draft PR**: A work-in-progress PR that notifies teammates of ongoing work while preventing premature merges.
- **CI Status Checks**: Automated pipeline jobs (tests, linters, security audits) that must pass before merging.
- **Squash and Merge**: Condenses all individual branch commits into one clean commit on the base branch.
- **Rebase and Merge**: Fast-forwards commits onto the base branch without creating a merge commit.
- **Closes #Issue**: Magic keyword in a PR description that automatically closes the referenced issue upon merge.

## Core Theory: What Makes a Great Pull Request?

1. **Small, Atomic Scope**: A PR should address one specific problem or feature. Smaller PRs (< 300 lines of diff) receive faster, more thorough code reviews and carry significantly lower regression risk.
2. **Contextual Description**: Reviewers cannot read your mind. A great PR answers: *What problem does this solve? Why this technical approach? How can a reviewer verify it works?*
3. **Reproducible Test Proof**: Include automated test passes or explicit manual test steps so reviewers can verify behavior without guessing.

## Practical Implementation

In this folder, `PR_TEMPLATE.md` provides a standardized template with checklists and test proof sections. `EXERCISE.md` walks through the entire lifecycle: pushing branches, opening PRs, responding to review comments, selecting merge strategies, and post-merge branch pruning.

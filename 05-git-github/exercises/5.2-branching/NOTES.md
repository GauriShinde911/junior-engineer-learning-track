# 5.2 Branching Strategies

In Git, a branch is simply a lightweight, movable 41-byte pointer to a specific commit hash. Creating or switching branches is instantaneous because no file duplication occurs.

## Key Commands & Syntax

- `git branch`: Lists existing local branches and indicates current active branch.
- `git switch -c <name>`: Creates a new branch and checks it out in one step (replaces `git checkout -b`).
- `git merge <branch>`: Integrates changes from target branch into current branch.
- `git merge --no-ff <branch>`: Forces creation of an explicit merge commit even when fast-forward is possible.
- `git rebase <upstream>`: Replays commits from the current branch on top of the latest commit of `<upstream>`.
- `git branch -d <name>`: Safely deletes a merged branch; use `-D` to force delete an unmerged branch.

## Core Theory: Merge vs. Rebase

- **Merge (`git merge`)**: Preserves the complete, exact chronological history and true branching structure. It joins two diverging lines of development with a diamond-shaped merge commit.
- **Rebase (`git rebase`)**: Rewrites local commit hashes to place your commits sequentially after the tip of `main`. It creates a clean, linear project timeline without cluttering history with merge commits.
- **Golden Rule of Rebasing**: Never rebase a public branch that has been pushed and shared with other developers. Only rebase private, local feature branches before integrating into `main`.

## Practical Implementation

In this folder, `setup_sandbox.py` initializes a math utility library. `EXERCISE.md` walks through creating three feature branches, committing atomic changes, merging using `--no-ff`, and synchronizing a lagging feature branch with `main` using `git rebase`.

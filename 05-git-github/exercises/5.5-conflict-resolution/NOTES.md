# 5.5 Conflict Resolution

A merge conflict occurs when Git performs a three-way merge (comparing the common ancestor, the current branch `HEAD`, and the incoming branch) and detects conflicting changes to the same lines of code that cannot be reconciled automatically.

## Key Commands & Conflict Syntax

- `git merge <branch>`: Initiates the integration; triggers conflict state if divergent lines overlap.
- `git status`: Identifies files flagged as `both modified` awaiting resolution.
- `git merge --abort`: Safely cancels the merge operation and resets working files back to pre-merge `HEAD`.
- `git checkout --ours <file>`: Selects current branch version for binary or complete-file overrides.
- `git checkout --theirs <file>`: Selects incoming branch version for complete-file overrides.
- `git add <file>`: Marks the resolved file as reconciled in the staging index.

## Core Theory: How Conflict Markers Work

When a conflict occurs, Git writes three delimiter markers directly into the affected file:
1. `<<<<<<< HEAD`: Code currently residing on your checked-out branch.
2. `=======`: Center separator dividing the two competing modifications.
3. `>>>>>>> <branch-name>`: Code coming from the branch being merged in.

Resolving a conflict requires reading both code paths, understanding the product intent of each branch, editing the file into a unified working solution, removing all three marker lines, and running tests before committing.

## Practical Implementation

In this folder, `setup_conflict_sandbox.py` initializes two branches (`feature/vip-loyalty` and `feature/seasonal-promo`) modifying identical discount calculation lines in `pricing.py`. `EXERCISE.md` walks through triggering the conflict, breaking down the conflict markers, synthesizing both discount tiers, verifying with unit tests, and finalizing the merge commit.

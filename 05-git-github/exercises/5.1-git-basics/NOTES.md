# 5.1 Git Basics

Git is a distributed version control system that models code history as a Directed Acyclic Graph (DAG) of immutable snapshots.

## Key Commands & Syntax

- `git status`: Displays the state of the working directory and the staging area.
- `git add <file>`: Copies modifications from the working directory into the staging area (index).
- `git commit -m "<msg>"`: Packages staged changes into a new immutable commit snapshot.
- `git diff`: Shows unstaged differences between the working tree and the index.
- `git diff --staged`: Shows changes between the staging area and the most recent commit (`HEAD`).
- `git log --oneline --graph`: Renders a compact, graphical overview of the commit history.
- `git restore --staged <file>`: Removes a file from the staging area without modifying disk content.
- `git reset --soft HEAD~1`: Moves the branch pointer back by one commit while keeping code staged.

## Core Theory: Git's Three-Tree Architecture

Git organizes every repository into three distinct conceptual trees:
1. **Working Directory**: The actual sandbox files on your local file system that you edit.
2. **Staging Area (Index)**: The preparation buffer where you selectively organize changes before committing.
3. **Commit History (HEAD)**: The permanent, cryptographic record of committed snapshots.

Understanding these three stages enables atomic commits — staging only relevant files for a specific feature while leaving unfinished experiments unstaged in the working directory.

## Practical Implementation

In this folder, `setup_sandbox.py` creates an isolated local repository with multiple historical commits. `EXERCISE.md` guides you through inspecting working tree diffs, creating branches, performing fast-forward merges, and recovering from accidental staging or bad commits with `git restore` and `git reset`.

# 05. Git & GitHub Workflow — Module Overview & Index

This skill folder covers disciplined software collaboration habits with Git and GitHub: building a clean version-controlled commit history, managing feature branches, contributing code through Pull Requests, organizing work through GitHub Issues, and resolving merge conflicts with engineering judgment.

---

## Curriculum Index & Subsection Overviews

1. [**5.1 Git Basics**](exercises/5.1-git-basics/NOTES.md)
   The three-tree architecture (working directory → staging area → commit history), core commands for inspecting and saving changes, creating branches, and safely recovering from common mistakes.

2. [**5.2 Branching**](exercises/5.2-branching/NOTES.md)
   Feature branch naming conventions, atomic multi-commit development, keeping branches synchronized with `main` via `git rebase`, and clean merge strategies using `--no-ff`.

3. [**5.3 Pull Requests**](exercises/5.3-pull-requests/NOTES.md)
   The professional PR lifecycle — description standards, CI gate requirements, code review etiquette, responding to review comments, and merge strategy selection.

4. [**5.4 Issues**](exercises/5.4-issues/NOTES.md)
   Translating ambiguous product requirements into actionable GitHub Issues using user stories, acceptance criteria checklists, vertical slicing, and definition-of-done contracts.

5. [**5.5 Conflict Resolution**](exercises/5.5-conflict-resolution/NOTES.md)
   Understanding Git's three-way merge model, reading conflict markers, synthesizing divergent intents without blindly accepting one side, and validating resolutions with tests.

- [**Independent Challenge: Issue-to-Merge Workflow**](independent/issue_to_merge_workflow/README.md)
  Practices the complete engineering lifecycle end-to-end: read an issue, create a feature branch, implement in atomic commits, rebase onto `main`, open a PR, address a review comment, squash-merge, and clean up.

---

## Key Principles This Skill Reinforces

- **Never commit directly to `main`** in a shared team repo. All work goes through feature branches and Pull Requests.
- **Commit messages are permanent communication**. A clear `feat:`, `fix:`, `refactor:` prefix plus a concise description saves your future teammates hours of archaeological guessing.
- **Small PRs merge faster**. A PR touching 10 files rarely gets a thorough review. A PR touching 2 files almost always does.
- **Resolving conflicts requires engineering judgment** — understanding why each diverging change was made before deciding how to integrate them cleanly.

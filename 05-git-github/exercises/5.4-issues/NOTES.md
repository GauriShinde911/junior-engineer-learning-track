# 5.4 Issue Management & Task Decomposition

GitHub Issues serve as the single source of truth for planning, tracking bugs, and decomposing product requirements into small, independently deliverable engineering tasks.

## Key Concepts & Conventions

- **User Story**: A requirement formulated from the user's perspective: *"As a [user], I want [goal], so that [benefit]."*
- **Acceptance Criteria (AC)**: Concrete, binary checklist (`- [ ]`) specifying exactly what must be true for the issue to be considered complete.
- **Labels**: Categorization tags (`bug`, `enhancement`, `security`, `priority:high`) that power project filtering and triage.
- **Milestones**: Target release dates or sprint boundaries grouping related issues together.
- **Definition of Done (DoD)**: Team-wide agreements on quality standards (e.g., code reviewed, tests passing, documentation updated).

## Core Theory: Vertical Slicing vs. Horizontal Layers

- **Horizontal Slicing (Avoid)**: Creating monolithic tasks like *"Build entire database"* or *"Build entire frontend"*. These block other developers and delay feedback until the very end.
- **Vertical Slicing (Preferred)**: Slicing requirements into thin, end-to-end features delivering working functionality (e.g., Issue #1: CSV export, Issue #2: Excel report). Vertical slices are testable, can be deployed incrementally, and allow multiple engineers to work concurrently without merge bottlenecks.

## Practical Implementation

In this folder, `ISSUE_TEMPLATE.md` provides a standardized template enforcing acceptance criteria and DoD. `example_requirement_to_issues.md` demonstrates how to break down a vague reporting request into four actionable, parallelizable engineering issues.

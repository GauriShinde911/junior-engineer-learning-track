# Junior Engineer Learning Track

Standalone, self-driven programming curriculum — independent of any customer or company project.
Goal: go from **Learned → Project Ready → Independent** across 13 core engineering skills, proven through real code, tests, and documentation (not tutorials).

---

## How This Repo Is Organized

Each folder below is one skill. Inside each folder you'll find your practice exercises, the independent challenge for that skill, and a short `README.md` explaining what you built.

```
junior-engineer-learning-track/
├── 01-python-fundamentals/
├── 02-oop-modular-design/
├── 03-pandas-excel/
├── 04-sqlite/
├── 05-git-github/
├── 06-pytest-testing/
├── 07-rest-api/
├── 08-authentication-security/
├── 09-streamlit/
├── 10-debugging-logging/
├── 11-windows-packaging/
├── 12-documentation/
└── capstone-asset-tracker/     <- final project combining everything
```

Each skill folder follows the same simple layout:
```
0X-skill-name/
├── exercises/          <- guided practice programs
├── independent/        <- the unassisted challenge for this skill
├── tests/               <- pytest tests
└── README.md            <- what this skill covers + how to run the code
```

---

## Progress Tracker

Progress for each skill is tracked in **`Junior_Programming_Training_Tracker.xlsx`** (kept outside this repo, or linked here if you choose to include it), using three levels:

| Level | Meaning |
|---|---|
| **Learned** | Understand the concept, can complete guided exercises |
| **Project Ready** | Can apply the skill in a real codebase following existing standards |
| **Independent** | Can design, implement, test, debug, and explain the skill without step-by-step help |

A skill is only marked complete once its **Independent Challenge** is done unassisted, with working tests, a README, and (where possible) a mentor review — not just because a tutorial was followed.

---

## Skills Covered

1. Python Fundamentals
2. OOP & Modular Design
3. Pandas & Excel
4. SQLite
5. Git & GitHub Workflow
6. pytest & Testing
7. REST / API Integration
8. Authentication & Security
9. Streamlit
10. Debugging & Logging
11. Windows Packaging
12. Documentation
13. **Capstone:** Asset Request & Tracking App (combines all of the above)

---

## Submission Standard (applies to every skill folder)

- All exercises committed to Git with meaningful commit messages
- Every mini-project includes source code, tests, a README, and setup instructions
- No secrets, passwords, or tokens ever committed to source code
- Code is formatted consistently with clear, meaningful names
- Every exercise includes at least one negative/error case
- Code and tests are run locally before requesting any review
- I can explain my own code line-by-line, at a high level, without notes

---

## How to Run Anything in This Repo

```bash
# clone the repo
git clone <repo-url>
cd junior-engineer-learning-track

# set up a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# install dependencies for a specific skill folder
pip install -r 0X-skill-name/requirements.txt

# run tests for a specific skill folder
pytest 0X-skill-name/tests/
```

---

## Status

| Skill | Level |
|---|---|
| Python Fundamentals | 🟡 In Progress |
| OOP & Modular Design | ⚪ Not Started |
| Pandas & Excel | ⚪ Not Started |
| SQLite | ⚪ Not Started |
| Git & GitHub Workflow | ⚪ Not Started |
| pytest & Testing | ⚪ Not Started |
| REST / API Integration | ⚪ Not Started |
| Authentication & Security | ⚪ Not Started |
| Streamlit | ⚪ Not Started |
| Debugging & Logging | ⚪ Not Started |
| Windows Packaging | ⚪ Not Started |
| Documentation | ⚪ Not Started |
| Capstone | ⚪ Not Started |

*(Update this table as you progress — 🟡 In Progress, 🟢 Learned, 🔵 Project Ready, ✅ Independent)*

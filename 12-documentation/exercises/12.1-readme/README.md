# Daily Task Tracker CLI (`sample_app`)

A lightweight, zero-dependency command-line utility for tracking daily personal tasks, setting priorities, and managing workflow completion.

---

## 1. Purpose

The Daily Task Tracker provides engineers and individual contributors with a frictionless, offline command-line interface to capture and organize ad-hoc tasks without requiring a web browser, external database, or third-party cloud service. Data is stored locally in clean JSON format for portability and easy scripting.

---

## 2. Prerequisites

Before installing and running this application, ensure your environment meets the following requirements:

- **Operating System**: Windows 10/11, macOS (10.15+), or Linux (Ubuntu 20.04+, Debian, Fedora, Arch).
- **Python**: Python 3.8 or higher. Check your version with:
  ```bash
  python --version
  # or on Unix/macOS:
  python3 --version
  ```
- **External Dependencies**: None. This application relies exclusively on the Python standard library (`argparse`, `json`, `pathlib`, `datetime`).

---

## 3. Installation

1. **Clone or navigate to the repository**:
   ```bash
   git clone https://github.com/GauriShinde911/junior-engineer-learning-track.git
   cd junior-engineer-learning-track/12-documentation/exercises/12.1-readme/sample_app
   ```

2. **Verify direct execution**:
   Run the CLI directly using the Python interpreter:
   ```bash
   python main.py --help
   ```

---

## 4. Configuration

The application works out of the box with default settings, but supports custom data file storage via environment variables:

| Setting / Variable | Default Value | Description |
|---|---|---|
| `TASK_TRACKER_DATA` | `tasks.json` (in current working directory) | Absolute or relative file path where tasks are stored as JSON. |

### Setting a Custom Storage Path

- **Linux / macOS (Bash / Zsh)**:
  ```bash
  export TASK_TRACKER_DATA="$HOME/.tasks.json"
  ```
- **Windows (PowerShell)**:
  ```powershell
  $env:TASK_TRACKER_DATA = "$HOME\.tasks.json"
  ```
- **Windows (Command Prompt)**:
  ```cmd
  set TASK_TRACKER_DATA=%USERPROFILE%\.tasks.json
  ```

---

## 5. Usage & Run Commands

The CLI provides three primary subcommands: `add`, `list`, and `complete`.

### Adding a Task

Syntax:
```bash
python main.py add "<task title>" [--priority {low,medium,high}]
```

Examples:
```bash
# Add a task with default medium priority
python main.py add "Submit Q3 engineering quarterly report"

# Add a high-priority task
python main.py add "Fix memory leak in ingestion service" --priority high

# Add a low-priority task
python main.py add "Update team onboarding documentation" --priority low
```

Output:
```text
[OK] Added task #1: 'Submit Q3 engineering quarterly report' (priority: medium)
[OK] Added task #2: 'Fix memory leak in ingestion service' (priority: high)
```

---

### Listing Tasks

Syntax:
```bash
# List active (pending) tasks
python main.py list

# List all tasks including completed ones
python main.py list --all
```

Output:
```text
ID   Status     Priority   Title                          Created
---------------------------------------------------------------------------
1    Pending    medium     Submit Q3 engineering quarter  2026-09-26 14:00:00
2    Pending    high       Fix memory leak in ingestion   2026-09-26 14:02:15
```

---

### Completing a Task

Syntax:
```bash
python main.py complete <task-id>
```

Example:
```bash
python main.py complete 1
```

Output:
```text
[OK] Task #1 marked as completed.
```

If the specified ID does not exist:
```text
[ERROR] Task #99 not found.
```
(Exits with non-zero status code `1`).

---

## 6. Troubleshooting & Common Questions

- **Where is my data stored?**  
  By default, `tasks.json` is created in the directory from which you executed `python main.py`. If you want persistence across different terminal directories, set the `TASK_TRACKER_DATA` environment variable to an absolute path.
- **Can I edit the data file manually?**  
  Yes. The file is standard formatted JSON. Ensure you maintain valid JSON syntax (matching brackets, quoted strings) when making manual edits.

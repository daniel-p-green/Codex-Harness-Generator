# Getting Started

Open Codex in this project, ask for a source-backed summary, and verify that the assistant separates evidence from inference. The permission profile allows workspace edits while denying secrets and private keys.

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only"
```


# Getting Started

Open Codex in this project, ask for a small verified change, and verify the assistant can run tests. The permission profile allows workspace edits while denying secrets and private keys.

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only"
```

Then summarize task-trial outcomes:

```bash
python scripts/summarize-task-trials.py
```


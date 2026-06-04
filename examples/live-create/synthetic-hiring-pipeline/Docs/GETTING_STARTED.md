# Getting Started

Open Codex in this project and ask for a scorecard note from synthetic hiring
materials. This harness is for public-safe hiring-pipeline examples only.

## First Task

1. Add or inspect a synthetic role and candidate-evidence file.
2. Ask Codex to write `reports/hiring-scorecard-note.md`.
3. Verify the note includes source scope, role requirements, structured
   criteria, scorecard evidence, bias and privacy checks, and a human-review
   boundary.

The permission profile allows workspace edits while denying secrets, tokens,
credentials, `.env` files, and private keys.

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only"
```

Then summarize task-trial outcomes:

```bash
python scripts/summarize-task-trials.py
```


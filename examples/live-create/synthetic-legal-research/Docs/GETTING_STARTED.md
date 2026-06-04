# Getting Started

Open Codex in this project and ask for a source-backed note from synthetic legal
or policy excerpts. This harness is for public-safe legal-research examples
only.

## First Task

1. Add or inspect a synthetic source file.
2. Ask Codex to write `reports/legal-research-note.md`.
3. Verify the note includes jurisdiction, source citations, uncertainty, and a
   not-legal-advice boundary.

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


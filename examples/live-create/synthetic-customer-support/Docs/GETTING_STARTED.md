# Getting Started

Open Codex in this project and ask for a support escalation note from synthetic
ticket and policy materials. This harness is for public-safe customer-support
examples only.

## First Task

1. Add or inspect synthetic ticket and policy files.
2. Ask Codex to write `reports/support-escalation-note.md`.
3. Verify the note includes source scope, grounded claims, `[VERIFY]` gaps,
   `[PROPOSED]` commitments, privacy checks, and escalation or human-review
   paths.

The permission profile allows workspace edits while denying secrets, tokens,
credentials, `.env` files, and private keys.

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only"
```


# Getting Started

Open Codex in this project and ask for a scenario note from synthetic financial
assumptions. This harness is for public-safe financial-modeling examples only.

## First Task

1. Add or inspect a synthetic assumptions file.
2. Ask Codex to write `reports/financial-scenario-note.md`.
3. Verify the note includes source scope, assumptions, scenarios, risk,
   uncertainty, sensitivity, and a not-financial-advice boundary.

The permission profile allows workspace edits while denying secrets, tokens,
credentials, `.env` files, and private keys.

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only"
```


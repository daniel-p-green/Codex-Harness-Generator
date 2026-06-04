# Getting Started

Open Codex in this project and ask for a safe review of a synthetic source file.
This harness is for public-safe security-audit examples only.

## First Task

1. Add or inspect a synthetic source file.
2. Ask Codex to write `reports/security-review.md`.
3. Verify every finding names the affected path, evidence, risk, and safe
   remediation.

The permission profile allows workspace edits while denying secrets, tokens,
credentials, `.env` files, and private keys.

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only"
```


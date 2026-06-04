# Getting Started

Open Codex in this project and ask for a small verified task. This
harness expects the assistant to inspect files before editing, avoid secrets, and
verify work with the narrowest meaningful check.

## First Checks

1. Run `/health-check` to verify the harness structure.
2. Ask Codex to map datasets, schemas, and pipeline entry points.
3. Ask for a small data-contract or validation check.
4. Ask the reviewer to inspect data quality and backfill risk.

The permission profile allows workspace edits while denying secrets, tokens,
credentials, private keys, and `.env` files.

You can also run the local smoke check without the generator repo:

```bash
python scripts/check-harness.py
```

When a repeated issue appears, record it in the local improvement log:

```bash
python scripts/record-improvement.py --category CHECK_GAP --task "short task" --friction "what went wrong" --evidence "file or command evidence"
```

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only"
```

Then summarize task-trial outcomes:

```bash
python scripts/summarize-task-trials.py
```

Run the copied-harness eval report:

```bash
python scripts/run-harness-evals.py
```

Generated: 2026-06-04

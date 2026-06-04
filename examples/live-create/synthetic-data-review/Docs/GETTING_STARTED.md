# Getting Started

This harness helps Codex work with a public-safe synthetic data analysis workspace: checking CSV quality, summarizing weekly metrics, and drafting lightweight chart-ready report notes.

## Start A Session

1. Open a terminal in `temporary synthetic target`.
2. Run `codex`.
3. Ask for a concrete task, such as "check `data/raw/example.csv` for quality issues."
4. Let Codex inspect the file and verify counts before it summarizes.

## Available Commands

- `/data-quality-check` - inspect a CSV for parse errors, columns, nulls, duplicates, and date coverage.
- `/summarize-week` - compute a weekly metric summary from synthetic CSV data.
- `/chart-notes` - draft chart titles, caveats, and takeaways from verified metrics.
- `/state-save` - save current progress in `Docs/_working/state/`.
- `/state-load` - resume saved progress and check for drift.

## Suggested First Tasks

- "Check the CSV files in `data/raw/` and tell me what looks risky."
- "Create a weekly summary from this synthetic metrics CSV."
- "Turn this verified weekly summary into chart-ready notes."

## Permissions

The config allows local workspace reads/writes needed for synthetic data, docs, and report outputs. It denies common secret, token, credential, and key patterns.

## Monitoring And Optimizing Costs

Use `/cost` for cost awareness during longer report sessions. Keep raw data and generated exports out of version control when they are large or temporary. RTK is optional for reducing repeated token load; markdown docs and the gitignore rules cover the normal workflow.

## How It Improves

Repeated lessons go into `Docs/_working/retro/`. When enough useful patterns accumulate, Codex should recommend updating the harness rules or skills.

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only"
```


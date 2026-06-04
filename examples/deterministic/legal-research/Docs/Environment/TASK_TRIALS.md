# Task Trials

Use this file to record whether the generated harness helps Codex complete real
legal research tasks. This is separate from `IMPROVEMENT_LOG.md`: task trials
capture task outcome evidence, while improvement entries capture harness-change
ideas from repeated friction.

Append entries manually or with:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only" --limitations "one task, not longitudinal proof"
```

Summarize recorded trials with:

```bash
python scripts/summarize-task-trials.py
```

Run the copied-harness eval summary with:

```bash
python scripts/run-harness-evals.py
```

Export a public-safe usage report draft after at least one successful real task.
Use the matching pilot slug when one exists:

```bash
python scripts/export-public-usage-report.py --title "Public-safe usage title" --slug "public-safe-usage-slug" --out Docs/Environment/PUBLIC_USAGE_REPORT.md
```

## Outcome Labels

- `success`: Codex completed the task and verification passed.
- `partial`: Codex helped materially, but some work, review, or data remained.
- `failed`: Codex did not complete the task usefully.
- `inconclusive`: The task did not provide enough evidence to judge usefulness.

## Entry Template

```text
Date:
Task:
Outcome: success | partial | failed | inconclusive
Evidence:
Verification:
Privacy review:
Harness helped:
Limitations:
```

## Review Rule

Only treat a trial as product evidence when it names concrete evidence,
verification, privacy review, and limitations. Do not paste secrets, raw private
logs, personal data, customer data, candidate data, private repository names,
email addresses, or local machine paths.

## Entries

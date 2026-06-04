# Getting Started

Open Codex in this project and ask for a small verified task. This harness
expects the assistant to inspect files before editing, avoid secrets, and verify
work with the narrowest meaningful check.

## First Checks

1. Run `/health-check` to verify the harness structure.
2. Ask Codex to identify datasets, scripts, and output reports.
3. Ask for a metric definition map before changing analysis logic.
4. Ask the reviewer to inspect reproducibility and unsupported claims.

The permission profile allows workspace edits while denying secrets, tokens,
credentials, private keys, and `.env` files.

You can also run the local smoke check without the generator repo:

```bash
python scripts/check-harness.py
```

## First Useful Task Loop

Use this loop for the first real data analysis task so the harness produces
evidence, not just a successful setup check.

1. Pick a small task with a visible artifact, file change, or source-backed
   answer.
2. Ask Codex to inspect the relevant files and state the planned verification
   before it edits or summarizes.
3. Complete the task, then run the narrowest meaningful check.
4. Ask the reviewer to inspect correctness, privacy, safety, regressions, and
   missing verification before finalizing.
5. Record the result in `Docs/Environment/TASK_TRIALS.md`.
6. Run the copied-harness eval report and decide whether any repeated friction
   belongs in `Docs/Environment/IMPROVEMENT_LOG.md`.

Good first-task evidence is concrete: a changed file, generated report, command
output, source comparison, or reviewer finding. Do not record raw secrets,
personal data, private repository names, email addresses, local machine paths,
customer data, candidate data, proprietary source, or raw private logs.

## Verification Menu

Start with the checks below, then add project-specific commands to
`Docs/Environment/EVAL_PLAN.md` after the first useful task.

- Run the narrowest analysis script, notebook check, or test available.
- Inspect input schemas and row counts before changing calculations.
- State metric definitions, denominators, exclusions, and data limits.

## Evidence Commands

When a repeated issue appears, record it in the local improvement log:

```bash
python scripts/record-improvement.py --category CHECK_GAP --task "short task" --friction "what went wrong" --evidence "file or command evidence"
```

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only" --limitations "one task, not longitudinal proof"
```

Then summarize task-trial outcomes:

```bash
python scripts/summarize-task-trials.py
```

Summarize the improvement backlog:

```bash
python scripts/summarize-improvements.py
```

Run the copied-harness eval report:

```bash
python scripts/run-harness-evals.py
```

After a successful real task trial, export a public-safe usage report draft.
Use the matching pilot slug when one exists:

```bash
python scripts/export-public-usage-report.py --slug "public-safe-usage-slug" --out Docs/Environment/PUBLIC_USAGE_REPORT.md
```

If this harness came from the public generator and the task is safe to describe,
share only the exported public usage report, local eval summary, task-trial
summary, privacy review, and limitations. Keep raw private evidence out of
public reports.

Generated: 2026-06-04

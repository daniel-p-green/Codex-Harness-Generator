# Next Task Trial

Use this file when a reporter or teammate asks, "What do I actually do first?"
It is the shortest path from a generated Codex harness to public-safe evidence
that a maintainer can inspect.

## Pick The Task

Choose one small real or synthetic-safe knowledge work task with a visible artifact or
answer. Good candidates:

- Ask Codex to map the key docs and their roles.
- Ask for a concise source-backed summary of one folder.
- Ask the reviewer to check whether the summary overclaims.

Avoid tasks that require secrets, personal data, customer data, candidate data,
private repository names, raw logs, or irreversible production actions.

## Run The Loop

1. Ask Codex to inspect the relevant files before changing or summarizing them.
2. Ask Codex to state the planned verification before it edits or summarizes.
3. Complete the task and run the narrowest meaningful check.
4. Ask the reviewer to inspect correctness, privacy, safety, regressions, and
   missing verification.
5. Record the trial with `python scripts/record-task-trial.py`.
6. Run `python scripts/run-harness-evals.py --min-successes 1`.
7. Export `Docs/Environment/PUBLIC_USAGE_REPORT.md` with
   `python scripts/export-public-usage-report.py --out Docs/Environment/PUBLIC_USAGE_REPORT.md`.

## Copyable Record Command

```bash
python scripts/record-task-trial.py \
  --task "short public-safe task summary" \
  --outcome success \
  --evidence "public-safe artifact, file, command, or source comparison" \
  --verification "command, reviewer pass, source check, or manual inspection" \
  --privacy-review "no secrets, personal data, private repo names, local paths, or raw private logs included" \
  --harness-helped "what the generated harness made easier" \
  --limitations "one task trial, not longitudinal proof"
```

## Evidence Boundary

Share the exported public usage report, local eval status, and task-trial
summary. Do not share raw private files, secrets, personal data, customer data,
candidate data, private repository names, email addresses, local machine paths,
or raw private logs.

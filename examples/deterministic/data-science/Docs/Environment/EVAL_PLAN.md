# Eval Plan

This plan defines the first project-specific checks to run after the generated
Codex harness is copied into a real workspace. It complements the structural
health check in `scripts/check-harness.py`.

## Success Criteria

- Codex inspects the relevant files before editing or summarizing.
- Codex follows the data science verification rules in `AGENTS.md`.
- The reviewer agent catches correctness, privacy, safety, regression, and
  missing-verification risks before work is called done.
- The final response names any skipped checks, missing data, unresolved
  assumptions, or remaining risk.

## Smoke Checks

1. Ask Codex to map datasets, notebooks, scripts, and reports.
2. Ask for a metric and leakage-risk review.
3. Ask the reviewer to inspect reproducibility and unsupported conclusions.

## Acceptance Checks

Use these checks to verify task work before calling it done:

- Inspect data splits, metric definitions, and leakage risks before changing analysis.
- Run the narrowest reproducible notebook, script, or test check available.
- Report assumptions, confidence limits, sample size, and assessment caveats.

## Reviewer Check

Ask Codex to run the reviewer on one non-trivial completed task. The review
passes only if it cites the files, commands, or source artifacts it inspected and
leads with bugs, regressions, privacy/safety issues, and missing tests or checks.

## Regression Checks

- Re-run `python scripts/check-harness.py` after modifying harness files.
- Re-run the narrowest project command used for the task after changing source
  or deliverable files.
- Update this eval plan when the project adds a new test runner, build command,
  external service, compliance requirement, or recurring failure mode.

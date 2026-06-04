# Eval Plan

This plan defines the first project-specific checks to run after the generated
Codex harness is copied into a real workspace. It complements the structural
health check in `scripts/check-harness.py`.

## Success Criteria

- Codex inspects the relevant files before editing or summarizing.
- Codex follows the social media verification rules in `AGENTS.md`.
- The reviewer agent catches correctness, privacy, safety, regression, and
  missing-verification risks before work is called done.
- The final response names any skipped checks, missing data, unresolved
  assumptions, or remaining risk.

## Smoke Checks

1. Ask Codex to map campaign briefs, source assets, and channels.
2. Ask for one channel-specific post set.
3. Ask the reviewer to inspect claim accuracy and brand fit.

## Acceptance Checks

Use these checks to verify task work before calling it done:

- Check source material, claims, dates, and channel constraints before drafting posts.
- Keep public-facing copy grounded and avoid unsupported product or event claims.
- Mark approvals, assets, and scheduling assumptions before publishing.

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

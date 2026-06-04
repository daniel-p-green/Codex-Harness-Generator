# Hiring Pipeline Workspace Codex Harness

This Codex harness supports hiring-pipeline, job, rubric, interview, and candidate-evidence support work. Verify live file state before
editing, run the narrowest meaningful check, and report any skipped verification.

## Defaults

- Prefer simple, maintainable code with clear names.
- Do not read secrets, tokens, private keys, credential files, or `.env` files.
- Treat security and privacy issues as high priority.
- Ask for clarification when correctness, data loss, or privacy depends on
  missing context.
- Run tests when they exist; otherwise use source checks, dry runs, or the
  narrowest runnable command.
- Use the reviewer for non-trivial changes before calling work done.
- Record repeated workflow friction in `Docs/Environment/IMPROVEMENT_LOG.md`
  before changing harness behavior.

## Verification

- Fix structured criteria, rubric, and scorecard anchors before evaluating evidence.
- Map every criterion to job-related requirements and avoid protected-class proxies.
- State decision support only; human reviewers own adverse decisions.

## Domain Guidance

- Mitigate bias, discrimination, and fairness risks; do not use protected class traits or proxies.
- Use structured criteria, rubrics, scorecards, and job-related evidence only.
- Protect candidate privacy, candidate data, personal data, and PII; never automate screen-outs, rankings, rejections, or adverse actions without human review.

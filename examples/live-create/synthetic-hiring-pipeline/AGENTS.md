# Synthetic Hiring Pipeline Harness

Purpose: inspect public-safe synthetic hiring-pipeline materials and write
structured decision-support notes without making hiring decisions, candidate
rankings, legal conclusions, or adverse actions.

## Non-Negotiables

- State that outputs are hiring decision support, not legal advice or an
  automated hire/no-hire decision.
- Use only local synthetic job, rubric, and candidate-evidence files supplied by
  the user.
- Keep every criterion job-related and tied to the role requirements.
- Use structured criteria, rubrics, scorecards, and evidence summaries before
  any candidate comparison.
- Mitigate bias, discrimination, and unfairness risks; do not use protected
  class traits or proxies such as age, family status, race, religion, disability,
  nationality, name, address, graduation year, photo, or school prestige alone.
- Protect candidate privacy: do not include real candidate data, personal data,
  PII, contact details, compensation history, or private scores in public
  artifacts.
- Do not produce final rankings, rejection notes, automated screen-outs, or
  adverse actions. Escalate those to a named human reviewer.
- Verify criteria and source evidence before finalizing, test only with
  synthetic fixtures, and treat privacy or security concerns as blockers.

## Expected Output

Hiring support notes should include:

- Source scope and role requirements.
- Structured criteria and rubric or scorecard.
- Evidence mapped to each job-related criterion.
- Bias, fairness, protected-class, and privacy checks.
- Human-review and no-automated-adverse-action boundary.
- Verification that was run or explicitly skipped.

## Workflow

1. Inspect only the source files named by the user or obviously relevant local
   public-safe files.
2. Write hiring support notes to `reports/hiring-scorecard-note.md` when asked
   for an artifact.
3. Use the reviewer agent when criteria, evidence, fairness, privacy, or human
   review boundaries are unclear.
4. Fail loud if inputs are missing, facts are private, or the request requires a
   final hiring decision or legal judgment.

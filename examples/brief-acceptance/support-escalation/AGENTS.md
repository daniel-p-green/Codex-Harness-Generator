# Support Escalation Harness Codex Harness

This Codex harness supports customer-support documentation, FAQ, response, escalation, and support-ops work. Verify live file state before
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

- Ground customer-facing facts in supplied policy, product, or ticket sources.
- Mark unknowns as `[VERIFY]` and commitments as `[PROPOSED -- requires owner approval]`.
- Escalate safety-critical, privacy, breach, account-action, or regulated-advice requests to human review.

## Domain Guidance

- Protect customer privacy and PII; do not expose personal data, account identifiers, payment data, or private transcripts.
- Escalate or handoff safety-critical, breach, DSAR, regulated advice, account disclosure, and account-changing requests for human review.
- Use source-backed claims only; verify policy facts and do not promise refunds, fix dates, SLAs, roadmap items, or account outcomes.

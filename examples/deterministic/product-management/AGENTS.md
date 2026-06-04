# Product Management Workspace Codex Harness

This Codex harness supports PRDs, roadmap, prioritization, stakeholder specs, and product planning work. Verify live file state before
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

- Map requirements back to user evidence, stakeholder notes, or product goals.
- Check acceptance criteria, scope boundaries, and tradeoffs before finalizing specs.
- Flag assumptions, unresolved decisions, and missing validation.

# Grant Writing Workspace Codex Harness

This Codex harness supports grant proposals, funding narratives, budgets, and submission packets. Verify live file state before
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

- Map proposal claims back to funder criteria and supplied source materials.
- Check budget figures, deadlines, and eligibility against source files.
- Flag missing attachments, unsupported claims, and owner-review needs.

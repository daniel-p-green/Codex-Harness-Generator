# Infrastructure Workspace Codex Harness

This Codex harness supports a local infrastructure or deployment workspace. Verify live file state before
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

## Verification

- Prefer dry-run, plan, lint, or validation commands before applying changes.
- Inspect target environment names before editing deployment files.
- Document rollback steps and commands that were not run.

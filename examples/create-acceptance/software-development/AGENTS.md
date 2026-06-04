# Minimal Python CLI Codex Harness

This Codex harness supports a small Python CLI utility. Verify live file state before
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

- Run `python -m pytest` when tests exist.
- Run the specific CLI command being changed when no tests exist.
- If no runnable check exists, explain that limitation plainly.

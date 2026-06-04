# Data Analysis Workspace Codex Harness

This Codex harness supports a local data analysis workspace with scripts, notebooks, and reports. Verify live file state before
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

- Run the narrowest analysis script, notebook check, or test available.
- Inspect input schemas and row counts before changing calculations.
- State metric definitions, denominators, exclusions, and data limits.

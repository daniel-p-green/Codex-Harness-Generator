# Data Engineering Workspace Codex Harness

This Codex harness supports data pipeline, schema, ETL, validation, and monitoring work. Verify live file state before
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

- Inspect schemas, contracts, row counts, and partition assumptions before changing pipelines.
- Run narrow validation, lint, or sample-data checks when available.
- State data quality limits, backfill risk, and rollback or replay requirements.

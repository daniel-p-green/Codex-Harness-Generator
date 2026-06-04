# Data Science Workspace Codex Harness

This Codex harness supports offline data science, model assessment, experiment, and research-analysis work. Verify live file state before
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

- Inspect data splits, metric definitions, and leakage risks before changing analysis.
- Run the narrowest reproducible notebook, script, or test check available.
- Report assumptions, confidence limits, sample size, and assessment caveats.

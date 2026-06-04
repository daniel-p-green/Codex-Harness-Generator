# Book Publishing Workspace Codex Harness

This Codex harness supports long-form manuscript editing, production, and publishing work. Verify live file state before
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

- Compare edits against the source manuscript before changing meaning.
- Check style, continuity, and chapter-level consistency.
- Mark publishing, rights, or distribution questions that need human review.

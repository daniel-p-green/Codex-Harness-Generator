---
name: audit-todos
description: Use when the user asks to inspect, test, debug, or improve Markdown TODO scanning, stale-item detection, date thresholds, parser edge cases, or CLI fixtures.
---

# Audit TODOs

Use this skill for Markdown TODO scanning work.

## Workflow

1. Inspect the CLI entry point, TODO parser, and existing tests or fixtures.
2. Identify the exact stale-TODO rule in use: age threshold, date format, completed marker handling, and ignored directories.
3. Add or update the smallest focused tests that prove the intended behavior.
4. Run the narrowest meaningful test command.
5. If user-facing output changes, run a synthetic CLI invocation and inspect the summary.

## Quality Bar

- Parsing is deterministic.
- Date handling is timezone-stable enough for the project default.
- Output uses relative paths and short snippets.
- No secrets or machine-local private paths appear in reports.

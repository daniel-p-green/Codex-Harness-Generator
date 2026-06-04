# Getting Started

This Codex harness is for a synthetic Python CLI that scans Markdown files for stale TODO items and writes a cleanup summary.

## First Checks

1. Open the project in the target directory.
2. Ask Codex to inspect the CLI files before editing.
3. For TODO logic changes, run focused tests first.
4. For report changes, run the CLI against public-safe fake Markdown fixtures and inspect the output.

## Permissions

The default permission profile keeps work inside the workspace and denies common secret-bearing files such as `.env`, token files, credential files, `.pem`, and `.key` files. Network access is disabled by default because this CLI should not need it.

## Common Tasks

- Fix stale TODO detection: use the `audit-todos` skill.
- Improve cleanup summary wording: use the `write-cleanup-summary` skill.
- Add a CLI flag: inspect the parser, update tests, then run a synthetic command.

## Verification

Use the smallest meaningful command for the task. To verify behavior changes, run a focused test plus a CLI invocation that writes a cleanup summary from synthetic Markdown.

## Cost And Context

The harness uses medium reasoning by default and enables agent teams only as an available mode for larger future investigations. For this small CLI, direct sequential work should usually be enough.

After a meaningful Codex task, record a task trial:

```bash
python scripts/record-task-trial.py --task "short task" --outcome success --evidence "artifact or file inspected" --verification "command or review completed" --privacy-review "public-safe summary only"
```


---
name: state-load
description: "Use when the user says resume, load saved progress, continue the weekly report, restore context, or check where we left off. Do not use for discovering unrelated files when no saved state exists."
---

## Critical

Check for drift before continuing. A saved CSV path or report note may be stale.

## Workflow

1. Read `Docs/_working/state/SESSION_CONTEXT.md` and `SESSION_SNAPSHOT.json`.
2. Verify referenced files still exist.
3. Compare modified times or visible contents when drift would affect the task.
4. Report what can be trusted, what changed, and the next safe action.

## Output

- Loaded task
- Referenced artifacts
- Drift check
- Blockers
- Recommended next step


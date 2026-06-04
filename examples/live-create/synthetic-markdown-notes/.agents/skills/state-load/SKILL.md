---
name: state-load
description: Use when the user says "resume", "load state", "continue where we left off", "/state-load", or asks what was happening in a prior synthetic documentation session. Do not use as a source of truth when current files conflict.
---

## Critical

Loaded state is a navigation aid, not authority. Always check current files before making claims or editing.

## Steps

1. Read `Docs/_working/state/SESSION_CONTEXT.md` if it exists.
2. Read `Docs/_working/state/SESSION_SNAPSHOT.json` if it exists and parses.
3. Verify referenced artifact paths still exist.
4. Check for newer files in `Inbox/`, `Outbox/`, `Docs/Areas/`, and `Docs/Decisions/`.
5. Report current task, last known files, decisions, blockers, and drift risks.

## Symmetry

Load the same six categories saved by `/state-save`: tool state, task state, artifact state, decision state, blocked state, and drift risk.

## Output

Return a concise resume note with verified paths and a short "needs refresh" section when drift is detected.

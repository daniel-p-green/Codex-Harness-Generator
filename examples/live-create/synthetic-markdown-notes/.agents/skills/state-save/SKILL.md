---
name: state-save
description: Use when the user says "save progress", "remember where we are", "pause this task", "/state-save", or before compaction in this synthetic documentation workspace. Do not use for permanent project decisions; write those to Docs/Decisions instead.
---

## Critical

This skill saves transient session context only. It must not store real personal data, secrets, credentials, or non-synthetic private details.

## Steps

1. Ensure `Docs/_working/state/` exists.
2. Read the current task context and identify the six categories below.
3. Write or update `Docs/_working/state/SESSION_CONTEXT.md`.
4. Write valid JSON to `Docs/_working/state/SESSION_SNAPSHOT.json`.
5. Prune session notes in `Docs/_working/sessions/` older than 30 days when safe.

## State Taxonomy

- Tool state: active files, validation commands run, conversion tools used.
- Task state: current user goal, requested output, intended audience.
- Artifact state: notes, decisions, plans, drafts, Inbox files, Outbox files.
- Decision state: chosen project direction, deferred options, rationale.
- Blocked state: missing source files, unclear owners, ambiguous dates.
- Drift risk: newer notes, changed plans, stale decisions, changed public-safety needs.

## Output

Report the two state paths written and any information deliberately omitted for safety.

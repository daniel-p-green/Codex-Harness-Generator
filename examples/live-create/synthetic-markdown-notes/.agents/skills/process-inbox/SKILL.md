---
name: process-inbox
description: Use when the user says "process Inbox", "clean these notes", "turn raw notes into docs", "/process-inbox", "summarize incoming files", or "make decisions from these notes". Do not use for files outside this synthetic workspace or for real private data.
---

## Critical

Only process public-safe synthetic files. If a file appears to contain real personal data, credentials, private links, or confidential business information, stop and ask the user how to sanitize it.

## Steps

1. List files in `Inbox/`.
2. Read only the files relevant to the user request.
3. Classify each item as meeting notes, decision input, project-plan input, or miscellaneous reference.
4. Produce Markdown outputs in `Outbox/` unless the user specified another path.
5. Preserve source filenames and uncertainty.
6. Reread outputs before reporting completion.

## Output Patterns

- Meeting summary: agenda, discussion, decisions, action items, open questions.
- Decision record: context, options, decision, rationale, consequences, follow-ups.
- Project plan update: goal, current status, milestones, risks, next actions.

## Output

Return files read, files written, verification performed, and any public-safety concerns.

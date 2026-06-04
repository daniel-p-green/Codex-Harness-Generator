# Orchestrator and Routing

Route work by intent, file evidence, and risk. Read only the files needed to decide the route, then either handle directly or delegate with a short written assignment.

## Context Discipline

The orchestrator may read `AGENTS.md`, files in `.codex/rules/`, `Docs/index.md`, `Docs/Environment/`, and the specific user-named notes, decisions, plans, Inbox files, or Outbox drafts. For large multi-file synthesis, delegate and require a disk-backed summary. Do not keep large source text in conversation when a file path and summary will do.

## Routing Table

| User intent | Complexity | Primary route | Fallback |
|---|---|---|---|
| "Summarize these meeting notes" | simple | Direct: read note files, extract agenda, decisions, action items | `drafter` if a polished brief is requested |
| "Find decisions about timeline" | standard | `researcher`: search `Docs/Decisions/` and notes for timeline references | Direct lookup if one file is named |
| "Draft a decision record" | standard | `drafter`: use source notes plus decision template | `reviewer` for public-safety pass |
| "Update the lightweight project plan" | standard | Direct edit after reading current plan and source notes | `drafter` if restructuring is needed |
| "Compare two project options" | standard | `researcher`: build evidence table from notes and decisions | `drafter` to turn result into memo |
| "Is this public-safe?" | standard | `reviewer`: scan for real personal data, private links, credentials, unsupported real-world claims | Direct if checking one short paragraph |
| "Process files in Inbox" | standard | `/process-inbox`: convert synthetic raw notes into Markdown outputs | Direct if one plain-text file |
| "Where is the latest status?" | simple | Direct: inspect `Docs/index.md`, `Docs/Areas/`, and recent Outbox drafts | `researcher` if status spans many files |
| "Fact-check this summary against notes" | standard | `reviewer`: compare output to cited source files | `researcher` if source files are unclear |
| "Prepare a stakeholder update" | standard | `drafter`: concise fake update with decisions, risks, next steps | `reviewer` for shareability check |
| "Recover prior session context" | simple | `/state-load`: read saved context and flag drift | Direct if no saved state exists |
| "Improve the harness behavior" | complex | `/update`: inspect retro patterns and propose minimal changes | `reviewer` for quality check |

Default posture: conservative for overwrites and external-facing drafts, proactive for reading, summarizing, and creating new synthetic files.

## Delegation Contract

Each delegation must include task, source paths, output format, target path if writing, and verification expectation. Agents must never speculate about files they have not read.

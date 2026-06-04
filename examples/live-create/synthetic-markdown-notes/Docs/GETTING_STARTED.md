# Getting Started

This environment helps Codex work with a synthetic documentation workspace: fake meeting notes, decisions, and lightweight project plans that are safe to use in public examples.

## Start a Session

1. Open a terminal in `temporary synthetic target`.
2. Run `codex`.
3. Ask for a concrete documentation task, such as summarizing notes or drafting a decision.
4. When Codex changes a file, ask it to verify the result or run `/health-check`.

## Commands

- `/state-save`: save progress before a pause or compaction.
- `/state-load`: resume from saved context and check whether files changed.
- `/update`: improve the harness from repeated retro notes.
- `/health-check`: verify setup, permissions, references, and safety basics.
- `/process-inbox`: process synthetic files in `Inbox/` into clean outputs in `Outbox/`.

## First Tasks

- Put a fake meeting note in `Inbox/` and ask: "Process Inbox into a meeting summary."
- Ask: "Draft a decision record from this note."
- Ask: "Review this Outbox draft for public-safe fake data."

## What This Assistant Can and Cannot Do

The assistant works with files in this local workspace. It cannot directly access Google Docs, Notion, calendars, or other web tools unless connectors are configured. For web-based materials, export or paste synthetic content into `Inbox/`, then move the generated result back manually.

## Verification and Permissions

The harness is allowed to write within the workspace but denies common sensitive paths such as secrets, tokens, credentials, `.env` files, and private keys. Use `/health-check` before sharing the workspace as a public example.

## File Processing

Use `Inbox/` for raw synthetic notes and `Outbox/` for generated summaries, decisions, and plan updates. Markdown is the default output format. Pandoc is optional if you later want formatted files.

## Monitoring and Optimizing Costs

This balanced setup uses higher reasoning for research/review and medium effort for drafting. Use `/cost` for awareness during longer sessions. RTK is optional for token reduction, and `.gitignore` already excludes transient `Docs/_working/` state.

## How It Improves

Repeated misses should be recorded in `Docs/_working/retro/`. Run `/update` when patterns accumulate so the harness can improve without adding unnecessary complexity.

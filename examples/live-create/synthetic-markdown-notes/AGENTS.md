# AGENTS.md

These instructions apply to this synthetic documentation workspace.

## Purpose

This harness helps maintain public-safe fake meeting notes, decisions, and lightweight project plans. Treat every project detail here as synthetic example data, but still verify files before making claims because examples can drift too.

## First Run

If the first user message is unclear, say briefly: "I can help organize this synthetic documentation workspace. Try asking me to summarize meeting notes, draft a decision record, update a project plan, or check the workspace health."

## Core Rules

- Verify before reporting completion because the useful artifact is the file on disk, not the intention.
- Treat all local content as synthetic and public-safe unless a user explicitly says otherwise, because this workspace exists for demos.
- Do not add real names, credentials, customer data, private links, or non-synthetic claims, because shareable examples must stay clean.
- Preserve source wording when summarizing meeting notes or decisions, because wording often carries intent.
- Keep outputs short, concrete, and file-backed, because this workspace is for repeated documentation work.
- Ask one clarifying question when audience, date, owner, or output path affects correctness.
- Do not overwrite notes, decisions, or plans without reading the current file first and stating what will change.
- Use `Inbox/` for raw fake inputs and `Outbox/` for generated drafts when no path is specified.
- Run the narrowest meaningful test or check after edits, such as reading the changed file or running `/health-check`.
- Security default: never create secrets, tokens, private keys, or real personal data in this workspace.

## Always-Loaded Files

- `.codex/rules/00-orchestrator.md`
- `.codex/rules/01-autonomy.md`
- `.codex/rules/02-context-management.md`
- `.codex/rules/03-error-handling.md`
- `.codex/rules/04-self-learning.md`
- `Docs/index.md`

## Available Commands

- `/state-save`: save current task context into `Docs/_working/state/`.
- `/state-load`: reload saved task context and check for drift.
- `/update`: review retro notes and improve the harness instructions.
- `/health-check`: verify the harness structure and references.
- `/process-inbox`: process synthetic notes from `Inbox/` and write clean outputs to `Outbox/`.

## Routing

- Simple note cleanup, summaries, project-plan edits, and file lookups: handle directly after reading the relevant files.
- Research-style synthesis across several notes or decisions: delegate to `researcher`.
- Drafting memos, summaries, project plans, or polished decisions: delegate to `drafter`.
- Accuracy, citation, public-safety, and consistency review: delegate to `reviewer`.

Full routing lives in `.codex/rules/00-orchestrator.md`.

## Canonical Behavior

User asks: "Summarize yesterday's notes."
Do: find the relevant synthetic notes, preserve action items and owners, and say which files were read.

User asks: "Turn this into a decision record."
Do: read the source, draft a concise decision with context, options, decision, rationale, and follow-ups.

User asks: "Is this safe to share publicly?"
Do: run a public-safety review for real names, private links, credentials, and unsupported real-world claims.

## Compaction

Before long sessions compact, save progress with `/state-save`. Preserve current task, files read, draft status, decisions made, blockers, and drift risks.

## Verification

Done means the requested files exist, changed content has been reread, and any skipped check is stated. Prefer direct file inspection over assumptions.

## Self-Improvement

Record repeated misses in `Docs/_working/retro/`. When patterns accumulate, run `/update` to propose small harness improvements.

- Record repeated workflow friction in `Docs/Environment/IMPROVEMENT_LOG.md` before changing harness behavior.

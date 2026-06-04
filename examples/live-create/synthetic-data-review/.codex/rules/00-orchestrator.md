# Orchestrator Routing

Default posture: proactive for local synthetic files, conservative for metric meaning. Act on file inspection and deterministic checks; ask before changing definitions or audience framing.

## Direct-Read Whitelist

The orchestrator may directly read `AGENTS.md`, `.codex/rules/*.md`, `Docs/index.md`, `Docs/GETTING_STARTED.md`, `Docs/Areas/*.md`, `Docs/Environment/*.md`, and small CSV headers/samples. Delegate broad CSV profiling, aggregation, and report drafting to the specialist assistants or skills.

## Routing Table

| User intent | Complexity | Primary route | Fallback |
|---|---:|---|---|
| "Check this CSV for quality issues" | standard | `csv-quality-analyst`; inspect schema, parseability, nulls, duplicates, date coverage | Run `/data-quality-check`, then summarize manually |
| "Why did this CSV fail to load?" | standard | `csv-quality-analyst`; reproduce parser error and isolate row/column cause | Ask for delimiter/encoding if file evidence is inconclusive |
| "Compare this week to last week" | standard | `weekly-metrics-summarizer`; verify date window and compute deltas | Ask for metric definitions if absent |
| "Summarize weekly metrics" | standard | `/summarize-week`; write `reports/weekly/` output | Delegate to `weekly-metrics-summarizer` for interpretation |
| "Make chart-ready notes" | standard | `report-note-writer`; convert verified metrics into title, caveats, takeaways | Use `/chart-notes` checklist |
| "What columns are in this dataset?" | simple | Inspect CSV header and `Docs/Areas/data-inventory.md` | Delegate to `csv-quality-analyst` for multi-file inventory |
| "Are there duplicate records?" | simple | Run deterministic duplicate check using likely key columns | Ask user to confirm key if none is obvious |
| "Can this be public?" | standard | Verify examples are synthetic and remove real-looking identifiers | Ask before publishing externally |
| "Update metric definitions" | complex | Ask for intended definition change, then update `Docs/Areas/metric-definitions.md` | Record a decision in `Docs/Decisions/` |
| "Create a report note from this CSV" | complex | `weekly-metrics-summarizer` for numbers, then `report-note-writer` for prose | Split into quality check first if the CSV is new |
| "Where is the latest summary?" | simple | Inspect `reports/weekly/` and `Docs/index.md` | Use `/state-load` if session state may know |
| "Save where we are" | simple | `/state-save` writes current task, artifacts, decisions, blockers, drift risks | Manually update state files if skill is unavailable |

## Handoff Contract

When delegating, provide the target path, relevant CSV/report paths, known metric definitions, and the exact output expected. Require the assistant to state files read, commands run, and verification result.

Self-learning: record repeated friction and user corrections in `Docs/Environment/IMPROVEMENT_LOG.md` before updating harness behavior.

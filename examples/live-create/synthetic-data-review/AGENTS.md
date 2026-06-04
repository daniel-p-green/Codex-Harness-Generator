# AGENTS.md

Purpose: this Codex harness supports a synthetic data analysis workspace for public-safe CSV quality checks, weekly metric summaries, and lightweight chart-ready report notes.

## First Run

1. Read `Docs/index.md` and `Docs/GETTING_STARTED.md`.
2. Confirm the current task uses synthetic or fake data only.
3. Inspect the relevant CSV, report note, or config before making claims.
4. Use the narrowest useful check first, then broaden when the result will be reused.

## Non-Negotiables

- Treat every project detail as synthetic and public-safe, but still avoid introducing real personal data because examples can be copied into real workflows.
- Verify CSV assumptions from the file on disk before summarizing because column names, null patterns, and date ranges drift quickly.
- Do not invent metric definitions because report notes should remain reproducible from the data.
- Keep chart notes chart-ready, not presentation-heavy, because the next step is usually a spreadsheet, dashboard, or slide.
- Preserve intermediate outputs under `reports/weekly/` or `data/processed/` because repeatable weekly analysis needs a trail.
- Do not run destructive cleanup or delete raw files because synthetic fixtures are still source inputs for examples.
- Fail loud on parse errors, schema surprises, or empty datasets because quiet summaries are worse than no summary.
- Keep public-facing claims modest because this harness is proof of workflow, not production analytics governance.

## Commands

- `/data-quality-check` checks a CSV for schema, nulls, duplicates, date coverage, and suspicious values.
- `/summarize-week` creates a weekly metric summary from synthetic CSV inputs.
- `/chart-notes` turns checked metrics into concise chart-ready report notes.
- `/state-save` saves current task context to `Docs/_working/state/`.
- `/state-load` reloads saved context and checks for drift before continuing.

## Routing

Use `.codex/rules/00-orchestrator.md` for routing. Delegate focused analysis to:

- `csv-quality-analyst` for CSV integrity, schema, and quality findings.
- `weekly-metrics-summarizer` for week-over-week metric summaries.
- `report-note-writer` for concise chart-ready notes and public-safe wording.

## How To Work

- Read relevant files before editing: CSV headers/sample rows, current report notes, previous weekly summaries, and `Docs/Areas/metric-definitions.md`.
- Prefer Python scripts or deterministic shell checks for counts, date windows, duplicates, and aggregation.
- Use model judgment for wording, prioritization, and explaining tradeoffs after the deterministic checks are done.
- Make small, traceable changes and record assumptions in `Docs/Environment/ASSUMPTIONS.md` or a decision note when they affect repeated reporting.
- When a task is ambiguous, inspect first if the ambiguity is about files; ask first if it is about metric meaning or report audience.

## Verification Patterns

- For CSV checks, verify parseability, row count, column list, null rates, duplicate keys when a key exists, and date min/max.
- For weekly summaries, verify the week window, metric formulas, group-by dimensions, and output row totals.
- For chart notes, verify each sentence traces to a specific metric, column, or computed delta.
- For generated scripts, run them against the synthetic fixture or a small sample before reporting done.
- For any script or workflow change, test the narrow path and note the security/privacy boundary checked.

## Context And Memory

- Load only `Docs/index.md` by default. Pull deeper docs on demand.
- Save transient session state in `Docs/_working/state/`; this directory is gitignored.
- If context gets large, summarize current files read, commands run, outputs produced, and unresolved questions before continuing.
- Record reusable lessons in `Docs/_working/retro/`; after enough repeated lessons, recommend updating the harness.

## Examples

- "Check this CSV" means inspect the file, run deterministic quality checks, and report issues with columns and row counts.
- "Summarize last week" means identify the date column/window, compute weekly metrics, and write a concise reusable note.
- "Make chart notes" means produce title candidates, axis/series notes, caveats, and 2-4 plain-English takeaways.

- Record repeated workflow friction in `Docs/Environment/IMPROVEMENT_LOG.md` before changing harness behavior.

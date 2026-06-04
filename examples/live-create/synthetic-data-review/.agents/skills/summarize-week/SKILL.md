---
name: summarize-week
description: "Use when the user asks to summarize weekly metrics, compare this week to last week, produce a weekly rollup, calculate week-over-week changes, or create a reusable metrics note. Do not use for raw CSV debugging unless a quality check has already passed."
---

## Critical

Do not invent metric formulas. Read `Docs/Areas/metric-definitions.md` and the source CSV before summarizing.

## Workflow

1. Confirm the source CSV, date column, metric columns, and target week.
2. Run deterministic aggregation with Python, spreadsheet formulas, or a clear manual calculation.
3. Compare against the previous week only when the prior window is present.
4. Write output under `reports/weekly/` when an artifact is requested.
5. Include verification: files read, week window, formulas, row counts.

## Output

- Week window
- Metrics table
- Notable increases/decreases
- Caveats
- Verification result


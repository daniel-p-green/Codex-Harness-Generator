---
name: data-quality-check
description: "Use when the user says check this CSV, audit data quality, validate a dataset, inspect nulls, find duplicate rows, or explain why a CSV looks wrong. Do not use for narrative-only chart notes or weekly summary writing unless quality checks are the first step."
---

## Critical

Only work with synthetic/public-safe data in this harness. Inspect the live file before reporting results.

## Workflow

1. Identify the CSV path. If none is given, inspect likely files under `data/raw/`.
2. Run `scripts/check_csv.py <csv-path>` from this skill folder or use equivalent deterministic checks.
3. Verify row count, columns, parseability, null counts, duplicate rows, and date-like column ranges.
4. Report findings with file path, exact checks, and recommended next action.

## Output

- CSV checked
- Rows and columns
- Quality findings
- Public-safety note
- Suggested follow-up


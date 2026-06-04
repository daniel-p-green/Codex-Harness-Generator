# Live Create Example Index

These examples were generated through the live model-mediated `/create` capture
path, sanitized, and checked in for product proof. Each capture includes
`Docs/Environment/CREATION_CONTEXT.md`, `LIVE_CREATE_CAPTURE.md`, eval score,
offline smoke result, and public-safe synthetic scope notes.

| Example | Project Type | What It Proves | Agents | Skills |
|---|---|---|---|---|
| `synthetic-markdown-notes/` | Knowledge work | Notes, decisions, planning docs, inbox/outbox workflow | `researcher`, `drafter`, `reviewer` | `state-save`, `state-load`, `update`, `health-check`, `process-inbox` |
| `synthetic-python-cli/` | Python CLI | Markdown TODO scanning and cleanup-summary workflow | `markdown-auditor`, `summary-writer` | `audit-todos`, `write-cleanup-summary` |
| `synthetic-data-review/` | Data analysis | CSV quality checks, weekly metric summaries, chart-ready notes | `csv-quality-analyst`, `weekly-metrics-summarizer`, `report-note-writer` | `data-quality-check`, `summarize-week`, `chart-notes`, `state-save`, `state-load` |

Verify all checked-in live examples with:

```bash
python scripts/eval_generated_harness.py examples/live-create/synthetic-*
python scripts/smoke_generated_harness.py examples/live-create/synthetic-*
python scripts/run_evals.py
```

Run representative live task trials against temporary copies:

```bash
python scripts/run_live_example_task_trials.py
```

Run authenticated smoke checks separately when local Codex CLI auth is available:

```bash
python scripts/run_evals.py --codex-live --codex-live-profile all
```

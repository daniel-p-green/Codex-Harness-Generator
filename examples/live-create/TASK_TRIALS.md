# Live Example Task Trials

Generated: 2026-06-04T05:03:44Z
Status: PASS

These trials copy checked-in live-create examples to a temporary
workspace, seed synthetic inputs, run authenticated `codex exec`, and
verify that each generated harness produces the expected output file.

| Trial | Example | Status | Output |
|---|---|---|---|
| `markdown-notes-summary` | `synthetic-markdown-notes` | PASS | `Outbox/planning-sync-summary.md` |
| `python-cli-todo-audit` | `synthetic-python-cli` | PASS | `reports/todo-audit.md` |
| `data-review-weekly-summary` | `synthetic-data-review` | PASS | `reports/weekly/2026-05-25-summary.md` |
| `security-review-synthetic-code` | `synthetic-security-audit` | PASS | `reports/security-review.md` |

## Scope

- Uses synthetic, public-safe input data only.
- Mutates temporary copies of examples, not the checked-in examples.
- Proves representative task usefulness; it does not prove every
  generated harness will handle every future task perfectly.

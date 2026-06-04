---
name: state-save
description: "Use when the user says save progress, remember this analysis state, pause this weekly summary, preserve decisions, or checkpoint the current CSV/report task. Do not use for permanent documentation updates that belong in Docs/Areas or Docs/Decisions."
---

## Critical

Save transient state only. Do not store real personal data or private secrets.

## State Taxonomy

- Tool state: current shell, scripts used, command outputs worth rerunning.
- Task state: active CSV, requested week, target report, next action.
- Artifact state: generated files under `data/processed/` and `reports/weekly/`.
- Decision state: metric definitions, public-safety assumptions, chart framing choices.
- Blocked state: missing CSV, unclear metric definition, parse error, audience question.
- Drift risk: source CSV changed, week window changed, metric definition changed.

## Workflow

1. Summarize the active task and evidence read.
2. Update `Docs/_working/state/SESSION_CONTEXT.md`.
3. Update `Docs/_working/state/SESSION_SNAPSHOT.json` with paths, decisions, blockers, and drift risks.
4. Prune stale session notes older than 30 days when practical.


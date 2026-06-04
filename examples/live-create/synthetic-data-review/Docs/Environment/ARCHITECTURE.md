# ARCHITECTURE

## Component Manifest

| Pass | File Path | Reference Template | Notes |
|---:|---|---|---|
| 1 | AGENTS.md | Core/agents-md.md | Root instructions |
| 1 | .codex/config.toml | Core/codex-config-toml.md | Local permissions and registry |
| 1 | .gitignore | Foundation | Excludes working state and generated data |
| 1 | .codex/hooks/self_learning_check.py | Optional/hooks-template.md | Self-learning trigger |
| 1 | .codex/rules/00-orchestrator.md | Core/orchestrator-rule.md | Routing table |
| 1 | .codex/rules/01-autonomy.md | Core/autonomy-rule.md | Autonomy |
| 1 | .codex/rules/02-context-management.md | Core/context-management-rule.md | Context |
| 1 | .codex/rules/03-error-handling.md | Core/error-handling-rule.md | Errors |
| 1 | .codex/rules/04-self-learning.md | Core/self-learning-rule.md | Learning loop |
| 1 | .codex/rules/05-reporting-style.md | Domain rule | Report wording |
| 2 | .codex/agents/csv-quality-analyst.toml | Agents/domain-specialist | CSV quality |
| 2 | .codex/agents/weekly-metrics-summarizer.toml | Agents/domain-specialist | Weekly summaries |
| 2 | .codex/agents/report-note-writer.toml | Agents/writer | Chart notes |
| 3 | .agents/skills/data-quality-check/SKILL.md | Skills/domain-command | CSV checks |
| 3 | .agents/skills/data-quality-check/scripts/check_csv.py | Skills/scripts | Deterministic check |
| 3 | .agents/skills/summarize-week/SKILL.md | Skills/domain-command | Weekly summary |
| 3 | .agents/skills/summarize-week/scripts/summarize_week.py | Skills/scripts | Deterministic aggregation |
| 3 | .agents/skills/chart-notes/SKILL.md | Skills/domain-command | Chart notes |
| 3 | .agents/skills/state-save/SKILL.md | Core/state-save-skill.md | Save state |
| 3 | .agents/skills/state-load/SKILL.md | Core/state-load-skill.md | Load state |
| 4 | Docs/index.md | Core/memory-scaffold.md | Wiki entry |
| 4 | Docs/Areas/data-inventory.md | Memory scaffold | Data files |
| 4 | Docs/Areas/metric-definitions.md | Memory scaffold | Metrics |
| 4 | Docs/Areas/reporting-style.md | Memory scaffold | Notes |
| 4 | Docs/Decisions/0001-public-safe-synthetic-only.md | Decision record | Synthetic-only decision |
| 5 | Docs/GETTING_STARTED.md | Documentation | Onboarding |
| 5 | README.md | Documentation | Project README |
| 5 | Docs/Environment/MANIFEST.md | Documentation | Generated file list |
| 5 | Docs/Environment/ASSUMPTIONS.md | Documentation | Assumptions |
| 5 | Docs/Environment/SOURCE_MAP.md | Documentation | Sources |
| 5 | Docs/Environment/VALIDATION_REPORT.md | Validator | Validation |
| 5 | Docs/Environment/VERSION.md | Documentation | Version |

## Routing Table

The routing table is implemented in `.codex/rules/00-orchestrator.md` with 12 domain-specific routes covering CSV quality, parse errors, weekly metrics, chart notes, public safety, metric definitions, exploration, and state.

## State Taxonomy

- Tool state: shell commands, Python scripts, parser outputs.
- Task state: active CSV, week window, target report.
- Artifact state: files in `data/processed/`, `reports/weekly/`, and Docs notes.
- Decision state: metric formulas, synthetic-only decision, chart framing.
- Blocked state: missing file, undefined metric, parse error, unclear date column.
- Drift risk: changed CSV contents, changed metric definition, changed reporting week.

## Memory Tier Selection

Standard. The workspace is solo/simple in sensitivity but has repeated workflows, generated artifacts, and reusable definitions across CSV quality, weekly summaries, and chart notes.

## Directory Structure Preview

```text
project-root/
├── AGENTS.md
├── .codex/
│   ├── config.toml
│   ├── hooks/
│   ├── agents/
│   └── rules/
├── .agents/
│   └── skills/
├── data/
│   ├── raw/
│   └── processed/
├── reports/
│   └── weekly/
└── Docs/
    ├── index.md
    ├── GETTING_STARTED.md
    ├── Areas/
    ├── Decisions/
    ├── Environment/
    └── _working/
```

## Environment Complexity

User inclination: lean simple. Status: Auto-confirmed (preset mode).

| Component | Benefit | Setup Cost | Simpler Alternative | Recommendation |
|---|---|---|---|---|
| Pandas dependency | Faster analysis for large CSVs | Install and environment maintenance | Standard-library CSV scripts | Skip |
| External analytics connectors | Direct dashboard access | Credentials and privacy risk | Local CSV exports | Skip |
| Vector memory | Semantic recall | Extra service/configuration | Markdown wiki | Skip |

## Token Optimization

- Efficiency tier: balanced
- Model override policy: standard mixed selection
- Compaction threshold: default
- VCS ignore rules aggressiveness: standard
- RTK recommendation level: mention
- Agent consolidation notes: standard roster retained
- AGENTS.md line target: 200
- Docs/Environment/EVAL_PLAN.md
- Docs/Environment/IMPROVEMENT_LOG.md
- Docs/Environment/TASK_TRIALS.md
- scripts/record-improvement.py
- scripts/record-task-trial.py
- scripts/summarize-task-trials.py
- scripts/run-harness-evals.py
- Docs/Environment/EVAL_REPORT.md

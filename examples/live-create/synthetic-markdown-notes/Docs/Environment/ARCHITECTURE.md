# ARCHITECTURE

## Component Manifest

| Pass | File Path | Reference Template | Notes |
|---|---|---|---|
| 1 | AGENTS.md | Core/agents-md.md | Always-loaded instructions for synthetic docs |
| 1 | .codex/config.toml | Core/codex-config-toml.md | Limited network, sensitive deny rules |
| 1 | .gitignore | architecture-guide.md | Excludes transient working state |
| 1 | .codex/rules/00-orchestrator.md | Core/orchestrator-rule.md | Domain routing table |
| 1 | .codex/rules/01-autonomy.md | Core/autonomy-rule.md | Conservative overwrite posture |
| 1 | .codex/rules/02-context-management.md | Core/context-management-rule.md | State taxonomy and wiki loading |
| 1 | .codex/rules/03-error-handling.md | Core/error-handling-rule.md | Missing files, ambiguity, safety |
| 1 | .codex/rules/04-self-learning.md | Core/self-learning-rule.md | Retro-triggered improvements |
| 2 | .codex/agents/researcher.toml | Agents/researcher.md | Read-only synthesis |
| 2 | .codex/agents/drafter.toml | Agents/drafter.md | Writes Markdown documents |
| 2 | .codex/agents/reviewer.toml | Agents/reviewer.md | Read-only accuracy and public-safety review |
| 3 | .agents/skills/state-save/SKILL.md | Core/state-save-skill.md | Saves six-category state |
| 3 | .agents/skills/state-load/SKILL.md | Core/state-load-skill.md | Loads and checks drift |
| 3 | .agents/skills/update/SKILL.md | Core/update-skill.md | Learns from retro patterns |
| 3 | .agents/skills/health-check/SKILL.md | Core/health-check-skill.md | Validates harness structure |
| 3 | .agents/skills/process-inbox/SKILL.md | Skills/process-inbox.md | Processes synthetic input files |
| 4 | Docs/index.md | Core/memory-scaffold.md | Wiki index with NEW_ENVIRONMENT |
| 4 | Docs/Areas/meeting-notes.md | Core/memory-scaffold.md | Notes conventions |
| 4 | Docs/Areas/project-planning.md | Core/memory-scaffold.md | Planning conventions |
| 4 | Docs/Decisions/index.md | Core/memory-scaffold.md | Decision index |
| 4 | Inbox/README.md | memory-scaffold.md | Raw synthetic inputs |
| 4 | Outbox/README.md | memory-scaffold.md | Generated outputs |
| 5 | Docs/GETTING_STARTED.md | component-generator-guide.md | User onboarding |
| 5 | Docs/Environment/VERSION.md | component-generator-guide.md | Version record |
| 5 | Docs/Environment/MANIFEST.md | component-generator-guide.md | Generated file list |
| 5 | Docs/Environment/ASSUMPTIONS.md | component-generator-guide.md | Assumptions and limits |
| 5 | Docs/Environment/SOURCE_MAP.md | component-generator-guide.md | Official and local sources |
| 5 | Docs/Environment/VALIDATION_REPORT.md | validation-guide.md | Validation record |
| 5 | README.md | component-generator-guide.md | Project summary |

## Routing Table

The routing table is fully enumerated in `.codex/rules/00-orchestrator.md` with 12 entries covering notes, decisions, planning, Inbox processing, public-safety review, state recovery, and harness updates.

## State Taxonomy

- Tool state: validation commands, conversion tools used, files inspected.
- Task state: current documentation goal, audience, requested output path.
- Artifact state: meeting notes, decisions, plans, Inbox inputs, Outbox drafts.
- Decision state: durable choices, rationale, rejected options, follow-ups.
- Blocked state: missing files, unclear owners, ambiguous dates, uncertain source.
- Drift risk: newer notes, changed plans, stale saved state, changed public-safety requirements.

## Memory Tier

Lite. The workspace is solo, synthetic, and document-centric, with a small number of files and no team role structure. `Docs/index.md` is the only default wiki page; detail pages load on demand.

## Directory Structure Preview

```text
project-root/
├── AGENTS.md                          # always loaded
├── .codex/                            # assistant configuration
│   ├── config.toml
│   ├── agents/
│   └── rules/
├── .agents/skills/                    # triggerable commands
├── Docs/                              # workspace knowledge
│   ├── index.md                       # always loaded
│   ├── Areas/
│   ├── Decisions/
│   ├── Environment/
│   └── _working/                      # gitignored transient state
├── Inbox/                             # synthetic raw inputs
└── Outbox/                            # generated outputs
```

## Environment Complexity

Status: Auto-confirmed (preset mode)

| Component | Benefit | Setup Cost | Simpler Alternative | Recommendation |
|---|---|---|---|---|
| MarkItDown MCP | Converts many incoming document formats | Requires MCP setup | Markdown/text files in Inbox | Skip for lean proof |
| Pandoc | Produces formatted docs and PDFs | Requires installed binary and templates | Markdown outputs | Skip for generated harness; available locally if user wants it |
| Brand support | Checks style guides and templates | Adds Brand directory and update flow | Plain concise Markdown | Skip; no brand requirement |
| Sensitive-data enforcement hook | Deterministic PII blocking | Requires pattern config and maintenance | Advisory public-safety review | Skip; user stated synthetic safe data |

## Token Optimization

- Efficiency tier: balanced.
- Model override policy: mixed high reasoning for research/review, medium for drafting.
- Compaction threshold: default.
- Ignore rules: standard, focused on transient state and generated formatted outputs.
- RTK recommendation level: mention only.
- Agent consolidation: keep three agents because research, drafting, and review have different write permissions.
- AGENTS.md line target: 200.

## Permissions

Use workspace write with sensitive recursive deny rules for `.env`, secrets, tokens, credentials, private keys, and certificates. Network is limited to official Codex/OpenAI and GitHub documentation domains.
- Docs/Environment/EVAL_PLAN.md
- Docs/Environment/IMPROVEMENT_LOG.md
- Docs/Environment/TASK_TRIALS.md
- scripts/record-improvement.py
- scripts/record-task-trial.py
- scripts/summarize-task-trials.py

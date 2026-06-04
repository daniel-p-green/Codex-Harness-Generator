# Architecture

## Directory Structure

```text
.
├── AGENTS.md
├── .codex/
│   ├── config.toml
│   ├── agents/
│   │   ├── markdown-auditor.toml
│   │   └── summary-writer.toml
│   └── rules/
│       ├── 00-orchestrator.md
│       ├── 01-python-cli.md
│       ├── 02-safety-privacy.md
│       └── 03-self-learning.md
├── .agents/
│   └── skills/
│       ├── audit-todos/
│       │   └── SKILL.md
│       └── write-cleanup-summary/
│           └── SKILL.md
└── Docs/
    ├── GETTING_STARTED.md
    └── Environment/
```

## Components

- Rules: 4.
- Assistants: 2.
- Skills: 2.
- External services: none.
- MCP servers: none.

## Environment Complexity

| Option | Decision | Reason |
|---|---|---|
| Network access | Rejected | The CLI scans local Markdown only. |
| Compliance hooks | Rejected | Public-safe synthetic data does not justify deterministic enforcement. |
| Multi-area hub | Rejected | One focused Python CLI work area is enough. |
| Agent Teams mode | Available | Documented as an execution mode but not the default path for small tasks. |

## Generation Plan

1. Foundation: AGENTS.md, config, core rules, docs.
2. Assistants: Markdown auditor and summary writer.
3. Skills: TODO audit and cleanup summary writing.
4. Infrastructure: permissions, ignore rules, working-memory folders.
5. Documentation: manifest, assumptions, source map, validation report.
- Docs/Environment/EVAL_PLAN.md
- Docs/Environment/IMPROVEMENT_LOG.md
- Docs/Environment/TASK_TRIALS.md
- scripts/record-improvement.py
- scripts/record-task-trial.py

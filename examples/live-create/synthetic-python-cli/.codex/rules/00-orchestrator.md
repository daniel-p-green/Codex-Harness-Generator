# Orchestrator Rule

Route work by risk and dependency shape.

## Execution Modes

- Sequential subagents: use for normal tasks with natural order, such as plan, implement, review, then verify.
- Parallel subagents: use for two or three independent investigations, such as checking parser edge cases while separately reviewing summary copy.
- Agent Teams: use only for large independent streams with distinct file ownership where the speedup is worth the higher token cost.

Prefer Git worktrees over Agent Teams if the project later becomes Git-based and multiple assistants need filesystem isolation.

## Routing

- CLI flag or parser fix: inspect relevant files, patch directly, verify with tests or a command run.
- Markdown TODO classification: route to `markdown-auditor`, then implement the smallest correction.
- Cleanup summary wording: route to `summary-writer` when public-facing wording matters.
- Security, permissions, or data exposure: pause for scope clarity if real data may be involved.

## Context

Keep task context small. Summarize long findings into `Docs/_working/state/SESSION_CONTEXT.md` when a task spans multiple turns, then continue from that summary.

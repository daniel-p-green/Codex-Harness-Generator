# 2. Agents

**Last Updated**: 2026-06-03

This topic defines how generated harnesses use Codex subagents. Custom agents are
project-scoped TOML files under `.codex/agents/`.

## 2.1 Custom Agent Schema

- **Source**: https://developers.openai.com/codex/subagents
- **Required fields**:
  - `name`
  - `description`
  - `developer_instructions`
- **Recommended fields for generated harnesses**:
  - `model = "gpt-5.5"`
  - `model_reasoning_effort = "low" | "medium" | "high" | "xhigh"`
  - `sandbox_mode = "read-only" | "workspace-write"`

Example:

```toml
name = "code_mapper"
description = "Read-only codebase explorer for locating relevant files and symbols before edits."
model = "gpt-5.5"
model_reasoning_effort = "low"
sandbox_mode = "read-only"
developer_instructions = """
Map the relevant code paths.
Return file paths, symbols, and concise evidence.
Do not edit files.
"""
```

## 2.2 Delegation Contract

Every delegation should include five elements:

1. **Objective**: what the agent must accomplish.
2. **Inputs**: files, prior notes, commands, or user constraints it should use.
3. **Boundaries**: what is out of scope and whether it may write files.
4. **Verification**: how it should check or support its answer.
5. **Output**: the artifact or response shape expected.

Good delegation:

```text
Use the code_mapper agent to locate the auth refresh flow. Read only. Return
the owning files, entry points, and a short flow summary with paths.
```

Poor delegation:

```text
Research auth.
```

## 2.3 Reasoning Effort By Role

Use one model family (`gpt-5.5`) and vary effort by job.

| Role | Effort | Sandbox | Notes |
|---|---|---|---|
| Explorer / mapper | `low` | `read-only` | Fast file and symbol location |
| Intake interviewer | `medium` | `workspace-write` | Writes structured intake artifacts |
| Implementer | `medium` | `workspace-write` | Follows an approved plan and verifies |
| Validator | `medium` | `read-only` or report-only write scope | Runs checklists and writes reports |
| Planner / architect | `high` | `workspace-write` | Designs structure and tradeoffs |
| Debugger | `high` | `workspace-write` | Multi-hypothesis investigation |
| Reviewer | `high` | `read-only` | Finds regressions and missing tests |
| High-stakes analyst | `high` or `xhigh` | Usually `read-only` | Legal, finance, security, medical, policy |

Use `xhigh` sparingly and document why the extra depth is worth the cost.

## 2.4 Sandbox Scope

- Use `sandbox_mode = "read-only"` when the agent should gather evidence,
  review, research, or inspect.
- Use `sandbox_mode = "workspace-write"` when the agent must create or edit
  project files.
- Keep sensitive path restrictions in `.codex/config.toml` permissions, not in
  prose promises.
- If an agent writes only a report, prefer a narrow instruction that names the
  report path.

Anti-pattern: a reviewer that can edit source files by default. Reviewers should
report findings; implementation should be a separate step.

## 2.5 Description Quality

Descriptions are routing-critical. They should say when to use the agent, not
only what it is.

Strong description:

```text
Reviews code changes for correctness, behavior regressions, missing tests, and
security risk. Use after implementation or when the user asks for a review. Do
not use for making changes.
```

Weak description:

```text
Helps with code quality.
```

Include negative triggers when two agents are easy to confuse.

## 2.6 Context Discipline

The orchestrator should not read large source files directly when a subagent can
map or inspect them in isolated context.

Pattern:

1. Orchestrator delegates exploration.
2. Explorer writes or returns concise findings with paths.
3. Planner or implementer uses those findings.
4. Reviewer checks the result independently.

For long workflows, have agents write handoff notes under `Docs/_working/` so
the main session reads summaries rather than raw exploratory material.

## 2.7 Generated-Agent Checklist

Every generated `.codex/agents/*.toml` file must pass this checklist:

- TOML parses.
- `name` matches the filename stem.
- `description` includes clear triggers and negative triggers where needed.
- `developer_instructions` state objective, boundaries, verification, and output.
- `model` is an OpenAI model ID.
- `model_reasoning_effort` matches task complexity.
- `sandbox_mode` matches write needs.
- Read-only agents explicitly say they do not edit files.
- Write-capable agents include scope and verification rules.

## 2.8 Anti-Patterns

- Creating agents "just in case" when routing can stay in the main session.
- Using broad write scope for review, exploration, or research.
- Writing agent instructions that repeat all of AGENTS.md.
- Omitting verification criteria.
- Letting subagents fan out recursively without an explicit reason.

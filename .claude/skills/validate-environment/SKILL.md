---
name: validate-environment
description: Validates an existing Claude Code environment against structural correctness and quality standards (file references resolve, frontmatter is valid, size limits hold, routing is complete, hub registry matches disk). Use when user says "validate environment", "check my environment", "is my setup correct", "validate my config", "audit my environment", "run the validator", or "/validate-environment". Do NOT use for creating new environments or for best-practice upgrade recommendations (use /upgrade-environment for the latter).
context: fork
allowed-tools: [Read, Glob, Grep, Write]
metadata:
  author: Claude Harness Generator
  version: 1.0.0
---

## Critical

This skill validates an EXISTING environment. It is read-only with respect to the environment (writes only the validation report). The authoritative checklist lives in `Docs/Templates/References/validation-guide.md` -- load that at Step 2 rather than relying on any list in this file. The guide is updated as standards evolve; duplicating it here would drift.

## What this skill does

1. Get the environment path from the user
2. Detect environment shape (single or hub) and read the relevant GENESIS/ARCHITECTURE files
3. Load the current validation checklist from validation-guide.md
4. Run every applicable check
5. Write a validation report
6. Present results in plain language and offer fixes

## Steps

### Step 1: Get the environment path

Ask the user for the path to the environment to validate. If the current directory contains a `.claude/` directory or `CLAUDE.md`, offer to validate it.

Verify the path exists and contains at least one of:
- `.claude/` directory
- `CLAUDE.md` file
- `Docs/Environment/HUB_GENESIS.md` (hub case -- directory itself may not have `.claude/`)

If none is found, report "No Claude Code environment found at this path" and stop.

### Step 2: Detect shape

Check for `<target>/Docs/Environment/HUB_GENESIS.md`.
- If present: shape is HUB. Read HUB_GENESIS.md and HUB_ARCHITECTURE.md (if it exists) plus every per-area GENESIS.md and ARCHITECTURE.md listed in the work-area registry.
- If absent: shape is SINGLE. Read `<target>/Docs/Environment/GENESIS.md` and `ARCHITECTURE.md` if they exist.

Also detect HUB_LIKE_UNDECLARED: sibling environments (each a full `.claude/` + `CLAUDE.md`) under the target without a parent HUB_GENESIS.md. Report this in the output so the user can consider declaring a hub via `/upgrade-environment`.

### Step 3: Load the current validation checklist

Read `Docs/Templates/References/validation-guide.md` in its entirety. It contains:
- Structural checks
- Routing and logic checks
- Size and quality checks
- Conditional checks (triggered by specific GENESIS/ARCHITECTURE contents)
- Hub-mode checks (run only when shape is HUB)

Also read `Docs/AgentPlaybooks/EnvironmentValidation.md` for functional-test scenarios and the smoke test template.

### Step 4: Run every applicable check

Execute every check from the guide against the target. For hub environments, run the core checks against the parent AND each work area, then run the hub-only checks once at the parent level. Record PASS, WARN, or FAIL with details for each non-PASS result.

Do not invent checks not in the guide. Do not skip checks even if early ones fail -- a complete report is more useful than a short one.

### Step 5: Write validation report

Write to `<target>/Docs/Environment/VALIDATION_REPORT.md` using the report format from the validation guide. For hubs, include a "Per-area results" subsection per work area plus a "Hub-level results" section.

### Step 6: Present results

Output a plain-language summary to the user:
- Overall status: PASS (everything looks good), WARN (some improvements possible), or FAIL (issues need fixing)
- For each FAIL: what is wrong, why it matters, how to fix it
- For each WARN: what could be improved
- If shape is HUB_LIKE_UNDECLARED: gently suggest running `/upgrade-environment` to declare it
- Use plain language, not technical jargon

### Step 7: Offer fixes

If FAIL or WARN issues were found:
- Offer to create a fix plan
- Group fixes by effort: quick (1-2 file edits), medium (new files needed), large (structural changes)
- Let the user choose which fixes to apply

Do NOT apply fixes automatically. This skill is read-only (except for the validation report).

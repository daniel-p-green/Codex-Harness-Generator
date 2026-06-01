---
name: upgrade-environment
description: Audits an existing Claude Code environment against current best practices, interviews the user about pain points, and implements approved improvements -- including shape conversions (single <-> multi-area hub <-> undeclared siblings). Recommendations are tiered quick wins / medium / large so the user picks what to implement. Use when user says "upgrade environment", "improve my environment", "optimize my setup", "audit my environment for best practices", "make my environment better", "convert to hub", "collapse hub", "/upgrade-environment", or "what can I improve". Do NOT use for creating new environments or for structural-only validation (use /validate-environment for the latter).
context: fork
allowed-tools: [Read, Glob, Grep, Write, Bash]
metadata:
  author: Claude Harness Generator
  version: 1.0.0
---

## Critical

This skill is a TRIGGER. It inventories the target environment and writes UPGRADE_CONTEXT.md, then returns control to the orchestrator. It does NOT run the analysis, interview, or implementation -- the orchestrator coordinates those steps.

## What this skill does

1. Get target path (offer current directory if it has `.claude/`)
2. Verify environment exists (must have `.claude/` + `CLAUDE.md`)
3. Quick inventory: count rules, agents, skills, check for Docs/ structure
4. Check for GENESIS.md and ARCHITECTURE.md (richer context if present)
5. Write `<target>/Docs/Environment/UPGRADE_CONTEXT.md` with inventory + platform info
6. Return to orchestrator

## Steps

### Step 1: Get the target directory

Ask the user for the path to the environment to upgrade. If the current directory contains a `.claude/` directory and `CLAUDE.md`, offer to use it.

### Step 2: Verify environment exists

The target MUST have both:
- `.claude/` directory
- `CLAUDE.md` file

If either is missing, report "No complete Claude Code environment found at this path" and stop. An environment must exist before it can be upgraded.

### Step 3: Quick inventory

Count and list:
- Rule files: glob `.claude/rules/*.md` -- count and list names
- Agent files: glob `.claude/agents/*.md` -- count and list names
- Skill directories: glob `.claude/skills/*/SKILL.md` -- count and list names
- Docs structure: check for `Docs/index.md`, `Docs/GETTING_STARTED.md`, `Docs/_working/`
- Settings: check for `.claude/settings.json`, `.claude/settings.local.json`
- Hooks: check for `.claude/hooks.json` or hook entries in settings.json
- VCS ignore: check for `.gitignore`, `.p4ignore`

### Step 4: Check for GENESIS.md and ARCHITECTURE.md

Look for `<target>/Docs/Environment/GENESIS.md` and `<target>/Docs/Environment/ARCHITECTURE.md`. These provide richer context for the upgrade analysis but are not required (the environment may not have been created by the Harness Generator).

Also check for `<target>/Docs/Environment/VALIDATION_REPORT.md` -- a recent validation gives the analyzer a head start.

### Step 4a: Detect hub shape

Apply these tests in order. First match wins.

**Test 1 -- declared hub**:
If `<target>/Docs/Environment/HUB_GENESIS.md` exists, record `Shape: HUB`.
Read its work-area registry and for each listed area-slug record whether
`<target>/<area-slug>/Docs/Environment/GENESIS.md` and `ARCHITECTURE.md` exist
(registry-vs-disk drift).

**Test 2 -- single environment**:
If `<target>/.claude/` AND `<target>/CLAUDE.md` both exist, record `Shape: SINGLE`.
Do NOT look deeper. A single environment may have unrelated subfolders that
contain their own unrelated Claude setups (e.g., a vendored library with its
own CLAUDE.md), and those should not be treated as work areas.

**Test 3 -- undeclared hub**:
ALL of the following must hold:
- `<target>/.claude/` does NOT exist at the root
- `<target>/CLAUDE.md` does NOT exist at the root
- `<target>/Docs/Environment/HUB_GENESIS.md` does NOT exist
- Two or more immediate subdirectories of `<target>` each contain their own
  `.claude/` directory AND a `CLAUDE.md` file
- Those subdirectory environments are sibling peers (common parent is `<target>`,
  not grandparent-and-below)

If all hold, record `Shape: HUB_LIKE_UNDECLARED` and list the qualifying
subfolders. Offer `Declare hub structure` in the upgrade recommendations.

**Test 4 -- empty target**:
If none of the above matches, report "No Claude Code environment found at this
path" and stop. Do not attempt to upgrade an empty directory.

### Why the tests are ordered this way

- Declared hubs (Test 1) are unambiguous -- HUB_GENESIS.md is the declaration.
- Single environments (Test 2) must be detected BEFORE undeclared-hub because a
  single env with noise in subfolders should stay single. Only match
  HUB_LIKE_UNDECLARED when there is NO env at the root.
- Two sibling envs is the minimum for "hub-like" -- one sibling is just a
  single env with an odd parent.
- Deeper nesting (e.g., `<target>/a/b/c/.claude/`) is ignored; hubs are
  parent + immediate children only.

### Step 5: Create environment directory

Create `<target>/Docs/Environment/` if it does not exist.

### Step 6: Write UPGRADE_CONTEXT.md

Write to `<target>/Docs/Environment/UPGRADE_CONTEXT.md`:

```markdown
# Upgrade Context

Created: <timestamp>

## Target
- Path: <absolute path>
- Platform: <win32|darwin|linux>

## Inventory
- Rules: <count> (<list of names>)
- Agents: <count> (<list of names>)
- Skills: <count> (<list of names>)
- Docs structure: <present|absent> (index.md: yes|no, GETTING_STARTED: yes|no, _working: yes|no)
- Settings: settings.json <yes|no>, settings.local.json <yes|no>
- Hooks: <yes|no> (<details>)
- VCS ignore: <type or "none">

## Available Context
- GENESIS.md: <yes|no>
- ARCHITECTURE.md: <yes|no>
- HUB_GENESIS.md: <yes|no>
- HUB_ARCHITECTURE.md: <yes|no>
- VALIDATION_REPORT.md: <yes|no> (<date if present>)

## Shape
- Shape: <SINGLE | HUB | HUB_LIKE_UNDECLARED>
- Work areas (hub only): <list of area slugs and descriptions>

## CLAUDE.md Stats
- Line count: <N> (hub: parent CLAUDE.md line count; per-area counts listed separately)
- Has first-run greeting: <yes|no>
- Has routing reference: <yes|no>

## Pipeline Status
- Stage: TRIGGER_COMPLETE
- Next: USER_INTERVIEW
```

### Step 7: Output summary

Report to the user:
- Environment found at target path
- Quick inventory summary (N rules, N agents, N skills)
- Whether GENESIS.md/ARCHITECTURE.md were found (richer analysis if present)
- "The upgrade analysis pipeline will now begin."

The orchestrator reads UPGRADE_CONTEXT.md and coordinates: user interview -> structural pre-check -> deep analysis -> recommendations -> implementation -> validation.

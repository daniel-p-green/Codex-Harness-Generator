---
name: upgrade-environment
description: Audits an existing Codex environment against current best practices, interviews the user about pain points, and implements approved improvements -- including shape conversions (single <-> multi-area hub <-> undeclared siblings). Recommendations are tiered quick wins / medium / large so the user picks what to implement. Use when user says "upgrade environment", "improve my environment", "optimize my setup", "audit my environment for best practices", "make my environment better", "convert to hub", "collapse hub", "/upgrade-environment", or "what can I improve". Do NOT use for creating new environments or for structural-only validation (use /validate-environment for the latter).
---

## Critical

This skill is a TRIGGER. It inventories the target environment and writes UPGRADE_CONTEXT.md, then returns control to the orchestrator. It does NOT run the analysis, interview, or implementation -- the orchestrator coordinates those steps.

## What this skill does

1. Get target path (offer current directory if it has `.codex/`)
2. Verify environment exists (must have `.codex/` + `AGENTS.md`)
3. Quick inventory: count rules, agents, skills, check for Docs/ structure
4. Check for GENESIS.md and ARCHITECTURE.md (richer context if present)
5. Write `<target>/Docs/Environment/UPGRADE_CONTEXT.md` with inventory + platform info
6. Return to orchestrator

## Steps

### Step 1: Get the target directory

Ask the user for the path to the environment to upgrade. If the current directory contains a `.codex/` directory and `AGENTS.md`, offer to use it.

### Step 2: Verify environment exists

The target MUST have both:
- `.codex/` directory
- `AGENTS.md` file

If either is missing, report "No complete Codex environment found at this path" and stop. An environment must exist before it can be upgraded.

### Step 3: Quick inventory

Count and list:
- Rule files: glob `.codex/rules/*.md` -- count and list names
- Agent files: glob `.codex/agents/*.toml` -- count and list names
- Skill directories: glob `.agents/skills/*/SKILL.md` -- count and list names
- Docs structure: check for `Docs/index.md`, `Docs/GETTING_STARTED.md`, `Docs/_working/`
- Config: check for `.codex/config.toml` and local config overlays
- Hooks: check for `.codex/hooks.json` or hook entries in .codex/config.toml
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
If `<target>/.codex/` AND `<target>/AGENTS.md` both exist, record `Shape: SINGLE`.
Do NOT look deeper. A single environment may have unrelated subfolders that
contain their own unrelated Codex setups (e.g., a vendored library with its
own AGENTS.md), and those should not be treated as work areas.

**Test 3 -- undeclared hub**:
ALL of the following must hold:
- `<target>/.codex/` does NOT exist at the root
- `<target>/AGENTS.md` does NOT exist at the root
- `<target>/Docs/Environment/HUB_GENESIS.md` does NOT exist
- Two or more immediate subdirectories of `<target>` each contain their own
  `.codex/` directory AND a `AGENTS.md` file
- Those subdirectory environments are sibling peers (common parent is `<target>`,
  not grandparent-and-below)

If all hold, record `Shape: HUB_LIKE_UNDECLARED` and list the qualifying
subfolders. Offer `Declare hub structure` in the upgrade recommendations.

**Test 4 -- empty target**:
If none of the above matches, report "No Codex environment found at this
path" and stop. Do not attempt to upgrade an empty directory.

### Why the tests are ordered this way

- Declared hubs (Test 1) are unambiguous -- HUB_GENESIS.md is the declaration.
- Single environments (Test 2) must be detected BEFORE undeclared-hub because a
  single env with noise in subfolders should stay single. Only match
  HUB_LIKE_UNDECLARED when there is NO env at the root.
- Two sibling envs is the minimum for "hub-like" -- one sibling is just a
  single env with an odd parent.
- Deeper nesting (e.g., `<target>/a/b/c/.codex/`) is ignored; hubs are
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
- Settings: .codex/config.toml <yes|no>, local config profile <yes|no>
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

## AGENTS.md Stats
- Line count: <N> (hub: parent AGENTS.md line count; per-area counts listed separately)
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

---
name: create
description: Starts creating a new Codex environment for any project -- interviews the user, generates AGENTS.md + rules + agents + skills + .codex/config.toml, and validates the result. Supports both single-project environments and multi-area hubs (several related work areas sharing a parent configuration layer). Auto-detects when run inside an existing hub and offers to add a new area. Use when user says "create environment", "set up my project", "generate environment", "I need a Codex setup", "make me an environment", "add a work area", "/create", or "build me an environment". Do NOT use for updating existing environments, validating existing environments, or best-practice upgrade recommendations.
---

## Critical

This skill is a TRIGGER. It prepares the creation context and returns control to the orchestrator. It does NOT run the full creation pipeline, spawn agents, or generate environment files. The orchestrator coordinates everything after this skill completes.

Exception: if the user explicitly asks for an acceptance test, smoke test,
minimal valid harness, deterministic harness, or non-interactive proof path, use
`scripts/generate_minimal_harness.py <target>` instead of the full model-mediated
pipeline. Use `--list-profiles` and `--profile <name>` when the user wants a
specific deterministic profile. Then run
`scripts/eval_generated_harness.py <target>` and
`scripts/smoke_generated_harness.py <target>`. This proves the writer/evaluator
contract quickly without pretending it is the full custom `/create` experience.

## What this skill does

1. Get the target directory path from the user
2. Verify the directory exists or can be created
3. Test writability
4. Check for existing Codex files
5. Write CREATION_CONTEXT.md
6. Return to orchestrator

## Steps

### Step 1: Get target directory

Ask the user for the target directory path where their project lives (or will live). If the user already mentioned a path in their initial message, use that.

### Step 2: Verify directory

Check if the directory exists:
- If it exists: proceed
- If it does not exist: create it (including parent directories)
- If creation fails: report the error and stop

### Step 2a: Check for interrupted generation

After verifying the directory, check if `<target>/Docs/Environment/GENERATION_PROGRESS.md` exists. If it does:
- Read it to determine which passes completed (look for COMPLETE / IN_PROGRESS / PENDING status markers)
- If some passes completed but not all (i.e., at least one COMPLETE and at least one non-COMPLETE):
  - Present the user with two options:
    a) **Resume** from the next incomplete pass (the first pass not marked COMPLETE)
    b) **Start fresh** (regenerate everything from the beginning)
  - If the user chooses to resume:
    - Determine the next pass number (first pass not marked COMPLETE)
    - In Step 6, write CREATION_CONTEXT.md with `Stage: RESUME_GENERATION` and include `Resume From Pass: <N>`
    - The orchestrator will then skip intake and architecture, jumping directly to generation at pass N
  - If the user chooses to start fresh: continue normally through all steps
- If all passes are COMPLETE: treat as an existing environment (note it in Step 4)
- If the file exists but no passes are COMPLETE: continue normally (treat as a failed first attempt)

### Step 3: Test writability

Create a temporary file in the target directory to confirm write access:
```
<target>/.codex_env_write_test
```
If creation succeeds, delete the temp file immediately. If it fails, report the permission error and stop.

### Step 3a: Pre-flight tool availability check

Run quick checks to detect which tools are available on the system. Each check should timeout after 5 seconds -- if a check fails or times out, record "not found" and move on. This is informational only; do NOT block creation if any tool is missing.

Checks to run:
- **Python**: run `python --version` (fall back to `python3 --version` if the first fails)
- **pip**: run `pip --version` (fall back to `pip3 --version`)
- **Pandoc**: run `pandoc --version`
- **PowerShell** (Windows only): run `powershell -Command "echo ok"`

Record the results for inclusion in CREATION_CONTEXT.md (Step 6).

### Step 4: Check for existing Codex files

Look for these in the target directory:
- `.codex/` directory
- `AGENTS.md` file
- `AGENTS.override.md` file

If any are found, note them in the output. Do not overwrite or modify them at this stage. The orchestrator will handle conflict resolution.

### Step 4a: Hub detection

Check whether the target directory itself, OR any ancestor directory up to the filesystem root, contains `Docs/Environment/HUB_GENESIS.md`. Walk upward from the target until either:
- A HUB_GENESIS.md is found -> record the hub root path and read the work-area registry (list of area slugs). Set Hub Context status to `HUB_ADD_AREA`.
- The filesystem root is reached -> no hub detected. Set Hub Context status to `NONE`.

Do not walk past a directory that itself contains AGENTS.md + .codex/ without HUB_GENESIS.md -- that is a single-area environment, not a hub.

Record in CREATION_CONTEXT.md:
```
## Hub Context
- Status: <HUB_ADD_AREA | NONE>
- Hub root: <absolute path, only if HUB_ADD_AREA>
- Existing area slugs: <comma-separated list, only if HUB_ADD_AREA>
```

When status is `HUB_ADD_AREA`, the orchestrator skips shared-basics intake and prompts the user to name the new work area before running per-area intake only.

### Step 5: Create environment directory

Create the directory `<target>/Docs/Environment/` if it does not exist. This is where CREATION_CONTEXT.md, GENESIS.md, and ARCHITECTURE.md will be written.

### Step 6: Write CREATION_CONTEXT.md

Write to `<target>/Docs/Environment/CREATION_CONTEXT.md`:

```markdown
# Creation Context

Created: <timestamp>

## Target
- Path: <absolute path to target directory>
- Platform: <win32|darwin|linux>

## Directory Status
- Status: <CLEAN | HAS_EXISTING_ENV | CREATED_NEW>
- Existing files found: <list or "none">

## Tool Availability
- Python: <version string or "not found">
- pip: <version string or "not found">
- Pandoc: <version string or "not found">
- PowerShell: <"available" or "not found">

## User Context
- Stated project type: <if mentioned, else "not specified">
- Additional notes: <any relevant details from user's message>

## Hub Context
- Status: <HUB_ADD_AREA | NONE>
- Hub root: <absolute path, only if HUB_ADD_AREA>
- Existing area slugs: <comma-separated list, only if HUB_ADD_AREA>

## Pipeline Status
- Stage: <TRIGGER_COMPLETE | RESUME_GENERATION>
- Resume From Pass: <N, only if Stage is RESUME_GENERATION>
- Next: <PROFILE_SELECTION | HUB_ADD_AREA_INTAKE | GENERATION_PASS_N>
```

If Hub Context Status is `HUB_ADD_AREA`, set Pipeline Status Next to `HUB_ADD_AREA_INTAKE`. Otherwise use `PROFILE_SELECTION`.

If resuming from an interrupted generation (Step 2a), set Stage to `RESUME_GENERATION` and include the pass number. Otherwise use `TRIGGER_COMPLETE` and omit the Resume From Pass line.

### Step 7: Output summary

Report to the user:
- Target directory: confirmed writable
- Existing files: what was found (if any)
- "The creation pipeline will now begin."

The orchestrator reads CREATION_CONTEXT.md and coordinates the rest:
profile selection -> architect -> generator (5 passes) -> validator -> summary.

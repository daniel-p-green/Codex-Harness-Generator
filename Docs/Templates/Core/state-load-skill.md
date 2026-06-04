# Template: State-Load Skill (/state-load)

<!-- TEMPLATE ANNOTATION
  This template defines the /state-load skill that restores session state
  from a previous /state-save. It follows a 5-step session startup protocol,
  detects drift between saved and current state, and produces a context
  restoration briefing.

  QUALITY CRITERIA:
  - Skill description includes 3+ trigger phrases
  - SKILL.md body under 500 lines
  - Session startup protocol (5 steps)
  - Drift detection (compare saved vs current)
  - Context restoration briefing format
  - Read-only (no file edits)
  - Progressive disclosure (references/troubleshooting.md)

  WHY THIS EXISTS:
  Every new session starts with an empty context window. Without state-load,
  Codex must re-discover the project state by reading files and asking questions.
  State-load provides instant context restoration from the last /state-save,
  enabling seamless continuation of work across sessions.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application

  File structure:
  .agents/skills/state-load/
    SKILL.md              (this file -- core instructions)
    references/
      troubleshooting.md    (drift resolution guidance)
============================================================ -->

## SKILL.md

```yaml
---
name: state-load
description: Restore session context from a previous save. Use when starting a new session, after /clear, when the user says "load state", "restore progress", "where was I", "continue from last time", or "/state-load". Do NOT use for loading files or reading documents.
context: fork
tool access policy: [Read, Glob, Bash]
metadata:
  author: Codex Harness Generator
  version: 1.0.0
---
```

## Critical

- This skill is READ-ONLY. Do not create, modify, or delete any files.
- Read `Docs/_working/state/SESSION_SNAPSHOT.json` and `Docs/_working/state/SESSION_CONTEXT.md`
- If neither file exists, report "No saved state found" and suggest /state-save
- Compare saved state against current environment to detect drift
- Output a concise context restoration briefing

## Session startup protocol

<!-- 5-STEP PROTOCOL
  WHY: This sequence is derived from the long-running-agent-harnesses research.
  The order matters: confirm location first, then read saved state, then verify
  the baseline, then decide what to work on.
-->

Follow these steps in order:

### Step 1: Confirm working directory

Run `pwd` to verify the working directory is correct.
If the directory does not match expectations, report it immediately.

### Step 2: Read saved state

Read both state files:
- `Docs/_working/state/SESSION_SNAPSHOT.json` -- programmatic state (6 categories)
- `Docs/_working/state/SESSION_CONTEXT.md` -- human-readable narrative

If `SESSION_SNAPSHOT.json` exists but `SESSION_CONTEXT.md` does not (or vice versa),
use whichever is available and note the missing file.

If neither exists:
- Report: "No saved state found. This appears to be a fresh session."
- Suggest: "Use /state-save at the end of your session to enable restoration next time."
- Stop here.

### Step 3: Verify baseline

Check that the environment matches expectations from saved state:

- **VCS state** (if saved): Compare current branch and dirty files against snapshot
  - Different branch? Flag as drift.
  - New commits since save? Flag as drift.
  - Files in snapshot that no longer exist? Flag as drift.
- **Build state** (if relevant): Note last known build status from snapshot
- **Files** (artifact state): Verify that files listed in the snapshot still exist
  - Use `Glob` to check file existence without reading contents

### Step 4: Detect and report drift

<!-- DRIFT DETECTION
  WHY: Between sessions, teammates may push changes, dependencies may update,
  or the user may have made manual edits. Drift detection catches these changes
  so the user is aware before continuing.
-->

Compare saved state vs current state. Flag any differences:

| Drift type | Detection method | Severity |
|---|---|---|
| Branch changed | Current branch differs from saved | High |
| New commits by others | `git log` shows commits not in snapshot | Medium |
| Modified files changed | `git status` shows changes to files in artifact list | High |
| Files deleted | Glob check fails for saved file paths | High |
| Dependency changes | Package lock file modified since save timestamp | Low |
| No drift | Everything matches | (none) |

If drift is detected, include it in the restoration briefing.
If drift is HIGH severity, recommend the user review changes before continuing.

For drift resolution guidance, see `references/troubleshooting.md`.

### Step 5: Produce context restoration briefing

<!-- BRIEFING FORMAT
  WHY: The briefing is the primary output of state-load. It must be concise
  enough to fit in context while providing enough information to resume work
  immediately. Structured as a short report, not a dump of the state file.
-->

Output a briefing in this format:

```
## Session Restored

**Last saved**: [timestamp]
**Current task**: [one-sentence goal from task state]
**Status**: [done count]/[total steps] complete

### Completed
- [completed step 1]
- [completed step 2]

### Remaining
- [next step] <-- start here
- [subsequent steps]

### Blocked (if any)
- [blocked item with reason]

### Drift detected (if any)
- [drift item with severity and recommended action]

### Key decisions from last session
- [decision with rationale]

### Ready to continue
[Recommended next action based on remaining steps and blocked items]
```

## Handling edge cases

- **Corrupted JSON**: If `SESSION_SNAPSHOT.json` cannot be parsed, fall back to
  `SESSION_CONTEXT.md` for narrative restoration. Report the corruption.
- **Very old state** (saved > 7 days ago): Note the age and recommend verifying
  that the task is still relevant. Check for significant drift.
- **Multiple sessions saved**: If multiple snapshot files exist (timestamped backups),
  load the most recent one. Note that older snapshots are available.
- **Partial state**: If some taxonomy categories are empty or missing, report what
  was found and what was not. Do not fabricate missing state.

## references/troubleshooting.md

<!-- TROUBLESHOOTING REFERENCE
  WHY: Progressive disclosure. The main SKILL.md stays concise.
  Detailed drift resolution guidance lives in this reference file,
  loaded only when drift is actually detected.
-->

```markdown
# State-Load Troubleshooting

## Drift resolution

### Branch changed
The current git branch differs from the saved state.
- If the user switched branches intentionally: continue on current branch
- If unexpected: ask the user which branch to work on
- Consider: saved task may not apply to the current branch

### New commits by others
Teammates pushed changes since state was saved.
- Review the new commits: `git log --oneline [saved-commit]..HEAD`
- If new commits touch the same files as the saved task: warn about potential conflicts
- If new commits are unrelated: safe to continue

### Modified files changed externally
Files that were modified in the saved session have been changed again.
- Check `git diff [saved-commit] -- [file]` for each affected file
- If changes are additive (no conflicts): safe to continue
- If changes conflict with saved work: ask user how to proceed

### Files deleted
Files referenced in the snapshot no longer exist.
- Check git history: `git log --diff-filter=D -- [file]`
- If renamed: update task to reference new path
- If deleted intentionally: remove from remaining task steps

### Dependency changes
Package lock or dependency files changed since save.
- Run dependency install: `npm install` or `pip install -r requirements.txt`
- If new dependencies break the build: report the failure
```

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - VCS drift via git commands
  - Build state verification
  - Dependency change detection via lock files

  KNOWLEDGE WORK:
  - No VCS drift detection (or minimal)
  - Drift focuses on: source documents updated, deadlines passed
  - Simpler briefing format (less technical)
  - File existence checks for research documents and drafts

  GAME DEVELOPMENT:
  - VCS drift via Perforce commands (p4 changes, p4 sync status)
  - Build state from last known compilation
  - Additional: check for new submitted CLs affecting same files
  - Playtest status from saved state

  PERFORCE DRIFT DETECTION:
  ```
  # Check for new submitted CLs since save
  p4 changes -s submitted @>[saved_cl_number]
  # Check if opened files still exist and are still opened
  p4 opened
  # Check for sync status
  p4 sync -n
  ```
-->

<!-- ANTI-PATTERNS

  1. MODIFYING FILES DURING LOAD
     Problem: State-load creates or edits files, changing the environment state.
     Fix: "This skill is READ-ONLY." Load observes, it does not change.

  2. DUMPING THE FULL STATE FILE
     Problem: Pasting the entire SESSION_SNAPSHOT.json into the conversation.
     Fix: Produce a concise briefing. Reference the state files by path.

  3. NO DRIFT DETECTION
     Problem: State loaded from 3 days ago, branch changed, files deleted.
     User continues working on stale assumptions.
     Fix: Always compare saved vs current state. Flag differences.

  4. FAILING ON MISSING STATE
     Problem: No saved state -> error -> session stalls.
     Fix: Report "No saved state found," suggest /state-save, continue normally.

  5. FABRICATING MISSING STATE
     Problem: Some categories empty in snapshot. Skill guesses what they should be.
     Fix: Report what was found and what was not. Never fabricate.

  6. IGNORING OLD STATE
     Problem: State from 30 days ago loaded without warning. Tasks may be obsolete.
     Fix: Note age of state. Recommend verification if > 7 days old.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Skill description includes 3+ trigger phrases
  [ ] Negative trigger present ("Do NOT use for loading files or reading documents")
  [ ] SKILL.md body under 500 lines
  [ ] Critical instructions at top (read-only)
  [ ] 5-step session startup protocol in order
  [ ] Drift detection with severity levels
  [ ] Context restoration briefing format specified
  [ ] Edge cases handled (corrupted, old, partial, missing)
  [ ] Progressive disclosure (references/troubleshooting.md)
  [ ] Read-only enforced (no file modifications)
  [ ] No README.md in skill folder
  [ ] Briefing includes recommended next action
  [ ] ASCII-only
-->

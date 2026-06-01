# Template: State-Save Skill (/state-save)

<!-- TEMPLATE ANNOTATION
  This template defines the /state-save skill that captures session state
  across 6 universal categories. It writes JSON for programmatic state and
  Markdown for human-readable context.

  QUALITY CRITERIA:
  - Skill description includes 3+ trigger phrases
  - SKILL.md body under 500 lines
  - Progressive disclosure (SKILL.md + scripts/ + references/)
  - 6-category taxonomy fully specified
  - JSON output format for programmatic state
  - Markdown output for human context
  - Composability: checks state independently
  - Domain-specific state examples

  WHY THIS EXISTS:
  Sessions end. Context compacts. Claude Code restarts. Without state-save,
  every new session starts from zero. The 6-category taxonomy ensures all
  types of state are captured: tool state (what the environment looks like),
  task state (what we are doing), artifact state (what we produced), decision
  state (why we chose this approach), blocked state (what we are waiting for),
  and drift risk (what might change while we are away).
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application

  File structure:
  .claude/skills/state-save/
    SKILL.md              (this file -- core instructions)
    scripts/
      capture-vcs-state.sh  (captures git status, branch, recent commits)
    references/
      taxonomy.md           (detailed taxonomy with examples)
============================================================ -->

## SKILL.md

```yaml
---
name: state-save
description: Capture current session state for later restoration. Use when the user says "save state", "save progress", "save my work", "I'm done for now", "before I clear", or "/state-save". Do NOT use for saving files or committing code.
context: fork
allowed-tools: [Read, Write, Bash, Glob]
metadata:
  author: Claude Harness Generator
  version: 1.0.0
---
```

<!-- CRITICAL INSTRUCTIONS AT TOP
  WHY: "Critical instructions at TOP of SKILL.md" (Amendment 10f).
  The most important behavior must be the first thing Claude reads.
-->

## Critical

- Write TWO files: `Docs/_working/state/SESSION_SNAPSHOT.json` (programmatic) and `Docs/_working/state/SESSION_CONTEXT.md` (human narrative)
- Capture ALL 6 categories. Skip categories cleanly if data is unavailable.
- Each category checks its own state independently (do not assume prior skill execution)
- Do NOT modify any source files. This skill is read-and-capture only.

## State taxonomy

<!-- 6-CATEGORY TAXONOMY
  WHY: A flat "save everything" approach misses important state types.
  The 6 categories ensure comprehensive coverage across different dimensions.
  JSON format chosen because models corrupt Markdown more than JSON.
-->

Capture state across these 6 categories:

### 1. Tool state
What the development environment looks like right now.

- VCS: Run `scripts/capture-vcs-state.sh` (or equivalent). Captures branch, dirty files, recent commits.
  - If VCS is not configured: write `"vcs": "not_configured"` and continue
- Build: Last build result (success/failure/unknown)
- External tools: Any running servers, active connections, environment state

### 2. Task state
What we are working on.

- Current goal (one sentence)
- What is done (completed steps)
- What remains (next steps)
- Current checkpoint or milestone name

### 3. Artifact state
What files or documents were created or modified in this session.

- List of file paths changed (full paths)
- For each: what was changed and why (one line)
- New files created (paths only)
- Do NOT include file contents -- just paths and descriptions

### 4. Decision state
Key choices made during this session and their rationale.

- Decisions that affect future work (approach chosen, trade-offs accepted)
- Alternatives considered and why they were rejected
- Constraints discovered that were not known before

### 5. Blocked state
What is waiting on the user or an external process.

- Pending user decisions (questions asked but not answered)
- External dependencies (API access, credentials, third-party services)
- Playtest or review gates not yet completed

### 6. Drift risk
What could change externally while this session is paused.

- Files modified by this session that teammates might also change
- Dependencies that might update (packages, APIs, schemas)
- Time-sensitive items (deadlines, expiring tokens, scheduled deployments)

## Output format

### SESSION_SNAPSHOT.json

```json
{
  "timestamp": "2026-02-14T15:30:00Z",
  "session_id": "abc-123",
  "tool": {
    "vcs": {
      "type": "git",
      "branch": "feature/csv-export",
      "dirty_files": ["src/api/export.py", "src/components/ExportButton.tsx"],
      "recent_commits": ["abc1234 Add export endpoint skeleton", "def5678 Fix customer query"]
    },
    "build": "success",
    "servers": ["uvicorn on :8000"]
  },
  "task": {
    "goal": "Add CSV export to analytics dashboard",
    "done": ["Backend endpoint created", "Basic serialization working"],
    "remaining": ["Frontend button component", "Date range filtering", "Tests"],
    "checkpoint": "PT-02"
  },
  "artifact": {
    "modified": [
      {"path": "src/api/export.py", "change": "New endpoint for CSV generation"},
      {"path": "src/models/export.py", "change": "Export schema definition"}
    ],
    "created": [
      "src/api/export.py",
      "tests/test_export.py"
    ]
  },
  "decision": {
    "choices": [
      {"decision": "Use streaming response for large exports", "rationale": "Memory-efficient for datasets over 10K rows", "alternatives": ["Load all into memory -- rejected due to OOM risk"]}
    ]
  },
  "blocked": {
    "items": [
      {"type": "user_decision", "description": "Maximum export row limit -- user to decide"}
    ]
  },
  "drift": {
    "risks": [
      {"file": "src/api/customers.py", "risk": "Shared endpoint file, teammate may modify"},
      {"dependency": "pandas", "risk": "Used for CSV generation, pinned to 2.1.x"}
    ]
  }
}
```

### SESSION_CONTEXT.md

```markdown
# Session Context

Last saved: 2026-02-14 15:30 UTC

## Current task
Adding CSV export to the analytics dashboard. Backend endpoint is working,
frontend component and tests remain.

## Progress
- Created export endpoint with streaming response (memory-efficient)
- Export schema defined, basic serialization working
- Chose streaming over in-memory approach to handle large datasets

## Remaining
- Frontend ExportButton component
- Date range filtering on export
- Unit and integration tests

## Blocked
- Need user decision on maximum export row limit

## Key files
- src/api/export.py (new)
- src/models/export.py (new)
- tests/test_export.py (new, skeleton only)

## Drift risks
- src/api/customers.py is a shared file -- check for teammate changes
```

## Execution steps

1. Read the current conversation to extract state for all 6 categories
2. If VCS is configured, run `scripts/capture-vcs-state.sh` to capture tool state
3. If VCS is not configured, set `"vcs": "not_configured"` in tool state
4. Scan `Docs/_working/state/` for any existing state files (note if overwriting)
5. Write `SESSION_SNAPSHOT.json` with all 6 categories
6. Write `SESSION_CONTEXT.md` with human-readable narrative
7. Confirm: "State saved. X files tracked, Y decisions recorded, Z items blocked."

## scripts/capture-vcs-state.sh

<!-- SCRIPT REFERENCE
  WHY: Shell script captures VCS state more reliably than generating commands
  inline. The script handles edge cases (not a git repo, no commits yet, etc.)
  and returns structured output that the skill can parse.
-->

```bash
#!/usr/bin/env bash
# Capture VCS state for state-save skill
# Output: JSON fragment for tool.vcs

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo '{"type": "git", "status": "not_a_repo"}'
  exit 0
fi

BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
DIRTY=$(git diff --name-only 2>/dev/null | head -20)
STAGED=$(git diff --cached --name-only 2>/dev/null | head -20)
RECENT=$(git log --oneline -5 2>/dev/null || echo "no commits")

cat <<EOF
{
  "type": "git",
  "branch": "$BRANCH",
  "dirty_files": [$(echo "$DIRTY" | sed 's/.*/"&"/' | paste -sd, -)],
  "staged_files": [$(echo "$STAGED" | sed 's/.*/"&"/' | paste -sd, -)],
  "recent_commits": [$(echo "$RECENT" | sed 's/.*/"&"/' | paste -sd, -)]
}
EOF
```

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - VCS = git (branch, dirty files, commits)
  - Build = test suite, linter results
  - Drift = shared files, dependency updates

  KNOWLEDGE WORK:
  - VCS = usually none (set "not_configured")
  - Tool state = document editor state, research sources open
  - Task state = research progress, draft status
  - Drift risk = source documents being updated, deadlines

  GAME DEVELOPMENT:
  - VCS = Perforce (CL number, opened files, shelved changes)
  - Tool state = build result, editor PIE state
  - capture-vcs-state.sh uses p4 commands instead of git
  - Additional category consideration: playtest status

  PERFORCE VCS SCRIPT:
  ```bash
  #!/usr/bin/env bash
  if ! p4 info >/dev/null 2>&1; then
    echo '{"type": "perforce", "status": "not_connected"}'
    exit 0
  fi
  OPENED=$(p4 opened 2>/dev/null | head -20)
  PENDING=$(p4 changes -s pending -c $(p4 client -o | grep ^Client: | awk '{print $2}') 2>/dev/null | head -5)
  echo "{\"type\": \"perforce\", \"opened_files\": \"$(echo $OPENED | wc -l) files\", \"pending_cls\": \"$(echo $PENDING)\"}"
  ```
-->

<!-- ANTI-PATTERNS

  1. SAVING FILE CONTENTS
     Problem: State file becomes enormous with full source code.
     Fix: Save paths and descriptions only. Never include file contents.

  2. FLAT STATE FORMAT
     Problem: Everything in one list -- hard to parse, easy to miss categories.
     Fix: Use 6-category taxonomy. Each category is structurally separate.

  3. MARKDOWN-ONLY STATE
     Problem: Models corrupt Markdown headers, lists, and formatting over time.
     Fix: JSON for programmatic state (less corruption). Markdown only for human narrative.

  4. ASSUMING VCS IS CONFIGURED
     Problem: Script crashes on projects without git.
     Fix: Check for VCS first. Set "not_configured" and skip gracefully.

  5. MODIFYING SOURCE FILES
     Problem: State-save accidentally edits files it is supposed to only read.
     Fix: "Do NOT modify any source files. This skill is read-and-capture only."

  6. NOT COMPOSABLE
     Problem: State-save assumes state-load ran first, or some other skill set up state.
     Fix: Each category checks its own state independently.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Skill description includes 3+ trigger phrases
  [ ] Negative trigger present ("Do NOT use for saving files or committing code")
  [ ] SKILL.md body under 500 lines
  [ ] Critical instructions at top
  [ ] All 6 taxonomy categories covered
  [ ] JSON output format with complete example
  [ ] Markdown output format with complete example
  [ ] VCS script handles "not configured" gracefully
  [ ] Composability: each category checks independently
  [ ] Read-only: no source file modifications
  [ ] Progressive disclosure structure (SKILL.md + scripts/ + references/)
  [ ] No README.md in skill folder
  [ ] Output paths specified (Docs/_working/state/)
  [ ] Confirmation message format specified
  [ ] ASCII-only
-->

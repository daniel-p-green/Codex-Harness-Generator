# Hooks Configuration (Template)

<!-- ANNOTATION: Hooks are optional but powerful. Generate hook configuration
     when the project benefits from automated quality gates, audit trails,
     or domain-specific protections. Hooks go in .codex/config.toml, not in a
     separate rule file. This template shows the component-generator how
     to design hooks for different domains. -->

<!-- QUALITY: Must reference all 14 hook events. Must demonstrate exit code 2
     feedback pattern. Must include PreToolUse allow/deny pattern. Must
     include at least one industry-specific example. -->

## Hook Events Reference

<!-- ANNOTATION: This is the complete list. The component-generator should
     select only the events relevant to the user's domain. Most environments
     need at most 2-3 hooks. -->

| Event | When | Can Block? | Common Use |
|-------|------|-----------|------------|
| SessionStart | Session begins/resumes | No | Environment setup, state loading |
| InstructionsLoaded | AGENTS.md/rules load | Yes | Self-learning trigger, context refresh |
| UserPromptSubmit | User submits prompt | Yes | Input validation, audit |
| PreToolUse | Before tool executes | Yes (allow/deny/ask) | Safety gates, binary protection |
| PermissionRequest | Permission dialog | Yes | Auto-approve known-safe ops |
| PostToolUse | After tool succeeds | No (feedback) | Linting, formatting, audit trail |
| PostToolUseFailure | After tool fails | No | Error logging |
| Notification | Notification sent | No | External alerting |
| SubagentStart | Subagent spawned | No | Logging, resource tracking |
| SubagentStop | Subagent finishes | Yes | Result validation |
| Stop | Codex finishes responding | Yes | Final checks |
| TeammateIdle | Teammate going idle | Yes | Task reassignment |
| TaskCompleted | Task marked complete | Yes | Quality verification |
| PreCompact | Before compaction | No | State preservation |
| SessionEnd | Session terminates | No | Cleanup, final audit |

**New events (2025+)**: `ConfigChange` (settings modified), `WorktreeCreate` /
`WorktreeRemove` (git worktree lifecycle), `InstructionsLoaded` (AGENTS.md or
rules load, includes `agent_id` and `agent_type` fields). These are available in
Codex v2.1+ and useful for environments with worktree-based agent isolation
or self-learning triggers.

**Handler types**: Three handler types are available:
- `command` (default): Shell script, 600s timeout
- `prompt`: Single LLM evaluation, 30s timeout (platform-independent)
- `agent`: Multi-turn subagent with tools, 60s timeout (platform-independent)

Use `prompt` or `agent` types for platform-independent hooks that work on all OS.

## Exit Code 2 Feedback Pattern

<!-- ANNOTATION: Exit code 2 is the key mechanism for hooks to communicate
     with Codex. When a hook exits with code 2, stderr content is fed
     back to Codex as context. This enables build-fix-rebuild loops,
     lint-fix cycles, and validation feedback. -->

```bash
#!/bin/bash
# Example: PostToolUse hook that runs linter after file edits
# Exit 0 = success (no feedback to Codex)
# Exit 2 = blocking feedback (stderr sent to Codex)
# Other = non-blocking error (shown in verbose mode only)

INPUT=$(cat)  # Read JSON from stdin
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

if [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "Write" ]; then
    RESULT=$(npm run lint 2>&1)
    if [ $? -ne 0 ]; then
        echo "$RESULT" >&2
        exit 2  # Feed lint errors back to Codex
    fi
fi
exit 0
```

## PreToolUse Allow/Deny Pattern

<!-- ANNOTATION: PreToolUse hooks can make permission decisions on behalf
     of the user. This is how you implement domain-specific safety gates
     without relying on .codex/config.toml alone. -->

```bash
#!/bin/bash
# Example: Block edits to binary assets (game dev)
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input')

if [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "Write" ]; then
    FILE=$(echo "$TOOL_INPUT" | jq -r '.file_path // .path // empty')
    if echo "$FILE" | grep -qE '\.(uasset|umap|psd|fbx)$'; then
        cat <<'DENY' >&2
Cannot edit binary asset files directly. Write the exact editor
steps needed and stop for the user to make the change manually.
DENY
        # Output JSON decision
        echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Binary asset protection"}}'
        exit 0
    fi
fi
exit 0
```

## PostToolUse Audit Pattern

<!-- ANNOTATION: Audit hooks record what Codex does for compliance or
     debugging. They should be async (non-blocking) to avoid slowing
     down the workflow. -->

```bash
#!/bin/bash
# Example: Append tool usage to an audit log
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "$TIMESTAMP | $TOOL_NAME | $(echo "$INPUT" | jq -c '.tool_input')" \
    >> "$CODEX_PROJECT_DIR/Docs/audit-log.txt"
exit 0
```

## Industry-Specific Examples

### Software Development: Lint after edit

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{
          "type": "command",
          "command": "./scripts/lint-changed.sh",
          "timeout": 30,
          "statusMessage": "Running linter..."
        }]
      }
    ]
  }
}
```

### Game Development: Binary asset protection

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{
          "type": "command",
          "command": "./scripts/check-binary.sh",
          "timeout": 5,
          "statusMessage": "Checking file type..."
        }]
      }
    ]
  }
}
```

### Legal / Compliance: Audit trail

<!-- VARIATION: Legal and compliance domains need a record of every action
     Codex takes. Use async hooks to avoid blocking the workflow. -->

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [{
          "type": "command",
          "command": "./scripts/audit-log.sh",
          "async": true,
          "statusMessage": "Logging action..."
        }]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [{
          "type": "command",
          "command": "./scripts/finalize-audit.sh",
          "statusMessage": "Finalizing audit trail..."
        }]
      }
    ]
  }
}
```

### Compliance: PII content scanning (PreToolUse gate)

<!-- ANNOTATION: This is the highest-priority hook for environments handling
     regulated data (financial, healthcare, legal). Unlike advisory rules
     that depend on the model following instructions, this hook deterministically
     blocks writes containing sensitive data patterns. Use when GENESIS.md
     indicates sensitive/regulated data. Combine with the sensitive-data-rule
     template for defense-in-depth (advisory + deterministic). -->

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "command",
          "command": ".codex/hooks/pii-scan.sh",
          "timeout": 10,
          "statusMessage": "Scanning for sensitive data..."
        }]
      }
    ]
  }
}
```

Example hook script (`.codex/hooks/pii-scan.sh`):

```bash
#!/bin/bash
# PII content scanner -- blocks writes containing sensitive data patterns.
# Reads tool input from stdin, scans content for PII regex patterns.
# Exit 0 = clean (allow write). Exit code 2 = PII found (block + feedback).
# Patterns are loaded from a config file so domain experts can update them.

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

# Only scan Write and Edit tool calls
if [ "$TOOL_NAME" != "Write" ] && [ "$TOOL_NAME" != "Edit" ]; then
    exit 0
fi

# Extract content being written
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty')
if [ -z "$CONTENT" ]; then
    exit 0
fi

# Load patterns from config (one regex per line, # comments allowed)
PATTERN_FILE="$CODEX_PROJECT_DIR/.codex/hooks/pii-patterns.conf"
if [ ! -f "$PATTERN_FILE" ]; then
    # Fallback: common PII patterns
    PATTERNS=(
        '\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b'           # SSN (xxx-xx-xxxx)
        '\b[0-9]{3}\s[0-9]{2}\s[0-9]{4}\b'          # SSN (xxx xx xxxx)
        '\b[0-9]{16}\b'                               # Credit card (16 digits)
        '\b[0-9]{4}[\s-][0-9]{4}[\s-][0-9]{4}[\s-][0-9]{4}\b'  # Credit card (grouped)
    )
else
    PATTERNS=()
    while IFS= read -r line; do
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue
        PATTERNS+=("$line")
    done < "$PATTERN_FILE"
fi

FOUND=""
for PATTERN in "${PATTERNS[@]}"; do
    MATCHES=$(echo "$CONTENT" | grep -oP "$PATTERN" 2>/dev/null)
    if [ -n "$MATCHES" ]; then
        COUNT=$(echo "$MATCHES" | wc -l)
        FOUND="${FOUND}Pattern '${PATTERN}' matched ${COUNT} time(s). "
    fi
done

if [ -n "$FOUND" ]; then
    echo "BLOCKED: Sensitive data detected in output. ${FOUND}Redact all sensitive values (replace with [REDACTED] or placeholder) and retry." >&2
    exit 2
fi

exit 0
```

Example pattern config file (`.codex/hooks/pii-patterns.conf`):

```
# PII Detection Patterns -- one regex per line
# Customize for your domain. Lines starting with # are comments.

# SSN formats
\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b
\b[0-9]{3}\s[0-9]{2}\s[0-9]{4}\b

# Credit card (16 consecutive digits or grouped in 4s)
\b[0-9]{16}\b
\b[0-9]{4}[\s-][0-9]{4}[\s-][0-9]{4}[\s-][0-9]{4}\b

# Phone numbers (US formats)
\b\(?[0-9]{3}\)?[\s.-][0-9]{3}[\s.-][0-9]{4}\b

# Email addresses (uncomment if email counts as PII in your domain)
# \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}\b

# Financial account numbers (uncomment and customize for your institution)
# \b[0-9]{9,12}\b
```

<!-- VARIATION: For healthcare (HIPAA), add MRN and diagnosis code patterns.
     For financial (SOX), add account and routing number patterns.
     For legal, add case number + client name co-occurrence patterns.
     Keep patterns in the .conf file so compliance officers can update them
     without modifying hook scripts. -->

**PowerShell variant** (for Windows-primary environments):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "command",
          "command": "powershell -File .codex/hooks/pii-scan.ps1",
          "timeout": 10,
          "statusMessage": "Scanning for sensitive data..."
        }]
      }
    ]
  }
}
```

**Prompt-based variant** (platform-independent, no scripts):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "prompt",
          "prompt": "Check if the following content contains PII (SSN, credit card numbers, phone numbers, account numbers, or email addresses with real names). If PII is found, respond with ONLY the word BLOCKED followed by what was found. If clean, respond with ONLY the word ALLOWED.",
          "timeout": 15
        }]
      }
    ]
  }
}
```

<!-- ANNOTATION: The prompt-based variant is less reliable than script-based
     (model judgment vs regex determinism) but works on any platform without
     script setup. Recommend script-based for regulated industries, prompt-based
     as a quick-start option for less regulated contexts. -->

### Compliance: UserPromptSubmit input screening

<!-- ANNOTATION: Prevents accidentally pasted sensitive data from entering
     the conversation context. If a user pastes a spreadsheet with SSNs
     into their prompt, this catches it before the model sees it. -->

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [{
          "type": "command",
          "command": ".codex/hooks/pii-scan-input.sh",
          "timeout": 5,
          "statusMessage": "Checking input for sensitive data..."
        }]
      }
    ]
  }
}
```

The input screening script uses the same pattern file as the write scanner but
reads from `user_prompt` in the stdin JSON instead of `tool_input`. On match,
it blocks the prompt and warns the user to remove sensitive data before resubmitting.

### InstructionsLoaded: Self-learning trigger

<!-- ANNOTATION: Preferred over SessionStart for self-learning triggers because
     it fires on rule reload too, not just session init. Counts retro/ entries
     and recommends /update when threshold is reached. -->

```json
{
  "hooks": {
    "InstructionsLoaded": [
      {
        "hooks": [{
          "type": "command",
          "command": "count=$(find Docs/_working/retro/ -name '*.md' 2>/dev/null | wc -l); if [ \"$count\" -ge 5 ]; then echo \"$count unprocessed retro entries. Run /update to incorporate learnings.\" >&2; exit 2; fi",
          "timeout": 5
        }]
      }
    ]
  }
}
```

PowerShell variant (Windows-primary):
```json
{
  "hooks": {
    "InstructionsLoaded": [
      {
        "hooks": [{
          "type": "command",
          "command": "powershell -NoProfile -Command \"$c=(Get-ChildItem Docs/_working/retro/*.md -ErrorAction SilentlyContinue).Count; if($c -ge 5){Write-Error \\\"$c unprocessed retro entries. Run /update to incorporate learnings.\\\"; exit 2}\""
        }]
      }
    ]
  }
}
```

### PreCompact: Auto-save state before compaction

<!-- ANNOTATION: This is one of the most impactful hooks. Auto-compaction at ~95%
     can silently discard progress. This hook writes a timestamped summary to
     SESSION_CONTEXT.md before compaction occurs, ensuring no progress is lost. -->

```json
{
  "hooks": {
    "PreCompact": [
      {
        "hooks": [{
          "type": "command",
          "command": ".codex/hooks/pre-compact-save.sh",
          "timeout": 10,
          "statusMessage": "Saving state before compaction..."
        }]
      }
    ]
  }
}
```

Example hook script (`.codex/hooks/pre-compact-save.sh`):

```bash
#!/bin/bash
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
STATE_FILE="$CODEX_PROJECT_DIR/Docs/_working/state/SESSION_CONTEXT.md"
echo "" >> "$STATE_FILE"
echo "## Auto-save before compaction ($TIMESTAMP)" >> "$STATE_FILE"
echo "Session was compacted. Review above for pre-compaction context." >> "$STATE_FILE"
exit 0
```

### Status line monitoring

<!-- ANNOTATION: Status line displays information in the terminal without consuming
     conversation context. This is zero-cost monitoring. Use hooks to update a
     state file that the status line script reads. -->

Status line hooks work together: a UserPromptSubmit hook tracks activity, a PostToolUse
hook tracks turn count, and the status line script reads the state file to display info.

```json
{
  "env": {
    "CODEX_STATUSLINE": ".codex/hooks/statusline.sh"
  }
}
```

**Portability**: Status line scripts require bash. For Windows environments, document
the WSL/Git Bash requirement or use PowerShell alternatives.

### Agent-based hooks (multi-turn verification)

<!-- ANNOTATION: Agent hooks ("type": "agent") spawn a subagent with tool access.
     Use when verification requires reading files, running commands, or multi-step
     reasoning. More expensive than command hooks (~4x) but more capable. -->

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "agent",
        "prompt": "Verify all modified files compile and pass lint. Report any issues.",
        "timeout": 60
      }]
    }]
  }
}
```

Agent hooks are appropriate for: post-implementation validation, compliance checks
requiring document cross-reference, complex pre-commit verification. Do NOT use for
simple checks a shell script can handle.

### Stop hook: Self-review loop

<!-- ANNOTATION: This is the highest-leverage hook pattern. An independent agent
     reviews all work before the user sees it, creating a self-correcting quality
     gate. Exit code 2 feeds issues back to Codex for correction. -->

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "agent",
        "prompt": "Review all files modified in this session. Check for: compilation errors, missing error handling at system boundaries, security issues (injection, XSS), broken tests. If you find Critical or High issues, list them clearly. If everything looks good, say LGTM.",
        "timeout": 120
      }]
    }]
  }
}
```

**Critical**: The reviewing agent must detect re-entry to prevent infinite loops.
Check the `stop_hook_active` field in the hook input JSON -- if already true, exit
immediately. Alternatively, limit to one review iteration via a temp file flag.

This pattern provides an independent second opinion on every task. The reviewing
agent has a fresh context since it did not write the code. Validated as the
highest-leverage quality practice by O'Reilly and OpenAI documentation.

## Settings.json Integration

<!-- ANNOTATION: Hooks are configured in .codex/config.toml alongside
     permissions. The component-generator should merge hook config
     with the permissions config, not create a separate file. -->

Hooks go in `.codex/config.toml` under the `"hooks"` key, at the same
level as `"permissions"`. Most environments need at most 2-3 hook entries.
Do not over-hook -- each hook adds latency to every matching operation.

<!-- QUALITY: Validation checklist for the generator:
     - [ ] Only hooks relevant to the domain are included
     - [ ] Exit code 2 pattern used for feedback hooks
     - [ ] PreToolUse hooks output valid JSON decision format
     - [ ] Async flag used for non-blocking hooks (audit, logging)
     - [ ] Timeout specified for each hook
     - [ ] statusMessage provided for user-visible hooks
     - [ ] Total hooks <= 3 for most environments
     - [ ] PreCompact hook included for environments with long sessions
     - [ ] Platform-appropriate hook format (bash vs PowerShell vs prompt/agent)
     - [ ] Stop hook self-review included for software/game dev environments
-->

<!-- ANTI-PATTERN: Do not add hooks for every event. Most environments
     need 0-2 hooks. Do not use hooks to implement logic that belongs
     in rules (hooks are deterministic scripts, not advisory guidance).
     Do not use synchronous hooks for logging (blocks Codex). -->

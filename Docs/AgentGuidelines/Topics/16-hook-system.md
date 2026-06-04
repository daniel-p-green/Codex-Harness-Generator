# 16. Hook System

## 16.1 Hook Events (Expanded in April 2026)

- **Established**: Baseline; updated 2026-05-31
- **Source**: https://developers.openai.com/codex, developers.openai.com/codex | Tier 1
- **Recommendation**: The hook system now supports 20+ lifecycle events. Core events (stable,
  safe to rely on):

  | Event | When | Can Block? |
  |-------|------|-----------|
  | SessionStart | Session begins/resumes | No |
  | MessageDisplay | Before assistant text is shown; transform/hide it (v2.1.152) | No (rewrite only) |
  | UserPromptSubmit | User submits prompt | Yes |
  | PreToolUse | Before tool executes | Yes (allow/deny/ask/defer) |
  | PermissionRequest | Permission dialog appears | Yes |
  | PermissionDenied | After auto-mode classifier denial (v2.1.89) | Yes (retry: true) |
  | PostToolUse | After tool succeeds | No (feedback only) |
  | PostToolUseFailure | After tool fails | No |
  | Notification | Notification sent | No |
  | SubagentStart | Subagent spawned | No |
  | SubagentStop | Subagent finishes | Yes |
  | Stop | Codex finishes responding | Yes |
  | StopFailure | Turn ends due to API error (v2.1.78) | No |
  | TeammateIdle | Teammate going idle | Yes |
  | TaskCompleted | Task marked complete | Yes |
  | TaskCreated | Task created via TaskCreate (v2.1.84) | No |
  | PreCompact | Before compaction | Yes (exit 2 or {"decision":"block"}, v2.1.105) |
  | PostCompact | After compaction completes (v2.1.76) | No |
  | SessionEnd | Session terminates | No |
  | CwdChanged | Working directory changes (v2.1.83) | No |
  | FileChanged | Files change on disk (v2.1.83) | No |
  | Elicitation / ElicitationResult | MCP elicitation requests (v2.1.76) | Yes |
  | WorktreeCreate | Worktree created (v2.1.84, now http-capable) | No |

  Three handler types: `command` (shell script), `prompt` (single LLM evaluation),
  `agent` (multi-turn subagent with tools). Default timeouts: 600s command, 30s prompt,
  60s agent.

  Hook matchers: Strings only (e.g., `"Write|Edit"`). Events WITHOUT tool-specific matching
  (PreCompact, PostCompact, SessionStart, SessionEnd, Stop, UserPromptSubmit, CwdChanged,
  FileChanged) OMIT the matcher field entirely.

  Conditional hook execution: Hooks can be gated by the current Codex hook schema
  when that schema exposes conditions. Verify the exact field names before
  generating a hook.

  Stop and SubagentStop hooks now receive `last_assistant_message` in the input payload.

  Windows: Hooks now use Git Bash reliably; earlier Windows failures are fixed.
- **Anti-pattern**:
  - Not using hooks for quality enforcement. Unlike AGENTS.md (advisory), hooks are
    deterministic and guaranteed to execute.
  - Using an object matcher (e.g., `{"tool": "Write"}`) -- matchers must be strings.
  - Adding a matcher field to non-tool events like PreCompact.

## 16.2 Exit Code 2 Feedback

- **Established**: Baseline
- **Source**: https://developers.openai.com/codex | Tier 1
- **Recommendation**: Exit code 2 is the mechanism for hook-to-Codex communication:
  - Exit 0: Success, JSON output parsed from stdout
  - Exit 2: Blocking error. Stderr content is fed to Codex as feedback. For PreToolUse,
    this blocks the tool call.
  - Other exit codes: Non-blocking error, shown in verbose mode only

  Use exit code 2 for: lint failures, test failures, format violations, policy violations.
  Codex receives the error message and can self-correct.
- **Anti-pattern**: Using exit code 1 (non-zero, non-2) for feedback. Only exit code 2
  feeds the error message to Codex. Other non-zero codes are silently swallowed.

## 16.3 PreToolUse Allow/Deny

- **Established**: Baseline
- **Source**: https://developers.openai.com/codex | Tier 1
- **Recommendation**: PreToolUse hooks can return permission decisions:
  ```json
  {
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "allow|deny|ask",
      "permissionDecisionReason": "Reason text",
      "updatedInput": {"command": "modified command"},
      "additionalContext": "Extra context for Codex"
    }
  }
  ```

  Use cases: block binary file edits, enforce naming conventions, redirect destructive
  commands, add safety wrappers to dangerous operations.
- **Anti-pattern**: Using PreToolUse hooks that silently modify commands without
  `additionalContext`. Codex should know what the hook changed and why.

## 16.4 PostToolUse Audit

- **Established**: Baseline
- **Source**: https://developers.openai.com/codex/subagents | Tier 1
- **Recommendation**: PostToolUse hooks for audit trails and automated side effects:
  - Track file modifications (which files, when, word count)
  - Log script executions
  - Run linters after file edits
  - Update dashboards or monitoring
  - Generate compliance records

  Hooks receive JSON via stdin with `tool_name`, `tool_input`, `tool_response`. Keep audit
  logs bounded (e.g., last 50 entries). Use async hooks for non-blocking audit operations.
- **Anti-pattern**: Not auditing file modifications in regulated environments. Hooks provide
  deterministic audit trails that AGENTS.md instructions cannot guarantee.

## 16.5 Industry Examples

- **Established**: Baseline
- **Source**: https://developers.openai.com/codex, https://developers.openai.com/codex/subagents | Tier 1
- **Recommendation**: Domain-specific hook patterns:
  - **Software dev**: post-edit hook -> run eslint/prettier. pre-command hook ->
    block destructive git commands.
  - **Game dev**: pre-edit hook -> block .uasset/.umap modifications. post-build hook -> update DLL tracking.
  - **Finance/compliance**: post-write hook -> audit trail logging. Stop -> generate
    compliance summary.
  - **CI/CD**: SessionStart -> verify environment. Stop -> commit and push results.
  - **Content**: PostToolUse on Write -> run style guide checker. Stop -> generate revision
    summary.
- **Anti-pattern**: Generic hooks that do not match the domain's specific quality and
  compliance requirements.

## 16.6 Agent-Based Hooks

- **Established**: 2026-02
- **Source**: https://developers.openai.com/codex | Tier 1
- **Recommendation**: Hooks can use `"type": "agent"` for multi-turn verification that
  needs tool access. Agent hooks spawn a subagent with a 60-second default timeout.

  Use cases: post-implementation validation that requires reading multiple files,
  compliance checks that need to cross-reference documents, complex pre-commit
  verification.

  ```json
  {
    "hooks": {
      "Stop": [{
        "hooks": [{
          "type": "agent",
          "prompt": "Verify all modified files compile and pass lint checks.",
          "timeout": 60
        }]
      }]
    }
  }
  ```

  Agent hooks are more expensive than command hooks (~4x a single tool call) but can
  perform multi-step verification that shell scripts cannot.
- **Anti-pattern**: Using agent hooks for simple checks that a shell script can handle.
  Agent hooks should only be used when the verification requires tool access and
  multi-step reasoning.

## 16.7 Hook Portability

- **Established**: 2026-02
- **Source**: production game project production environment | Tier 2
- **Recommendation**: Bash hooks (.sh files) require a Unix shell. On Windows, this
  means either WSL or Git Bash must be available. For cross-platform environments:

  - **Option A**: Use bash hooks with a documented WSL/Git Bash dependency
  - **Option B**: Use PowerShell hooks (.ps1) for Windows-primary environments
  - **Option C**: Use `"type": "prompt"` or `"type": "agent"` hooks which are
    platform-independent (they run within Codex, not in a shell)

  When generating environments, detect the target platform from GENESIS.md and choose
  the appropriate hook format. Document any shell dependencies in GETTING_STARTED.md.
- **Anti-pattern**: Generating bash hooks for Windows-primary teams without documenting
  the WSL dependency. The hooks silently fail, providing no protection.

## 16.8 Stop Hook Self-Review Loop

- **Established**: 2026-02
- **Source**: https://developers.openai.com/codex, O'Reilly "Auto-Reviewing Codex's Code" | Tier 1
- **Recommendation**: Use a Stop hook to trigger an independent self-review whenever
  Codex finishes a task. This creates a self-correcting loop:

  1. Codex completes work and attempts to stop
  2. Stop hook runs an independent review (via agent or command)
  3. If issues found: exit code 2 feeds feedback back to Codex
  4. Codex addresses the feedback and attempts to stop again
  5. Loop continues until review passes (or max iterations reached)

  Implementation:

  ```json
  {
    "hooks": {
      "Stop": [{
        "hooks": [{
          "type": "agent",
          "prompt": "Review all files modified in this session. Check for: compilation errors, missing error handling, security issues, broken tests. If you find issues, list them clearly. If everything looks good, say LGTM.",
          "timeout": 120
        }]
      }]
    }
  }
  ```

  **Critical**: The hook must detect re-entry to prevent infinite loops. Check the
  `stop_hook_active` field in the input JSON and exit early if already in a review cycle.
  Alternatively, limit to one review iteration by tracking state in a temp file.

  This pattern provides an independent second opinion on every task. The reviewing agent
  has a fresh perspective since it did not write the code. Combined with test verification,
  this catches the majority of issues before they reach the user.
- **Anti-pattern**: Having the main agent review its own work inline. Self-review in the
  same context is less effective than an independent review from a separate agent with
  a fresh context window.

## 16.9 Compliance Enforcement Hooks

- **Established**: 2026-03
- **Source**: Hook system docs, HIPAA/SOX/GDPR compliance patterns | Tier 2
- **Recommendation**: For environments handling sensitive data (PII, PHI, financial records,
  legal privilege), use deterministic hooks to enforce compliance -- not just advisory rules.
  Advisory rules (sensitive-data-rule.md) tell Codex what to do; enforcement hooks guarantee
  it happens regardless of model behavior.

  **Three enforcement patterns**:

  **Pattern 1: PreToolUse content gate** -- Scan content being written for sensitive patterns
  before allowing the write. Runs on Write and Edit tool calls. Inspects `tool_input` for
  regex matches (SSN, email, phone, credit card, account numbers). On match: deny the write
  and feed the specific findings back to Codex via exit code 2, so it can redact and retry.

  ```json
  {
    "hooks": {
      "PreToolUse": [{
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "command",
          "command": ".codex/hooks/pii-scan.sh",
          "timeout": 10,
          "statusMessage": "Scanning for sensitive data..."
        }]
      }]
    }
  }
  ```

  **Pattern 2: PostToolUse redaction** -- After a file is written, scan and redact sensitive
  data in place. Less strict than Pattern 1 (allows the write, then fixes) but catches cases
  where PII appears in tool output or generated content. Useful as a safety net behind
  Pattern 1. Log redactions to the audit trail.

  **Pattern 3: UserPromptSubmit input screening** -- Scan user input for accidentally pasted
  sensitive data (credit card numbers, SSNs, full account numbers) before it enters the
  conversation context. On match: block the prompt and warn the user. This prevents sensitive
  data from entering the model's context in the first place.

  **Implementation notes**:
  - PII patterns must be domain-specific. Financial: account numbers, routing numbers, SSNs.
    Healthcare: MRNs, diagnosis codes + patient names. Legal: case numbers + client names.
  - Use the `updatedInput` field in PreToolUse JSON output to auto-redact while still allowing
    the write (replace SSN with `[SSN-REDACTED]` rather than blocking entirely).
  - Combine with PostToolUse audit hooks for a defense-in-depth approach.
  - On Windows, use PowerShell scripts or `"type": "prompt"` hooks for portability.
  - Keep regex patterns in a separate config file (`.codex/hooks/pii-patterns.conf`) so
    domain experts can update patterns without modifying hook scripts.
  - Test patterns against false positives: dates that look like SSNs, version numbers that
    match account number formats, etc.

- **Anti-pattern**: Relying solely on advisory rules (sensitive-data-rule.md) for compliance.
  Advisory rules depend on the model following instructions; enforcement hooks run
  deterministically. For regulated industries, advisory is necessary but not sufficient.
  Also: scanning only on Write but not Edit -- PII can be introduced via both tools.

## 16.10 InstructionsLoaded Hook

- **Established**: 2026-03
- **Source**: Codex v2.1.69+ docs | Tier 1
- **Recommendation**: The InstructionsLoaded event (v2.1.69+) fires when AGENTS.md or
  `.codex/rules/*.md` files are loaded. It includes `agent_id` and `agent_type` fields
  identifying which agent triggered the load.

  This is a better self-learning trigger than SessionStart because it fires on rule
  reload too (e.g., after compaction or when an agent spawns). Pattern: hook script
  reads the `retro/` directory, counts unprocessed entries, and outputs a recommendation
  via exit code 2 when 5+ entries exist. Codex receives the feedback and can suggest
  running /update.

  ```json
  {
    "hooks": {
      "InstructionsLoaded": [{
        "hooks": [{
          "type": "command",
          "command": ".codex/hooks/check-retro-entries.sh",
          "timeout": 5
        }]
      }]
    }
  }
  ```

  Also note: TeammateIdle and TaskCompleted hooks (experimental) are available for
  agent team quality gates. TeammateIdle fires when a teammate is about to go idle
  (can block to reassign work). TaskCompleted fires when a task is marked complete
  (can block to enforce review before acceptance).

- **Anti-pattern**: Using SessionStart for self-learning triggers when InstructionsLoaded
  is available. SessionStart only fires once; InstructionsLoaded fires on every rule
  load, catching cases where retro entries accumulate mid-session.

## 16.11 May 2026 Hook I/O Additions

- **Established**: 2026-05-31
- **Source**: developers.openai.com/codex (v2.1.139-v2.1.157) | Tier 1
- **Recommendation**: Several hook input/output fields landed in May 2026. Use them
  where they replace heavier patterns:

  **New input fields and env vars (all hooks)**:
  - `$CODEX_MODEL_REASONING_EFFORT` env var and `effort.level` in JSON input -- branch hook behavior
    by effort (e.g., skip an expensive review hook at `low`).
  - `$CODEX_PROJECT_DIR` now exported to MCP stdio servers; `$CODEX_SESSION_ID`
    in Bash tool and stdio MCP subprocesses.
  - PostToolUse / PostToolUseFailure now receive `duration_ms` (tool execution time)
    plus `background_tasks` and `session_crons`.

  **New output fields**:
  - `hookSpecificOutput.updatedToolOutput` (PostToolUse) -- replace tool output for ANY
    tool, not just MCP. Useful for redaction (extends 16.9 Pattern 2 to all tools).
  - `continueOnBlock: true` (PostToolUse) -- feed a rejection reason back to Codex
    instead of ending the turn.
  - `terminalSequence` -- emit desktop notifications, window titles, or bells without
    controlling the terminal (cleaner than echoing escape codes from a command hook).
  - `hookSpecificOutput.sessionTitle` (SessionStart) -- set the session title on
    start/resume.
  - `reloadSkills: true` (SessionStart) -- re-scan skill directories. Pairs with the new
    `/reload-skills` command; relevant for environments that generate skills dynamically.

  **Hook syntax**: hooks can declare `args: string[]` (exec form) to spawn the command
  directly without a shell (v2.1.139) -- safer quoting and faster than a shell string.
  Hooks can also invoke MCP tools directly via `"type": "mcp_tool"` (v2.1.118).

  **Windows note**: PowerShell hooks now pass `-ExecutionPolicy Bypass` by default
  (v2.1.143). Opt out with `CODEX_POWERSHELL_RESPECT_EXECUTION_POLICY=1`. This
  removes a common Windows-hook failure mode; reflect it in GETTING_STARTED.md hook
  setup notes for Windows-primary environments.
- **Anti-pattern**: Hand-rolling tool-output redaction by re-writing files in a separate
  hook when `updatedToolOutput` can replace the output inline. Also: emitting raw ANSI
  escape codes from command hooks instead of using `terminalSequence`.

---

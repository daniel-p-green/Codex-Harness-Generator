# Template: Error Handling Rule (04-error-handling.md)

<!-- TEMPLATE ANNOTATION
  This template defines how the generated environment handles failures gracefully.
  It covers agent failures, missing files, tool unavailability, state corruption,
  VCS not configured, and permission denied scenarios.

  QUALITY CRITERIA:
  - Under 120 lines in generated output
  - Every failure type has a specific recovery action
  - Graceful degradation (skip and note, do not crash)
  - No retry spirals (max 1 retry per failure)
  - Domain-specific failure types included

  WHY THIS EXISTS:
  Generated environments operate in unpredictable conditions. VCS may not be
  configured. Tools may be missing. State files may be corrupted. Without
  explicit error handling, Claude either crashes, retries infinitely, or
  silently produces wrong results. This rule ensures failures are handled
  gracefully with clear recovery paths.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application
============================================================ -->

# Error handling

<!-- CORE PRINCIPLE
  WHY: "Graceful degradation" means the environment continues to function
  even when components are missing or broken. It should never hard-fail
  on a recoverable error.
-->
When something fails, degrade gracefully: skip the failing component, note what
was skipped, and continue with available functionality. Never retry more than once.

## Agent failure

<!-- AGENT FAILURE
  WHY: Subagent invocations can fail (model error, timeout, bad tool use).
  Without handling, the orchestrator stalls or retries infinitely.
-->
When a delegated agent fails (error, timeout, or produces no useful output):

1. Log the failure: what agent, what task, what error
2. Report the failure to the user: "[agent-name] failed on [task]. Error: [brief description]"
3. Retry ONCE with a simplified objective (reduce scope, provide more specific guidance)
4. If retry fails, fall back to the next agent in the fallback chain (see routing rule)
5. If no fallback exists, report to the user and ask how to proceed

Do NOT:
- Retry the same failing operation more than once
- Silently swallow the error and continue as if it succeeded
- Escalate to a more expensive model without user awareness

## Missing file

<!-- MISSING FILE
  WHY: State files, memory files, or config files may not exist yet (new environment)
  or may have been accidentally deleted. Creating sensible defaults is better than
  failing.
-->
When a required file is not found:

| File type | Recovery action |
|---|---|
| `Docs/index.md` | Create with `Status: NEW_ENVIRONMENT` and empty structure |
| `Docs/_working/state/SESSION_SNAPSHOT.json` | Create empty JSON: `{"tool": {}, "task": {}, "artifact": {}, "decision": {}, "blocked": {}, "drift": {}}` |
| `Docs/_working/state/SESSION_CONTEXT.md` | Create with header and "No previous session state." |
| `Docs/_working/retro/YYYY-MM.md` | Create with header for the current month |
| `Docs/_working/retro/INDEX.md` | Create with empty theme list |
| `.claude/rules/*.md` | Note the missing rule file, continue without it |
| `.claude/agents/*.md` | Note the missing agent, use direct approach instead of delegation |
| `.claude/skills/*/SKILL.md` | Note the missing skill, inform user it is unavailable |
| Any source file referenced | Ask the user if the file was moved or renamed |

## Tool unavailable

<!-- TOOL UNAVAILABLE
  WHY: Tools may be disabled by permissions, sandboxing, or configuration.
  The environment should still function with reduced capability.
-->
When a tool is not available (permission denied, not installed, disabled):

- **Bash tool blocked**: Note which command was blocked. Suggest the user run it manually or update permissions in settings.json.
- **WebSearch/WebFetch blocked**: Skip web research. Note that results are based only on local context and codebase. Suggest the user fetch the information manually.
- **MCP tool unavailable**: Skip the MCP operation. Note which server/tool was unavailable and suggest checking `.mcp.json` configuration.
- **Write/Edit blocked on a path**: Report the specific path that was blocked. Suggest updating the `permissions.allow` list in `.claude/settings.json`.

Pattern: "[tool] is unavailable for [operation]. Skipping [step]. To enable: [specific fix]."

## State corruption

<!-- STATE CORRUPTION
  WHY: Agent-managed state files (JSON, Markdown) can become corrupted through
  partial writes, merge conflicts, or model errors. The recovery action depends
  on the file type.
-->
When a state file is corrupted (malformed JSON, inconsistent structure):

- **SESSION_SNAPSHOT.json**: Delete the corrupted file. Create a fresh snapshot from current state. Inform the user that previous session state was lost.
- **Docs/index.md**: Regenerate the index by scanning the Docs/ wiki directory. List all found files with basic metadata.
- **Docs/_working/retro/INDEX.md**: Regenerate by scanning Docs/_working/retro/ monthly files.
- **Docs/_working/retro/YYYY-MM.md**: If the monthly log is corrupted, rename it to `.corrupted` and start a fresh file. Do not discard the corrupted file (user may want to recover entries).
- **settings.json or settings.local.json**: Do NOT modify. Report the corruption and ask the user to fix it manually (settings control permissions and safety).

General rule: For files Claude manages, regenerate from directory contents.
For files the user manages, report and ask.

## VCS not configured

<!-- VCS NOT CONFIGURED
  WHY: Not every project uses VCS. State-save and other skills reference VCS
  state. When VCS is not available, those operations should be skipped cleanly.
-->
When git (or other VCS) is not configured or not available:

- Skip VCS state capture in `/state-save` (tool state section)
- Note in the state file: `"vcs": "not configured"`
- Do not attempt git commands
- Do not warn repeatedly about missing VCS (note it once per session)
- All other state categories (task, artifact, decision, blocked, drift) still function normally

## Permission denied

<!-- PERMISSION DENIED
  WHY: Permission errors are the most common friction in new environments.
  A specific, actionable suggestion reduces user frustration.
-->
When a permission is denied for a tool or operation:

1. Report which specific permission is missing
2. Suggest the exact settings.json addition to fix it
3. Example: "Permission denied for `Bash(npm test)`. Add `\"Bash(npm test)\"` to `permissions.allow` in `.claude/settings.json`."
4. Log as FRICTION in the retro log (this feeds into /update for permission improvements)

Do not:
- Attempt workarounds to bypass permissions
- Retry the same blocked operation
- Use alternative tools to circumvent the restriction

## Build or test failure

<!-- DOMAIN-SPECIFIC FAILURE
  WHY: Build/test failures are the most common domain-specific error.
  The response should be diagnostic, not retry-oriented.
-->
When a build or test command fails:

1. Read the error output carefully (do not skim)
2. Identify the root cause (not just the symptom)
3. If the fix is clear and within scope: apply it and re-run
4. If the fix is unclear: report the error with relevant log lines and ask for guidance
5. Never suppress errors or skip failing tests to make the build pass

## Diagnostic discipline

<!-- DIAGNOSTIC DISCIPLINE
  WHY: LLMs anchor on the first plausible diagnosis and keep drilling deeper
  into it even when evidence contradicts it. Users then waste time manually
  redirecting. This section forces multi-hypothesis reasoning and pivot triggers.
  Include in any environment where troubleshooting or debugging is expected
  (software dev, game dev, IT ops, devops, data). May be omitted for pure
  knowledge-work environments with no technical debugging.
-->
When diagnosing errors or unexpected behavior:

1. **Multi-hypothesis start**: List 2-3 possible causes before committing to one.
   State your working theory: "I believe this is caused by X because Y."
2. **Pivot trigger**: If your approach fails twice, stop. Assume the initial
   diagnosis is wrong. Re-examine the symptoms and consider alternative causes --
   especially in adjacent systems (e.g., a Graph SDK issue vs an Exchange issue,
   a module version vs an API change, a permission problem vs a code bug).
3. **Broaden before deepening**: Do not keep drilling into a failing theory.
   Step back, list what you have ruled out, and explore the next hypothesis.
4. **State assumptions explicitly**: When proposing a fix, say what you are
   assuming so the user can challenge it early rather than reverse-engineering
   your reasoning.

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Build/test failure handling
  - Git-specific VCS recovery
  - Permission suggestions reference npm, git, test tools

  KNOWLEDGE WORK:
  - Fewer tool-specific failures (minimal Bash use)
  - File-based failures more common (document not found, wrong format)
  - Add: "Source document unavailable: note the gap, do not fabricate content"

  GAME DEVELOPMENT:
  - Build failures with UE error output (can be very verbose -- extract key errors)
  - Binary asset errors: "Cannot edit .uasset -- write editor steps instead"
  - Perforce-specific VCS errors (p4 not logged in, workspace not configured)
  - Add: "Editor crash: suggest the user restart the editor and verify the change"

  DATA ENGINEERING:
  - Database connection failures
  - Pipeline failures with job IDs and log locations
  - Permission denied on data sources
  - Add: "Data source unavailable: skip, note the gap, do not fabricate data"

  DIAGNOSTIC DISCIPLINE APPLICABILITY:
  - Include for: Software Dev, Game Dev, DevOps, Data Engineering, IT Ops
  - Omit for: Pure Knowledge Work with no technical debugging
  - The adjacent-system examples should be domain-specific:
    - Software: dependency version vs code bug vs env config
    - Game Dev: engine API vs plugin vs asset pipeline vs editor config
    - DevOps: service vs permissions vs network vs DNS vs certificate
    - Data: query logic vs schema vs permissions vs connection vs data quality
    - IT Ops: service vs module version vs API change vs permissions
-->

<!-- ANTI-PATTERNS

  1. INFINITE RETRY LOOPS
     Problem: Tool fails, retry, fails again, retry... consumes context and time.
     Fix: Max 1 retry. Then fallback or ask user.

  2. SILENT FAILURE
     Problem: Agent fails, orchestrator continues as if nothing happened.
     Fix: Always log and report failures. User must know what was skipped.

  3. PANIC ON MISSING FILES
     Problem: INDEX.md missing -> error -> stop all work.
     Fix: Create with sensible defaults. Most missing files can be regenerated.

  4. MODIFYING SETTINGS ON PERMISSION ERROR
     Problem: Claude edits settings.json to grant itself more permissions.
     Fix: Report the needed permission, let the USER decide whether to grant it.

  5. WORKAROUNDS FOR BLOCKED TOOLS
     Problem: Bash blocked? Use a different tool to execute the same command.
     Fix: Respect permission boundaries. Report and suggest, do not circumvent.

  6. SUPPRESSING BUILD ERRORS
     Problem: Tests fail, Claude skips them or marks them as expected failures.
     Fix: "Never suppress errors or skip failing tests to make the build pass."

  7. DIAGNOSTIC ANCHORING
     Problem: First diagnosis looks plausible, keep drilling deeper into it even
     when evidence contradicts it. User has to manually redirect multiple times.
     Fix: List 2-3 hypotheses upfront. Pivot after 2 failures. Broaden before
     deepening. State assumptions explicitly so the user can challenge them.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 120 lines in generated output
  [ ] All 6 failure types covered (agent, file, tool, state, VCS, permission)
  [ ] Each failure type has a specific recovery action (not just "handle gracefully")
  [ ] "Never retry more than once" rule present
  [ ] Missing file table with recovery actions per file type
  [ ] Permission denied includes example settings.json fix
  [ ] VCS not configured degrades cleanly (skip, note, continue)
  [ ] State corruption handles both Claude-managed and user-managed files differently
  [ ] Domain-specific failure type included (build/test for software, etc.)
  [ ] Diagnostic discipline section included (for environments with debugging/troubleshooting)
  [ ] No silent failures -- all errors logged or reported
  [ ] ASCII-only
-->

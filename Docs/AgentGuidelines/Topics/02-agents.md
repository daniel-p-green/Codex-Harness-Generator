# 2. Agents

## 2.1 Delegation Framework (5 Elements)

- **Established**: 2025-09
- **Source**: multi-agent-research-system.md | Tier 1
- **Recommendation**: Every subagent delegation MUST include five elements:
  1. **Objective**: Clear, specific goal ("Find all authentication-related files and summarize
     the token refresh flow")
  2. **Output format**: Expected structure of results ("Return a markdown document with
     sections: Files Found, Flow Description, Integration Points")
  3. **Tool/source guidance**: Which tools to use and how ("Use Grep for pattern matching,
     Read for file content. Do not use Write or Edit.")
  4. **Task boundaries**: What is and is not in scope ("Only examine the auth/ directory.
     Do not modify any files. Report what you find without attempting fixes.")
  5. **Verification criteria**: How to confirm the work is correct ("Run pytest and confirm
     all tests pass. Verify the new endpoint returns 200 with valid auth token.")

  Verification criteria is the single highest-leverage element. Claude performs dramatically
  better when it can verify its own work -- run tests, compare outputs, validate results.
  Without verification criteria, agents frequently declare success without confirming it.
- **Anti-pattern**: Vague instructions like "research the authentication system." This causes
  agents to diverge, duplicate work, or explore irrelevant areas. In testing, vague
  delegation to research agents caused one to explore a 2021 crisis while two others
  duplicated 2025 investigations.

## 2.2 Model Selection Table

- **Established**: 2025-09
- **Source**: multi-agent-research-system.md, platform-agent-patterns.md, opus-4-6-guide.md | Tier 1
- **Recommendation**:

  | Agent Role | Model | Rationale | Typical maxTurns |
  |-----------|-------|-----------|------------------|
  | Orchestrator/Lead | opus | Complex reasoning, routing decisions | N/A (main thread) |
  | Planner | opus | Architectural reasoning, multi-step planning | 40 |
  | Debugger (complex) | opus | Multi-hypothesis investigation, deep reasoning | 40 |
  | Implementer | sonnet | Near-Opus coding quality, speed advantage compounds | 50 |
  | Reviewer | opus | Cross-model review catches implementer blind spots | 20 |
  | Validator | sonnet | Checklist-driven, speed advantage | 30 |
  | Explorer | sonnet | Fast scanning, more capable than haiku | 30 |
  | Quick lookups | haiku | Simple fact retrieval only | 15 |

  The Opus lead + Sonnet workers composition showed 90% improvement over single-agent
  Claude Opus in Anthropic's internal research eval.
- **Anti-pattern**: Using Opus for all agents. Sonnet 4.6 handles implementation,
  validation, and exploration at near-Opus quality with significant speed and cost
  advantages. Reserve Opus for orchestration, planning, and complex debugging where
  deep novel reasoning is required. Conversely, Haiku should only be used for the
  simplest lookups -- Sonnet 4.6 is fast enough to replace Haiku in most roles.

  Sonnet 4.6 update (Feb 2026): Sonnet 4.6 scores within 1.2% of Opus 4.6 on
  SWE-bench Verified (79.6% vs 80.8%) at 5x lower cost, with significant speed
  advantages that compound across agentic workflows. Default to Sonnet for tasks
  following established patterns (implementation, validation, exploration).
  Reserve Opus for tasks requiring deep reasoning (orchestration, planning,
  complex debugging, review). Developers preferred Sonnet 4.6 over the previous Opus 4.5
  59% of the time. Explorer upgrades from Haiku to Sonnet because Sonnet 4.6 is
  fast enough and substantially more capable.
  Cross-model diversity: pairing Sonnet implementation with Opus review creates
  genuine cognitive diversity -- each model has different blind spots, so the
  reviewer catches issues the implementer's model would consistently miss.

  `opusplan` alias (Mar 2026): The `opusplan` model alias automates the hybrid
  approach -- uses Opus during plan mode for architecture/reasoning, then switches
  to Sonnet for execution. This codifies the recommended Opus-plan + Sonnet-execute
  pattern without manual model switching. Recommend `opusplan` as the default for
  generated environments targeting complex projects.

  Subagent model override: `CLAUDE_CODE_SUBAGENT_MODEL` env var controls the model
  used for all subagent invocations. Useful for pinning subagents to Sonnet while
  the main thread uses Opus. For generated environments, set this in settings.json
  env block when explicit subagent model control is needed.

## 2.3 maxTurns Enforcement

- **Established**: Baseline
- **Source**: parallel-claudes-c-compiler.md, claude-code-docs.md | Tier 1
- **Recommendation**: Every agent definition MUST include maxTurns. Without it, agents can
  run indefinitely. Recommended ranges:
  - Explorer/lookup: 15-30
  - Reviewer/validator: 20-30
  - Implementer: 40-50
  - Planner/researcher: 30-40
  - Complex debugger: 40-50
- **Anti-pattern**: Omitting maxTurns. In the C compiler project (~2,000 sessions), agents
  without time constraints ran tests indefinitely. The `--fast` test flag was invented
  specifically to mitigate agent time-blindness.

## 2.4 disallowedTools

- **Established**: Baseline
- **Source**: claude-code-docs.md, platform-agent-patterns.md | Tier 1
- **Recommendation**: Restrict agent tools to enforce separation of concerns:
  - Reviewer: `disallowedTools: [Write, Edit]` (read-only analysis)
  - Explorer: `disallowedTools: [Write, Edit]` (read-only discovery)
  - Validator: `disallowedTools: [Edit]` (can write reports but not modify code)
  - Implementer: full tool access

  Use the `tools` field to whitelist, or `disallowedTools` to blacklist. Whitelisting is
  safer for restricted agents; blacklisting is easier for agents needing most tools.
- **Anti-pattern**: Giving all agents full tool access. A reviewer with Write access may
  "fix" issues it finds instead of just reporting them, conflating review and implementation.

## 2.5 Subagent Delegation Guidance (4.6 vs 4.7 behaviors)

- **Established**: 2025-09 (Opus 4.6); updated 2026-04-20 for Opus 4.7
- **Source**: platform-agent-patterns.md, opus-4-6-guide.md,
  platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | Tier 1
- **Recommendation**: Write subagent guidance that works for both models:
  - Use subagents when: tasks can run in parallel, require isolated context, involve
    independent workstreams, or require specialized model selection.
  - Work directly for: simple tasks, sequential operations, single-file edits, or tasks
    needing shared context.
  - Dial back aggressive tool-triggering language. Replace "CRITICAL: You MUST use this
    tool" with "Use this tool when..." -- both models perform better with measured phrasing.

  **Opus 4.6 bias**: Strong predilection for spawning subagents. Needs explicit brakes
  (the "work directly for" list above).

  **Opus 4.7 bias**: Spawns fewer subagents by default, uses reasoning more, and makes
  fewer tool calls. If you WANT aggressive delegation on 4.7, state it explicitly: "When
  a task spans multiple independent files, prefer spawning subagents in parallel."
  Otherwise 4.7 may keep work in the main loop where 4.6 would have forked.
- **Anti-pattern**:
  - Letting 4.6 orchestrators spawn subagents for trivial tasks (burns tokens, ~4x chat).
  - Assuming 4.7 will parallelize automatically -- it's more conservative. Explicit
    delegation hints matter more on 4.7.

## 2.6 Orchestrator Context Discipline

- **Established**: 2026-02
- **Source**: production game project production environment, production compliance project production environment | Tier 2
- **Recommendation**: The orchestrator is a dispatcher, not a reader. It must consume as
  little context as possible. Enforce a strict whitelist of what the orchestrator may Read:

  **Orchestrator MAY Read (small, pre-summarized files):**
  - Docs/ wiki index files and overview pages (< 300 lines)
  - Docs/_working/ state and session files
  - .claude/ config and rules files
  - CLAUDE.md, settings files, project config

  **Orchestrator MUST DELEGATE reads of (large, raw source):**
  - Source code files (any language) -- delegate to explorer, debugger, or implementer
  - Config files > 100 lines -- delegate to explorer
  - Build output -- delegate to debugger
  - External documentation -- delegate to researcher

  **Disk-based subagent handoff** (keeps intermediate data out of orchestrator):
  1. Subagent A writes findings to `Docs/_working/sessions/<slug>.md`
  2. Orchestrator spawns Subagent B, telling it to READ that file as input
  3. Subagent B builds on A's output, writes its own results to disk
  4. Orchestrator reads only the final summary, not intermediate artifacts

  WHY: Every line read into the orchestrator's context stays until compaction.
  A single 500-line source file consumes as much context as 10 subagent round-trips.
  Subagent reads are free to the orchestrator -- they use separate context windows.
- **Anti-pattern**: Orchestrator reading source code directly. This is the #1 cause of
  premature context exhaustion in complex environments. Even "just checking one file"
  accumulates across a session.

## 2.7 Agent Memory Persistence

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: Agents support persistent memory via the `memory` frontmatter field:
  - `user` scope: stored at `~/.claude/agent-memory/<name>/`, persists across projects
  - `project` scope: stored at `.claude/agent-memory/<name>/`, shared with team via VCS
  - `local` scope: stored at `.claude/agent-memory-local/<name>/`, private per machine

  First 200 lines of MEMORY.md are loaded at startup. Read, Write, Edit tools are
  auto-enabled when memory is active. Use for agents that accumulate domain knowledge
  over time (researchers, reviewers with project-specific conventions).
- **Anti-pattern**: Not using agent memory for agents that repeatedly need the same context.
  Without memory, each invocation starts cold, repeating discovery work.

## 2.8 Agent File Format

- **Established**: Baseline; updated 2026-04-20 for Claude Code v2.1.73-v2.1.111
- **Source**: claude-code-docs.md, code.claude.com/docs/en/changelog | Tier 1
- **Recommendation**: Agent definitions are markdown files in `.claude/agents/`. Required
  frontmatter fields: `name`, `description`. Supported optional fields: `tools`,
  `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`,
  `hooks`, `memory`, `effort`, `initialPrompt`. The markdown body is the system prompt.

  April 2026 additions:
  - `model:` -- override model via frontmatter (v2.1.73/v2.1.74)
  - `effort:` -- set effort level when agent is invoked (v2.1.76/v2.1.84). Use `low` for
    bounded subagents; `xhigh` for agentic coding. Defaults to session effort.
  - `initialPrompt:` -- agent auto-submits a first turn (v2.1.83). Useful for agents that
    should immediately orient themselves (e.g., "read ARCHITECTURE.md, then wait").
  - `maxTurns:` and `disallowedTools:` in frontmatter -- both formally documented in
    frontmatter as of v2.1.98 (always supported but now canonical).

  The `description` field is critical -- Claude uses it to decide when to delegate. Write
  descriptions that specify WHEN to delegate, not just WHAT the agent does. Include trigger
  phrases that match how users or orchestrators describe the work.

  Location priority: CLI flag > `.claude/agents/` > `~/.claude/agents/` > Plugin agents.
- **Anti-pattern**: Vague descriptions like "Helps with code." This prevents Claude from
  routing correctly. Write specific triggers: "Reviews code changes for security
  vulnerabilities, performance regressions, and adherence to project conventions. Delegate
  when the user says 'review', 'check my code', or 'audit changes'."

---

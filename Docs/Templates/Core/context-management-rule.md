# Template: Context Management Rule (02-context-management.md)

<!-- TEMPLATE ANNOTATION
  This template defines how the generated environment manages context window
  pressure. Context exhaustion is the #1 operational constraint for Codex.
  This rule provides multi-signal tracking, proactive summarization, and
  auto-save triggers to prevent context-related failures.

  QUALITY CRITERIA:
  - Under 120 lines in generated output
  - Multi-signal tracking with specific thresholds
  - Two-stage approach (summarize at 70%, auto-save at 100%)
  - Compaction preservation hints (domain-specific)
  - Technique selection guidance
  - Single-feature-per-session guidance
  - Adaptive threshold note

  WHY THIS EXISTS:
  The context window holds the entire conversation: every message, file read,
  command output. A single debugging session can consume tens of thousands of
  tokens. Without proactive management, Codex hits the wall mid-task and loses
  critical context during auto-compaction.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application
============================================================ -->

# Context management

<!-- CORE PRINCIPLE
  WHY: This framing helps Codex understand context as a finite resource
  that requires active management, not something that just happens.
-->
Context is a finite resource. Monitor it actively and save state before it runs out.

## Pressure signals

<!-- MULTI-SIGNAL TRACKING
  WHY: No single signal reliably predicts context exhaustion. Turn count misses
  large file reads. File read count misses long conversations. Multiple signals
  together catch more cases.

  The thresholds below are starting defaults. The self-learning system adjusts
  them based on observed friction (sessions that ran out of context).
-->
Track these signals for context pressure:

| Signal | Warning threshold | Critical threshold |
|---|---|---|
| Turn count (messages exchanged) | 25 | 35 |
| Delegation count (subagent invocations) | 8 | 12 |
| File reads (distinct files read) | 12 | 18 |

When ANY signal reaches the warning threshold, proactively summarize and consider
whether to save state. When ANY signal reaches the critical threshold, save state
before continuing.

## Two-stage approach

<!-- TWO-STAGE
  WHY: The 70% stage prevents surprise context loss. The 100% stage ensures
  state is preserved before the session must end or compact.
-->

### Stage 1: Proactive summarize (warning threshold reached)

When a warning threshold is reached:
1. Summarize the current task state in 3-5 bullets
2. Note which files have been modified and why
3. Identify remaining work items
4. Consider using `/compact` with focus instructions if the task needs more room

Compact focus example: `/compact Preserve: modified files list, test results, current task status for the API pagination feature`

### Stage 2: Auto-save (critical threshold reached)

When a critical threshold is reached:
1. Run `/state-save` to capture full session state
2. Update `Docs/_working/state/SESSION_CONTEXT.md` with current progress
3. Inform the user: "Context is getting full. State has been saved. Consider `/clear` and `/state-load` to continue with fresh context."

Do not stop the current task early. Complete the current atomic unit of work
(finish the current file edit, complete the current test run), then save.

## Compaction preservation hints

<!-- COMPACTION HINTS
  WHY: When auto-compaction triggers at ~95% capacity, Codex summarizes the
  conversation. Without hints, critical domain-specific context may be lost.
  These hints tell the compaction process what to preserve.
-->
When compacting (automatic or manual), always preserve:

- Modified files: full list of paths changed in this session
- Task status: current goal, what is done, what remains
- Test results: which tests passed/failed and why
- Decisions: key choices made and their rationale
- Blocked items: anything waiting on user input or external process
- Active errors: unresolved issues being debugged

Safe to discard:
- Raw file contents that were read but not modified
- Verbose command output from successful operations
- Intermediate search results that led to the final answer
- Redundant messages restating already-captured information

## Tool result clearing

<!-- TOOL RESULT CLEARING
  WHY: "Once a tool has been called deep in the message history, why would the
  agent need to see the raw result again?" This is the safest form of compaction.
  Old tool results consume significant context with no ongoing value.
-->
Old tool results (file reads, command outputs) from earlier in the conversation
can be safely summarized during compaction. Only the most recent tool results
(last 3-5 operations) need to be preserved in full.

## Technique selection

<!-- TECHNIQUE SELECTION
  WHY: Different task types benefit from different context management techniques.
  Using the wrong technique wastes context or loses important information.
-->

| Task type | Best technique | Why |
|---|---|---|
| Back-and-forth debugging | Compaction with focus hints | Preserves debugging chain |
| Iterative development with milestones | Note-taking (write to Docs/_working/state/) | Clear checkpoints to resume from |
| Parallel exploration of alternatives | Multi-agent (subagents or teams) | Each alternative gets clean context |
| Long refactoring across many files | Single-feature-per-session + state-save | Prevents mid-refactor context loss |
| Quick lookup or simple fix | Direct (no special management) | Task finishes before context is a concern |

## Single-feature-per-session

<!-- SINGLE FEATURE
  WHY: "Incremental scope: single feature per session prevents context exhaustion."
  Mixing multiple unrelated features in one session guarantees context pressure.
-->
Prefer one feature or task per session. When a task is complete:
1. Save state with `/state-save`
2. Suggest `/clear` to the user
3. Start the next task in a fresh session with `/state-load`

Domain-specific granularity for this project:
- One API endpoint = one session
- One React component = one session
- One bug fix = one session (unless trivially small, then batch 2-3)
- One database migration = one session
- Cross-cutting refactor: split by module, one module per session

## Quick navigation

<!-- CODE LANDMARKS
  WHY: Full wiki pages are too heavy for quick "where is X" lookups.
  A lightweight landmarks file (~20-30 lines) provides instant orientation
  without consuming significant context.
-->
For quick codebase navigation, maintain a landmarks file (`Docs/landmarks.md` or
`Docs/Dev/landmarks.md`) listing the most important files and their purposes.
This is smaller than full wiki pages and can stay in context cheaply.

Landmarks are generated by `/map-codebase` or created manually. They complement
detailed wiki documentation with instant orientation.

## Adaptive thresholds

<!-- ADAPTIVE THRESHOLDS
  WHY: Fixed thresholds are wrong for every project. The self-learning system
  adjusts thresholds based on observed friction. Sessions that hit context limits
  trigger threshold reductions; sessions that save state unnecessarily early
  trigger threshold increases.
-->
These thresholds are starting defaults. The self-learning system (see
`03-self-learning.md`) adjusts them based on friction entries tagged
`CONTEXT_PRESSURE`. If sessions consistently hit critical thresholds,
the warning thresholds are reduced. If state-save triggers too early,
thresholds are increased.

## Context window management

Your context will be automatically compacted when it reaches capacity.
Do not stop tasks early to avoid compaction. Instead:
- Save progress to disk regularly (Docs/_working/state/)
- Trust that compaction preserves key decisions and file lists
- After compaction, re-read `Docs/_working/state/SESSION_CONTEXT.md` to restore critical context

## PreCompact auto-save

<!-- PRECOMPACT
  WHY: Auto-compaction triggers at ~95% without warning. A PreCompact hook
  is the only way to guarantee state is saved before compaction happens.
  This is a safety net for progress not yet written to disk.
-->
A PreCompact hook automatically saves session state before auto-compaction.
This is configured in .codex/config.toml (not in this rule file). The hook
appends current activity and modified files to SESSION_CONTEXT.md.

If the hook is not configured, manually save state when context pressure
signals reach warning thresholds. Do not rely on compaction preserving
everything -- save proactively.

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- EFFICIENCY TIER THRESHOLDS
  The component-generator should substitute these values based on the Token
  Optimization section in ARCHITECTURE.md. The efficiency tier determines how
  aggressively context is managed.

  COST-CONSCIOUS (compaction at 85%):
  | Signal | Warning | Critical |
  | Turn count | 20 | 30 |
  | Delegation count | 6 | 10 |
  | File reads | 10 | 15 |
  Rationale: Lower thresholds trigger earlier state-saves, preventing context
  waste. Combined with 85% compaction, this keeps sessions lean.

  BALANCED (compaction at 95% default):
  | Signal | Warning | Critical |
  | Turn count | 25 | 35 |
  | Delegation count | 8 | 12 |
  | File reads | 12 | 18 |
  Rationale: Standard defaults. Good balance between session length and safety.

  QUALITY-FIRST (compaction at 95% default):
  | Signal | Warning | Critical |
  | Turn count | 30 | 40 |
  | Delegation count | 10 | 15 |
  | File reads | 15 | 22 |
  Rationale: Higher thresholds allow longer exploration before triggering saves.
  Optimizes for thoroughness over token economy.

  The reference implementation above uses BALANCED defaults. When generating for
  a different tier, replace the threshold table values accordingly.
-->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Granularity: one endpoint, one component, one bug fix per session
  - Preservation: modified files, test results, active errors
  - Technique: note-taking for milestones, compaction for debugging

  KNOWLEDGE WORK:
  - Granularity: one research question, one document draft, one review
  - Preservation: sources found, citations, draft structure, key findings
  - Technique: note-taking (write research findings to Docs/Areas/)
  - Lower thresholds (research reads many documents)

  GAME DEVELOPMENT:
  - Granularity: one gameplay feature, one bug fix, one performance issue
  - Preservation: playtest results, build status, changed files, replication context
  - Higher delegation count threshold (build + playtest cycles)
  - PreCompact hook recommended (build+playtest sessions are long)
  - Status line monitoring for context health (turn count, activity)

  CONSERVATIVE DOMAINS:
  - Lower thresholds across all signals (prefer saving state early)
  - Preserve: all citations, source references, compliance notes
  - Never discard: decision rationale, approval history
-->

<!-- ANTI-PATTERNS

  1. NO CONTEXT MANAGEMENT
     Problem: Session hits wall mid-task. Auto-compaction loses critical context.
     Fix: Implement multi-signal tracking with proactive save triggers.

  2. SINGLE SIGNAL TRACKING
     Problem: Only tracking turn count. Misses sessions with few turns but many file reads.
     Fix: Track turns + delegations + file reads together.

  3. AGGRESSIVE COMPACTION
     Problem: Compacting too aggressively loses subtle but critical context.
     Fix: Preserve decision rationale and active errors. Only discard confirmed-safe items.

  4. NO DOMAIN-SPECIFIC GRANULARITY
     Problem: "One task per session" without defining what a task is for this domain.
     Fix: List concrete examples of session-sized work units.

  5. STOPPING TASKS EARLY
     Problem: Detecting context pressure and abandoning the task mid-edit.
     Fix: Complete the current atomic unit, THEN save state.

  6. FIXED THRESHOLDS FOREVER
     Problem: Thresholds wrong for this project's typical session patterns.
     Fix: Adaptive thresholds via self-learning.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 120 lines in generated output
  [ ] Multi-signal tracking with specific numbers for all 3 signals
  [ ] Two-stage approach (warning + critical)
  [ ] Compaction preservation hints with domain-specific items
  [ ] Safe-to-discard list present
  [ ] Tool result clearing guidance present
  [ ] Technique selection table with task types
  [ ] Single-feature-per-session with domain-specific examples
  [ ] Adaptive threshold note referencing self-learning
  [ ] Context window management paragraph (do not stop early)
  [ ] No contradictions with orchestrator rule
  [ ] PreCompact auto-save section present (or reference to hook config)
  [ ] ASCII-only
-->

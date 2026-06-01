# Template: Orchestrator Rule (00-orchestrator.md)

<!-- TEMPLATE ANNOTATION
  This template defines the orchestrator rule -- the routing and delegation hub
  for the generated environment. It governs how the main assistant classifies
  user intent, selects agents, and coordinates work.

  QUALITY CRITERIA:
  - Under 120 lines in generated output
  - Routing table is domain-specific (not generic)
  - Every route has a fallback chain
  - Complexity scaling defined (simple/standard/complex)
  - Delegation requirements explicit (objective, output format, tool guidance, boundaries)
  - Teams vs Subagents decision matrix included
  - Proactive vs conservative default set per domain

  WHY THIS EXISTS:
  Without explicit routing, Claude either does everything in one context (exhausting it)
  or delegates randomly. The orchestrator rule ensures intent is classified correctly,
  work is delegated to the right agent with the right instructions, and fallbacks
  prevent dead ends when routing is wrong.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application
============================================================ -->

# Orchestrator rule

<!-- CORE RESPONSIBILITY
  WHY: The orchestrator must stay lean. If it reads source code or implements features
  directly, context fills up and quality degrades on complex tasks.
-->
The orchestrator classifies intent, delegates work, and coordinates results.
It must NOT read source files directly or implement features in the main context.

## Routing table

<!-- ROUTING TABLE
  Every entry must be domain-specific, not generic.
  WHY: Generic routing ("code question -> researcher") produces poor results.
  Domain-specific entries ("API endpoint bug -> debugger checks route handler + middleware")
  give agents the context they need to start productively.

  STRUCTURE: Intent | Complexity | Route | Fallback
  Fallback chains prevent dead ends when the primary route is wrong or insufficient.
-->

| User intent | Complexity | Route | Fallback |
|---|---|---|---|
| API endpoint bug / 500 error | simple | debugger (check route handler, middleware, DB query) | explorer -> debugger |
| Frontend rendering issue | simple | debugger (check component, state, API response) | explorer -> debugger |
| Database query performance | standard | explorer (identify query) -> implementer (optimize) | researcher (PostgreSQL docs) |
| New API endpoint | standard | planner (design endpoint + tests) -> implementer -> reviewer | explorer (find similar endpoints first) |
| New React component | standard | planner -> implementer -> reviewer | explorer (find component patterns) |
| Schema migration | complex | planner (migration + model + API updates) -> implementer -> reviewer | researcher (Alembic docs) |
| Full feature (backend + frontend) | complex | planner -> implementer (backend) -> implementer (frontend) -> reviewer | intake (if unclear) |
| Refactor / cleanup | standard | planner -> implementer -> reviewer | explorer (assess scope first) |
| "Where is X" / find code | simple | explorer | (direct grep/glob if explorer unavailable) |
| "How does X work" | simple | explorer (read code, summarize) | researcher (if concept question) |
| Code review request | standard | reviewer | (direct review if small diff) |
| Test failure / CI broken | simple | debugger (read test output, trace failure) | explorer -> debugger |
| Ambiguous / vague request | -- | Ask a clarifying question before routing | explorer (gather facts) |

<!-- COMPLEXITY SCALING
  WHY: Simple tasks should not spawn multiple agents (wasteful).
  Complex tasks need coordination to avoid context exhaustion.
-->
## Complexity scaling

| Level | Description | Agent pattern | Typical turns |
|---|---|---|---|
| Simple | Single file change, clear fix, quick lookup | 1 agent, direct response | < 5 |
| Standard | Multi-file change, clear requirements | 2-3 agents, sequential | 10-15 each |
| Complex | Cross-cutting feature, unclear scope | 3-5 agents, may need planning first | 15-30 each |

Rule: When unsure, start at standard. Downgrade to simple if the agent finishes quickly.
Upgrade to complex only when standard proves insufficient.

<!-- PROACTIVE VS CONSERVATIVE DEFAULT
  WHY: Different domains need different defaults. Engineering benefits from proactive
  action (fix the bug, don't ask). Legal/medical needs conservative (always confirm).
-->
## Action default: proactive

For this environment, default to acting rather than asking when:
- The action is local and reversible (file edits, test runs, searches)
- The intent is clear from context
- No destructive operations are involved

Ask before acting when:
- The user's intent is genuinely ambiguous (not just under-specified)
- The action is destructive or externally visible
- Multiple valid approaches exist with significant trade-offs

<!-- AMBIGUITY RESOLUTION
  WHY: Prevents the orchestrator from guessing wrong and wasting agent turns.
-->
## Ambiguity resolution

When user intent is unclear:
1. Prefer investigating over asking (use explorer to gather facts)
2. If investigation does not resolve ambiguity, ask ONE targeted question
3. Never ask more than two clarifying questions before starting work
4. If the request maps to multiple routes, pick the most likely and note the assumption

## Routing audit

When the user corrects a routing decision, log a CORRECTION entry:
```
[ROUTING_CORRECTION] Routed "fix the slow dashboard" to debugger, user meant frontend perf optimization -> should route to explorer (profiling) first
```
These corrections feed into `/update` for routing table improvements.

<!-- DELEGATION REQUIREMENTS
  WHY: Agents without clear objectives waste turns exploring randomly.
  Every delegation must include what to do, what to produce, what tools to use,
  what is out of scope, and how to verify success. Verification criteria is the
  single highest-leverage element -- agents perform dramatically better when they
  can confirm their own work.
-->
## Delegation format

Every delegation to an agent must include:

1. **Objective**: What specific outcome is expected (one sentence)
2. **Output format**: What artifact to produce and where to write it
3. **Tool guidance**: Which tools are relevant, which files to start with
4. **Boundaries**: What is out of scope, what NOT to change
5. **Verification**: How to confirm the work is correct (tests to run, outputs to check)

Example delegation:
```
Objective: Find the root cause of the 500 error on GET /api/customers when date_from > date_to
Output: Write findings to Docs/_working/state/SESSION_CONTEXT.md including root cause, affected files, and proposed fix
Tools: Read the route handler in src/api/customers.py, check the query builder, read recent test failures
Boundaries: Do not modify any files. Do not investigate unrelated endpoints.
Verification: Reproduce the error with a curl command, confirm the fix resolves it, run pytest tests/api/test_customers.py
```

<!-- DELEGATE MODE
  WHY: For complex multi-agent coordination, the orchestrator should coordinate
  rather than implement. Delegate mode enforces this by restricting tools.
-->
## Delegate mode

For complex tasks (3+ agents), consider switching to delegate mode:
- Restricts the orchestrator to coordination-only tools (no file edits)
- Forces all implementation through agents
- Enable with Shift+Tab when agent team is active

<!-- CONTEXT DISCIPLINE
  WHY: The orchestrator's context is the most precious resource. Every file read
  into it stays until compaction. Source code files (200-1000+ lines) consume
  context that could serve 10+ subagent delegations. Strict discipline here is
  the single most impactful optimization for complex environments.
-->
## Context discipline

The orchestrator MUST NOT read source code files directly.

**May read (small, pre-summarized):**
- Docs/ wiki pages (< 300 lines)
- Docs/_working/ state files
- .claude/ config and rules
- CLAUDE.md and project config files

**Must delegate reads of:**
- Source code (any language) -- to explorer, debugger, or implementer
- Config files > 100 lines -- to explorer
- Build output -- to debugger
- External docs -- to researcher

**Subagent handoff pattern** (keeps intermediate data out of orchestrator):
1. Subagent A writes findings to Docs/_working/sessions/
2. Orchestrator spawns Subagent B pointing at A's output file
3. Orchestrator reads only the final summary

<!-- TEAMS VS SUBAGENTS
  WHY: Agent Teams cost ~15x chat. Use them only when parallelism provides real benefit.
  Sequential subagents (Task tool) are cheaper and simpler for serial work.
-->
## Teams vs subagents

| Use Teams when | Use Subagents when |
|---|---|
| 2+ independent areas need parallel work | Work is naturally sequential |
| Competing hypotheses during debugging | Single focused task with one owner |
| Large feature with non-overlapping files | Low complexity or routine operations |
| Backend + frontend + tests in parallel | Plan -> implement -> review pipeline |

Default to subagents unless the task clearly benefits from parallelism.
Teams cost approximately 15x a normal chat interaction.

<!-- ARTIFACT-FIRST HANDOFF
  WHY: If agents return large outputs in chat, context fills up.
  Writing to disk and returning summaries keeps the orchestrator lean.
-->
## Artifact-first handoff

Every delegated job must produce a durable artifact:
- Explorer: findings written to Docs/Areas/ or Docs/_working/state/
- Planner: task plan written to Docs/_working/state/
- Implementer: code changes + summary in Docs/_working/state/SESSION_CONTEXT.md
- Reviewer: review report written to Docs/_working/state/
- Debugger: diagnosis written to Docs/_working/state/

The orchestrator returns: short summary + artifact paths + next action.

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Proactive action default
  - Technical routing entries (endpoint bug, schema migration, etc.)
  - Agents: researcher, planner, implementer, reviewer, explorer, debugger

  KNOWLEDGE WORK:
  - Conservative action default
  - Routing: research -> researcher, draft -> drafter, review -> reviewer
  - Simpler routing table (fewer intent categories)
  - Plain language in delegation format

  GAME DEVELOPMENT:
  - Proactive with playtest gates
  - Routes for gameplay bugs, performance, binary assets
  - Include performance-analyst agent in routes
  - Include manual playtest gate after implementation
  - Context discipline: whitelist Docs/ reads, delegate all Source/ reads
  - Disk-based subagent handoff for multi-step investigations

  CONSERVATIVE DOMAINS (medical, legal):
  - Conservative action default
  - Always-ask entries for anything involving external data
  - Citation verification required for research outputs
  - Human review gates at every decision point
-->

<!-- ANTI-PATTERNS

  1. GENERIC ROUTING TABLE
     Problem: "Bug -> debugger" without domain context. Agent does not know where to start.
     Fix: "API endpoint bug -> debugger (check route handler, middleware, DB query)"

  2. NO FALLBACK CHAINS
     Problem: Primary route fails, no recovery path. Work stalls.
     Fix: Every route has a fallback. "explorer -> debugger" if debugger alone is insufficient.

  3. ORCHESTRATOR READS CODE
     Problem: Main context fills up with file contents. No room for coordination.
     A single 500-line file consumes as much context as 10 subagent round-trips.
     Fix: Enforce a strict whitelist of what the orchestrator may Read. Delegate
     all source code reading to subagents. Use disk-based handoff between subagents
     to keep intermediate data out of the orchestrator's context entirely.

  4. VAGUE DELEGATIONS
     Problem: "Fix the bug" sent to debugger. Agent wanders aimlessly.
     Fix: Include objective, output format, tool guidance, boundaries, and verification criteria.

  5. ALWAYS USING TEAMS
     Problem: 15x cost for work that could be sequential.
     Fix: Default to subagents. Use teams only for genuinely parallel work.

  6. NO ROUTING AUDIT
     Problem: Routing mistakes repeat forever.
     Fix: Log CORRECTION entries. Feed them into /update for systematic improvement.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 120 lines in generated output
  [ ] Routing table has domain-specific entries (not generic)
  [ ] Every route has a fallback chain
  [ ] Complexity scaling table present (simple/standard/complex)
  [ ] Proactive vs conservative default explicitly set
  [ ] Ambiguity resolution rules present
  [ ] Routing audit (CORRECTION logging) included
  [ ] Delegation format includes all 5 elements (objective, output, tools, boundaries, verification)
  [ ] Delegate mode mentioned
  [ ] Teams vs subagents matrix present
  [ ] Artifact-first handoff rules present
  [ ] Anti-overengineering note present (via CLAUDE.md reference or direct)
  [ ] All routing entries use domain vocabulary (not generic terms)
  [ ] Context discipline section present (what orchestrator may/must-not read)
  [ ] Subagent handoff pattern documented (disk-based, not through orchestrator)
-->

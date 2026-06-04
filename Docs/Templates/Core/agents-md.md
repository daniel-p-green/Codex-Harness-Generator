# Template: Generated AGENTS.md

<!-- TEMPLATE ANNOTATION
  This template is an annotated reference implementation of a generated AGENTS.md file.
  The component-generator reads this as guidance and composes content adapted to the
  specific project's GENESIS.md and ARCHITECTURE.md.

  QUALITY CRITERIA:
  - Target: < 250 lines (every line must earn its place)
  - Keep total loaded project guidance under Codex's default project_doc_max_bytes cap
    of 32 KiB unless the user intentionally raises it
  - Every constraint includes WHY (intent-behind-rules)
  - No role-setting prompts ("Act as...", "You are a senior...")
  - 2-3 canonical behavior examples (few-shot)
  - Include/exclude rubric applied ruthlessly
  - Compaction preservation hints present
  - Verification patterns included
  - ASCII-only throughout

  INCLUDE/EXCLUDE RUBRIC:
  Include: commands Codex cannot guess, style rules differing from defaults,
  testing/verification instructions, architectural decisions, dev environment quirks,
  common gotchas, workflow constraints unique to this project
  Exclude: anything Codex can infer from code, standard language conventions,
  detailed API docs (link instead), frequently-changing info, self-evident practices

  WHY THIS STRUCTURE:
  GPT-5.5 follows instructions stated once without degradation. Front-load the most
  important constraints. Use few-shot examples instead of exhaustive rule lists.
  Keep it concise -- bloated AGENTS.md files cause Codex to IGNORE instructions.
  Codex can also load AGENTS.override.md and configured fallback files from
  project_doc_fallback_filenames, so generated root guidance should stay compact
  enough to compose with nested overrides.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION BEGINS
  Domain: Web application (FastAPI + React + PostgreSQL)
  Adapt vocabulary, constraints, and examples per GENESIS.md
============================================================ -->

# Project: Acme Dashboard

<!-- PURPOSE AND CONSTRAINTS
  State purpose directly. No role-setting. One paragraph maximum.
  Include the single most important constraint the project has.
  WHY: GPT-5.5 does not need "Act as..." prompts. Stating purpose once
  is sufficient -- the model maintains consistency across extended conversations.
-->
This is a FastAPI backend with a React frontend managing customer analytics dashboards.
The API serves financial data and must never expose raw PII in responses.

<!-- FIRST-RUN ONBOARDING
  Detect via INDEX.md marker. Show greeting only once.
  WHY: New users need orientation. Returning users need to resume work.
  The NEW_ENVIRONMENT marker is set during generation and cleared after first session.
-->
## First run

Check `Docs/index.md` for the `Status: NEW_ENVIRONMENT` marker. If present:
- Greet the user with a one-sentence summary of this environment
- List available commands: /state-save, /state-load, /update, /health-check
- Suggest first actions: "Try asking me to explore the codebase, or describe a feature to implement"
- Clear the marker after greeting

<!-- NON-NEGOTIABLE CONSTRAINTS
  3-7 hard rules that must never be violated.
  Each rule includes WHY in parentheses.
  WHY: These are the rules where violation causes real damage.
  Emphasis tuning: use IMPORTANT or NEVER for critical rules.
-->
## Non-negotiable constraints

- NEVER commit secrets, API keys, or .env files (leaked credentials cause security incidents)
- NEVER run destructive database operations without confirmation (data loss is irreversible)
- NEVER push to main/master directly (team uses PR workflow; direct pushes bypass review)
- Always run `pytest` before committing (CI will reject failing tests; catching locally saves time)
- PII fields must be masked in all API responses (regulatory compliance requirement)

<!-- AUTONOMY REFERENCE
  Brief summary pointing to the full rule file.
  WHY: Keeps AGENTS.md concise while ensuring autonomy boundaries are known.
-->
## Autonomy

See `.codex/rules/01-autonomy.md` for full boundaries. Summary:
- Local file reads/writes, searches, test runs: autonomous (just do it)
- Destructive operations, pushes, external service calls: ask first
- Do not overengineer. Only make changes directly requested or clearly necessary.

<!-- COMMAND REFERENCE
  List only generated skills. Keep descriptions to one line each.
  WHY: Users need to know what commands are available without reading skill files.
-->
## Commands

- `/state-save` -- Save current session progress before /clear or ending work
- `/state-load` -- Restore context at the start of a new session
- `/update` -- Review friction log and propose environment improvements
- `/health-check` -- Validate environment integrity and freshness

<!-- ORCHESTRATOR CONTRACT
  How the main assistant should behave. Delegation rules.
  WHY: Without this, Codex tries to do everything in one context, leading to
  context exhaustion on complex tasks. Delegation keeps context lean.
-->
## Orchestrator contract

Keep context lean. Delegate complex work to agents.

- Route by intent using `.codex/rules/00-orchestrator.md`
- Write durable output to disk, return short summaries
- Never read source files directly to answer questions -- delegate to explorer or implementer
- After meaningful progress, update `Docs/_working/state/SESSION_CONTEXT.md`

Anti-overengineering: Only generate what was requested. Do not add extra agents, rules,
abstractions, or documentation "just in case." A smaller correct change is better than
a comprehensive one that introduces risk.

<!-- CANONICAL BEHAVIOR EXAMPLES
  2-3 concrete few-shot examples showing expected behavior for THIS domain.
  WHY: "For an LLM, examples are the 'pictures' worth a thousand words."
  Few-shot examples beat exhaustive rule lists for pattern generalization.
-->
## Behavior examples

<example domain="bug-report">
User: "The /api/customers endpoint returns 500 when filtering by date range"

Expected behavior:
1. Delegate to debugger agent with the specific endpoint and error
2. Debugger reads the route handler, checks query parameter parsing, examines logs
3. Returns: root cause, proposed fix, affected files
4. Implement fix, run pytest, verify the endpoint works
5. Commit with descriptive message referencing the bug
</example>

<example domain="feature-request">
User: "Add a CSV export button to the analytics dashboard"

Expected behavior:
1. Delegate to explorer to understand current export patterns and dashboard structure
2. Delegate to planner for implementation plan (backend endpoint + frontend component)
3. Implement backend first (new endpoint, serialization), run tests
4. Implement frontend (button component, API call), verify in browser
5. Commit as single coherent change
</example>

<example domain="ambiguous-request">
User: "Make the dashboard faster"

Expected behavior:
1. Ask a clarifying question: "Which dashboard page feels slow? Are you seeing slow API responses, slow rendering, or slow initial page load?"
2. Based on answer, delegate to appropriate agent (debugger for API, explorer for frontend)
3. Do NOT immediately start optimizing random things
</example>

<!-- COMPACTION HINTS
  Tell Codex what to preserve when context is automatically compacted.
  WHY: Auto-compaction at ~95% capacity may discard critical context.
  These hints ensure the most important information survives compaction.
-->
## Compaction hints

When compacting, always preserve:
- The full list of modified files and their paths
- Current task status and remaining steps
- Any test commands and their pass/fail results
- Key decisions made and their rationale
- Database migration state if applicable

<!-- VERIFICATION PATTERNS
  Domain-specific commands that Codex should use to verify its work.
  WHY: Verification is the #1 highest-leverage intervention for agent quality.
  These commands let Codex self-check without relying on the user.
-->
## Verification

- Tests: `pytest tests/ -x --tb=short`
- Type checking: `mypy src/ --strict`
- Linting: `ruff check src/`
- API smoke test: `curl -s http://localhost:8000/health | jq .`
- Frontend: `npm run build` (catches TypeScript errors)

Run the appropriate verification after every code change.

<!-- SELF-IMPROVEMENT NOTE
  Signal that the environment learns from use.
  WHY: Sets expectations and encourages users to provide feedback.
-->
## Self-improvement

This environment improves with use. Friction, corrections, and wins are logged
in `Docs/_working/retro/`. Run `/update` periodically to review and apply improvements.

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  For different domains, adapt:

  SOFTWARE DEVELOPMENT (this example):
  - Verification = test suite, linter, type checker
  - Constraints = VCS workflow, CI gates
  - Examples = bug fix, feature, ambiguous

  KNOWLEDGE WORK (legal, research, analysis):
  - Verification = citation check, format compliance, word count
  - Constraints = confidentiality, source attribution, review gates
  - Examples = research task, document draft, review request
  - Use plain language throughout ("save your progress" not "/state-save")

  GAME DEVELOPMENT:
  - Verification = build command, manual playtest gate
  - Constraints = binary asset rules, replication safety, playtest requirements
  - Examples = gameplay feature, bug fix with repro, performance issue
  - Include binary asset handling rules

  DATA ENGINEERING:
  - Verification = data validation scripts, schema checks, dry-run queries
  - Constraints = never modify production data, always preview before write
  - Examples = pipeline bug, new transform, schema migration

  CONSERVATIVE DOMAINS (medical, legal, financial):
  - Default to asking before acting on external operations
  - Include citation/source verification in every example
  - Add disclaimer constraints
  - Keep autonomy boundaries tight
-->

<!-- ANTI-PATTERNS

  1. BLOATED AGENTS.MD (>250 lines)
     Problem: Codex ignores instructions buried in long files.
     Fix: Apply include/exclude rubric. Move reference material to rules or skills.

  2. ROLE-SETTING PROMPTS
     Problem: "Act as a senior engineer" wastes tokens, unnecessary with GPT-5.5.
     Fix: State purpose and constraints directly.

  3. REPEATING INSTRUCTIONS
     Problem: "Remember to always..." mid-file. GPT-5.5 follows instructions stated once.
     Fix: State each instruction exactly once, clearly.

  4. BARE RULES WITHOUT INTENT
     Problem: "Always use TypeScript strict mode" -- Codex may override if it seems unnecessary.
     Fix: "Always use TypeScript strict mode because our CI rejects non-strict files."

  5. GENERIC EXAMPLES
     Problem: Examples that could apply to any project do not help Codex understand THIS project.
     Fix: Use domain-specific examples with real endpoint names, real file paths, real commands.

  6. MISSING VERIFICATION
     Problem: No way for Codex to self-check. User becomes the only feedback loop.
     Fix: Always include domain-specific verification commands.

  7. KITCHEN-SINK FIRST-RUN
     Problem: Dumping every feature and capability on first greeting.
     Fix: 1 sentence + commands + 2-3 suggested actions. Let the user explore.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 250 lines
  [ ] No role-setting prompts ("Act as...", "You are a...")
  [ ] Every constraint includes WHY
  [ ] 2-3 canonical behavior examples (domain-specific)
  [ ] Compaction hints present with domain-specific items
  [ ] Verification commands present and runnable
  [ ] First-run onboarding section with index.md marker check
  [ ] Non-negotiable constraints are genuinely non-negotiable
  [ ] Autonomy section references rule file (not duplicated)
  [ ] Command reference lists all generated skills
  [ ] Orchestrator contract includes anti-overengineering
  [ ] Self-improvement note present
  [ ] ASCII-only
  [ ] No instructions that Codex would follow by default anyway
  [ ] For each line: "Would removing this cause Codex to make mistakes?" -- if no, cut it
-->

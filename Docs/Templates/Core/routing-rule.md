# Template: Routing Rule Configuration

<!-- TEMPLATE ANNOTATION
  This template provides detailed routing configuration that supplements the
  orchestrator rule. While the orchestrator rule defines the high-level routing
  table, this rule defines the structure, format, and decision logic for
  domain-specific routing entries.

  The orchestrator-rule.md and routing-rule.md may be combined into a single file
  for simpler environments, or kept separate for complex ones with many routes.

  QUALITY CRITERIA:
  - Domain-specific entry format with concrete examples
  - Fallback chain structure clearly defined
  - Complexity scaling with agent count and turn budgets
  - Conditional workflow branching with explicit decision points
  - Under 120 lines in generated output

  WHY THIS EXISTS:
  The routing table is the most-consulted section of the orchestrator rule.
  Getting routing wrong wastes agent turns and frustrates users. This rule
  provides the structure to make routing decisions consistent and auditable.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application
============================================================ -->

# Routing configuration

## Entry format

<!-- DOMAIN-SPECIFIC ENTRY FORMAT
  WHY: Each routing entry needs enough context for the orchestrator to make
  the right decision quickly. Generic entries ("bug -> debugger") force the
  orchestrator to spend turns figuring out where to start.
-->
Every routing entry follows this structure:

```
Intent signal: [keywords and phrases that trigger this route]
Complexity: simple | standard | complex
Primary route: [agent] ([starting context: which files/areas to check first])
Fallback chain: [agent1] -> [agent2] -> [ask user]
Preconditions: [what must be true for this route to apply]
Output: [expected artifact from the agent]
```

## Domain routing entries

<!-- DOMAIN ENTRIES
  These must be fully enumerated for the specific domain.
  WHY: Untested routes fail silently. Every entry should map to a real
  user intent that has been observed or anticipated for this domain.
-->

### Bug and error resolution

```
Intent: API returns error, endpoint broken, 500/400 status, "doesn't work", stack trace
Complexity: simple (single endpoint) | standard (cross-service)
Primary: debugger (start with route handler, check middleware chain, examine DB queries)
Fallback: explorer (find related code) -> debugger (with broader context)
Preconditions: User provides endpoint, error message, or reproduction steps
Output: Root cause analysis + proposed fix in Docs/_working/state/SESSION_CONTEXT.md
```

```
Intent: Frontend crash, component error, rendering issue, blank page, console error
Complexity: simple (single component) | standard (state management issue)
Primary: debugger (check component, props, state, API response shape)
Fallback: explorer (find component tree) -> debugger
Preconditions: User provides page/component or error message
Output: Root cause + fix in Docs/_working/state/SESSION_CONTEXT.md
```

```
Intent: Test failure, CI broken, pytest error, test red
Complexity: simple
Primary: debugger (read test output, trace assertion failure, check recent changes)
Fallback: explorer (find related test files) -> debugger
Output: Fix applied, tests passing
```

### Feature implementation

```
Intent: Add endpoint, create API, new route, implement feature (backend)
Complexity: standard
Primary: planner (design endpoint, tests, migration if needed) -> implementer -> reviewer
Fallback: explorer (find similar endpoints for pattern reference)
Preconditions: Requirements clear enough to design a route signature
Output: Implemented code, passing tests, review report
```

```
Intent: Add component, create page, new UI, implement feature (frontend)
Complexity: standard
Primary: planner (design component, identify existing patterns) -> implementer -> reviewer
Fallback: explorer (find component patterns in codebase)
Output: Implemented component, build passes
```

```
Intent: Full feature (backend + frontend), new capability, user story
Complexity: complex
Primary: planner (full design) -> implementer (backend) -> implementer (frontend) -> reviewer
Fallback: intake (if requirements unclear) -> planner
Output: End-to-end feature, all tests passing, review complete
```

### Code quality

```
Intent: Refactor, clean up, simplify, reduce duplication, improve naming
Complexity: standard (scoped) | complex (cross-cutting)
Primary: planner (assess scope, identify files) -> implementer -> reviewer
Fallback: explorer (assess scope first if unclear)
Preconditions: Scope is clear or can be clarified from codebase
Output: Refactored code, all existing tests still passing
```

```
Intent: Review code, check quality, look for issues
Complexity: standard
Primary: reviewer (read changed files, check against project conventions)
Fallback: direct review if diff is small (< 5 files)
Output: Review report with findings categorized by severity
```

### Information and exploration

```
Intent: Where is X, find code, locate function, which file handles Y
Complexity: simple
Primary: explorer (search codebase, summarize findings)
Fallback: direct grep/glob if explorer unavailable
Output: File paths, relevant code locations, brief explanation
```

```
Intent: How does X work, explain architecture, what is the flow
Complexity: simple (specific) | standard (broad)
Primary: explorer (read relevant files, trace execution flow)
Fallback: researcher (if question is about external library or concept)
Output: Explanation written to Docs/Areas/ for future reference
```

### Database and schema

```
Intent: Schema migration, database change, add column, new table
Complexity: standard (single table) | complex (multi-table with data migration)
Primary: planner (design migration + model + API updates) -> implementer -> reviewer
Fallback: researcher (Alembic/SQLAlchemy docs if unfamiliar pattern)
Output: Migration file, updated models, passing tests
```

## Fallback chain structure

<!-- FALLBACK CHAINS
  WHY: Generated routing tables are untested. Fallbacks prevent dead ends.
  Each fallback step should provide additional context that helps the next step.
-->
Fallback chains follow this progression:
1. **Primary agent**: Most likely to resolve the intent
2. **Context-gathering fallback**: Explorer or researcher gathers missing context
3. **Broadened primary**: Retry primary agent with additional context from step 2
4. **User clarification**: Ask the user for more information (last resort)

Never skip directly to user clarification. Always attempt at least one investigation step.

## Conditional branching

<!-- CONDITIONAL WORKFLOW
  WHY: Some intents require different workflows depending on what the agent discovers.
  Explicit decision points prevent agents from committing to the wrong path.
-->
At these decision points, the orchestrator must branch:

- **After planner completes**: If plan touches > 10 files, escalate to complex (add review step).
  If plan touches 1-3 files, downgrade to simple (skip separate review).
- **After debugger returns**: If root cause is in infrastructure (not application code),
  route to researcher for documentation. If root cause is a code bug, route to implementer.
- **After explorer returns**: If the relevant code is well-structured, route to implementer.
  If the code is tangled or poorly documented, route to planner first.

## Proactive vs conservative defaults

| Action category | Default | Override trigger |
|---|---|---|
| File reads and searches | Proactive | Never ask |
| File edits in source code | Proactive | Ask if ambiguous intent |
| File edits in Docs/ | Proactive | Never ask |
| Running tests | Proactive | Never ask |
| Git commits | Ask | User says "commit" |
| Git push | Ask | User says "push" |
| Database operations | Ask | User provides explicit migration |
| External API calls | Ask | User provides credentials |

### Tutorial / Teaching Pattern

<!-- ANNOTATION: [Step-by-step guidance routing]
     WHY: Some users need the assistant to teach them how to do something, not just
     do it for them. This is different from a research query (which provides information)
     or an implementation request (which produces code/documents). Tutorial requests
     need a structured, patient, step-by-step walkthrough.
     ADAPT: The teaching target varies by domain:
     - Game dev: "Walk me through building this Blueprint"
     - Data analysis: "Show me how to build a pivot table"
     - Legal: "How do I structure this type of brief"
     - DevOps: "Walk me through setting up this Terraform module" -->

Detect these intent signals:
- "Teach me how to..."
- "Walk me through..."
- "Show me step by step..."
- "How do I [do X] myself?"
- "Explain the process for..."
- "Guide me through..."
- "I want to learn how to..."

Route: researcher (find the canonical process) -> orchestrator presents step-by-step

Key requirements for tutorial output:
- Numbered steps (not just a description)
- One action per step (do not combine multiple actions)
- Expected result after each step (so the user can verify)
- If the steps involve a GUI application (editor, IDE, design tool), include:
  exact menu paths, button names, keyboard shortcuts
- If the steps involve code, show small complete snippets (not fragments)
- Offer to explain any step in more detail if the user is confused

Fallback: If the topic is too complex for a single walkthrough, break it into
multiple sessions and suggest starting with the first part.

Example routing table entry:
| "Walk me through [X]" / "Teach me [X]" | researcher (find process) -> present step-by-step | Adapt detail level to user's experience from GENESIS.md | answer directly (if well-known simple process) |

### Dual-Mode File Processing Pattern

<!-- ANNOTATION: [Quick analysis vs formatted deliverable routing]
     WHY: File processing requests fall into distinct modes. A user asking "summarize
     this PDF" wants quick text output. A user asking "create a report from this data"
     wants a formatted deliverable. Routing both through the same pipeline wastes
     effort or produces wrong-format output. Splitting into modes lets the orchestrator
     pick the right tool chain on the first try.
     ADAPT: This pattern is only generated when the environment has both analysis and
     deliverable capabilities (typically Data & Analysis or Knowledge Work profiles
     with Pandoc). Environments with only MarkItDown (no Pandoc) use quick mode only.
     Environments with only Python data tools use data mode only. -->

Detect file processing requests and route to the appropriate mode:

#### Quick mode (analysis and extraction)

```
Intent: "summarize", "analyze", "what does this say", "key findings", "extract",
        "compare these files", "list the items in"
Complexity: simple
Process: MarkItDown inbound -> Codex processes -> text/Markdown output
Output: Direct text response or Markdown file in Outbox/
```

#### Quality mode (formatted deliverables)

```
Intent: "create a report", "draft a memo", "produce a brief", "make a presentation",
        "format this as", "export as .docx/.pptx/.pdf"
Complexity: moderate
Preconditions: Pandoc installed, OR python-docx available

Process:
1. Brand check (if Brand/ directory exists):
   a. Check Brand/brand-rules.md Source Tracking against Brand/Guidelines/ and Brand/Templates/
   b. If new or modified files detected: re-analyze brand assets, update brand-rules.md
   c. Load brand-rules.md for content and formatting guidance
2. MarkItDown inbound (if processing input files)
3. Codex drafts content in Markdown, applying brand rules:
   - Tone/voice from brand-rules.md
   - Required terminology
   - Required sections/headers/disclaimers
4. Pandoc converts with brand template:
   - .docx: pandoc output.md -o result.docx --reference-doc=Brand/Templates/<name>.docx
   - .pptx: pandoc slides.md -t pptx -o deck.pptx --reference-doc=Brand/Templates/<name>.pptx
   - If no brand template exists: Pandoc uses default styling
5. Output to Outbox/

Fallback: If Pandoc not installed, use python-docx (basic formatting, no brand template).
          If no Brand/ directory, skip steps 1 and brand-specific parts of step 3-4.
Output: Formatted file in Outbox/
```

#### Data mode (full-fidelity modification)

```
Intent: "update the spreadsheet", "fix the formulas", "add a column",
        "merge these Excel files", "clean this data"
Complexity: standard
Process: openpyxl/ImportExcel reads with full fidelity -> Codex modifies -> writes in original format -> Outbox/
Preconditions: Python + openpyxl or PowerShell + ImportExcel available
Fallback: If tools not available, describe changes and ask user to apply manually
Output: Modified data file in Outbox/
```

Mode selection decision tree:
1. Does the user want information FROM a file? -> Quick mode
2. Does the user want a formatted file BACK? -> Quality mode
3. Does the user want to MODIFY a data file preserving its format? -> Data mode
4. Ambiguous? Default to quick mode (lowest overhead, easiest to retry in another mode)

Brand guidance is automatically applied in quality mode when a Brand/ directory exists.
No separate brand mode is needed -- it enriches quality mode transparently.

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Technical routing with endpoint/component/migration categories
  - Proactive defaults for file operations
  - Git workflow branching

  KNOWLEDGE WORK:
  - Simpler categories: research, draft, review, organize, summarize
  - Conservative defaults (always ask before sending/publishing)
  - No git/build entries
  - Entries like: "Summarize document -> drafter", "Fact-check claim -> researcher"

  GAME DEVELOPMENT:
  - Categories include: gameplay bug, performance issue, asset request, network/replication
  - Playtest gate branching: after implementation, always pause for manual test
  - Binary asset routes: "If change requires .uasset editing -> write editor steps, STOP"
  - Performance routes: "FPS drop -> perf-analyst (profiling) -> implementer (optimization)"

  DATA ENGINEERING:
  - Categories: pipeline failure, schema change, data quality issue, new transform
  - Conservative defaults for production data operations
  - Branching: "If pipeline touches production -> require dry-run step"
-->

<!-- ANTI-PATTERNS

  1. GENERIC ENTRIES WITHOUT STARTING CONTEXT
     Problem: "Bug -> debugger" gives no starting point.
     Fix: Include which files/areas the agent should check first.

  2. MISSING FALLBACK ON EVERY ENTRY
     Problem: Agent fails, no recovery path.
     Fix: Every entry needs at least one fallback step.

  3. NO CONDITIONAL BRANCHING
     Problem: Complex workflows follow a fixed path regardless of what agents discover.
     Fix: Define explicit decision points with branching criteria.

  4. OVER-ROUTING SIMPLE TASKS
     Problem: "Fix typo" triggers planner -> implementer -> reviewer pipeline.
     Fix: Complexity scaling. Simple tasks get 1 agent, direct response.

  5. CONSERVATIVE DEFAULT ON EVERYTHING
     Problem: Codex asks permission for every file read. User gets frustrated.
     Fix: Set proactive defaults for reversible local operations.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 120 lines in generated output
  [ ] All entries are domain-specific (mention real file types, tools, areas)
  [ ] Every entry has a fallback chain (at least one fallback)
  [ ] Complexity scaling present with agent counts
  [ ] Conditional branching defined for key decision points
  [ ] Proactive/conservative defaults table present
  [ ] Entry format is consistent and parseable
  [ ] No generic entries like "bug -> debugger" without context
  [ ] Covers at least: bugs, features, exploration, code quality
  [ ] Fallback chain progression documented (primary -> context -> retry -> ask)
-->

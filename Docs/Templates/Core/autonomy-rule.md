# Template: Autonomy Rule (01-autonomy.md)

<!-- TEMPLATE ANNOTATION
  This template defines the act-vs-ask boundaries for the generated environment.
  It uses a reversibility/impact classification to determine when Codex should
  act autonomously versus when it should ask for confirmation.

  QUALITY CRITERIA:
  - Under 120 lines in generated output
  - Reversibility/impact classification with concrete examples
  - Domain-specific customization
  - Overengineering prevention prompt for GPT-5.5
  - Clear examples for each classification level

  WHY THIS EXISTS:
  Without explicit autonomy boundaries, Codex either asks permission for everything
  (frustrating) or acts on everything (dangerous). The reversibility framework gives
  Codex a simple heuristic: "Can I undo this easily? Then just do it."

  GPT-5.5 also has a known tendency to overengineer -- adding extra features,
  documentation, and abstractions beyond what was asked. The overengineering
  prevention section counteracts this directly.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application
============================================================ -->

# Autonomy boundaries

<!-- CORE PRINCIPLE
  WHY: This single sentence gives Codex the heuristic for any situation
  not explicitly covered by the classification table below.
-->
Act on local, reversible operations. Ask before hard-to-reverse or externally visible actions.

## Classification

<!-- REVERSIBILITY/IMPACT TABLE
  WHY: Concrete examples prevent ambiguity. Codex sees "edit a source file"
  and knows it is autonomous. Codex sees "git push" and knows to ask.
  Without examples, Codex must reason about reversibility each time.
-->

### Autonomous (just do it, report what you did)

These actions are local, reversible, and low-risk:

- Read any project file
- Edit source files, config files, documentation
- Create new files in the project
- Delete scratch/temporary files
- Run tests (`pytest`, `npm test`)
- Run linters and formatters (`ruff`, `mypy`, `prettier`)
- Run build commands (`npm run build`)
- Search the codebase (grep, glob, find)
- Use configured web or docs sources; ask the parent session before going outside the network allowlist
- Write to `Docs/` directory (wiki, working state, retro logs)
- Edit `.codex/` files (rules, agents, skills)
- Create git branches
- Stage files (`git add`)
- Make git commits (with descriptive messages)

### Ask first (confirm before proceeding)

These actions are hard to reverse, destructive, or visible to others:

- Push to remote (`git push`) -- changes become visible to the team
- Force push (`git push --force`) -- rewrites shared history
- Delete branches (`git branch -D`) -- may lose work
- Reset/discard changes (`git reset --hard`, `git checkout .`) -- loses uncommitted work
- Merge branches -- affects shared state
- Create or comment on PRs/issues -- visible to team
- Run database migrations on non-local databases -- schema changes are hard to reverse
- Install or upgrade global packages -- affects system state
- Modify CI/CD configuration -- affects entire team workflow
- Send messages or notifications -- cannot unsend
- Access external APIs with write permissions -- external side effects

### Never do autonomously

- Delete production data
- Expose secrets or credentials in code or output
- Bypass safety checks (`--no-verify`, `--force`, `--skip-tests`)
- Run `rm -rf` on directories outside the project
- Modify system files outside the project directory
- Push to main/master without explicit user request

## Domain-specific rules

<!-- DOMAIN CUSTOMIZATION
  WHY: Different projects have different risk profiles. A solo developer's personal
  project has different boundaries than a team working on financial software.
  These rules supplement the general classification above.
-->

- Database operations: Always preview the SQL before executing. Use `--dry-run` flags when available.
- API endpoints: When adding new endpoints, follow existing patterns. Do not create novel conventions.
- Test data: Creating test fixtures is autonomous. Modifying shared test data requires confirmation.
- Environment files: Never read, create, or modify `.env` files. Ask the user to handle secrets directly.

## Overengineering prevention

<!-- OVERENGINEERING PREVENTION
  WHY: GPT-5.5 is known to overengineer -- adding features, abstractions, and
  documentation beyond what was requested. This section directly counteracts
  that tendency with explicit instructions.

  Evidence: https://developers.openai.com/codex/subagents and guardrails.md both document this behavior.
  The prompt text below is adapted from OpenAI's recommended guardrails.
-->
Avoid over-engineering. Only make changes directly requested or clearly necessary.
Keep solutions simple and focused:

- **Scope**: Do not add features beyond what was asked
- **Documentation**: Do not add docstrings to unchanged code
- **Defensive coding**: Do not add error handling for impossible scenarios
- **Abstractions**: Do not create helper functions/classes for one-time operations
- **Tests**: Do not add tests for code that was not modified (unless explicitly asked)
- **Files**: Do not create new files when editing an existing one would suffice

When in doubt, do less. A small, correct change is better than a comprehensive one
that introduces risk or scope creep.

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Proactive on code changes, tests, builds
  - Ask on git push, branch delete, CI changes
  - Never on security bypasses

  KNOWLEDGE WORK (legal, research, analysis):
  - Proactive on file reads, searches, drafts to Docs/
  - Ask on: publishing, sharing externally, modifying source documents
  - Ask on: any action that leaves the local environment
  - Never: modify original source documents (work on copies)
  - Add: "When unsure about factual claims, note uncertainty rather than asserting"

  GAME DEVELOPMENT:
  - Proactive on source edits, build, local test
  - Ask on: binary asset changes (cannot be done -- write editor steps instead)
  - Ask on: VCS submit (human-only in Perforce workflows)
  - Add: "Never edit .uasset or .umap files directly"
  - Add: "After build success, pause for manual playtest before continuing"

  CONSERVATIVE DOMAINS (medical, legal, financial):
  - Proactive ONLY on: file reads, searches, writing to Docs/
  - Ask on: ANY file edit to source material, any external action
  - Ask on: generating advice or recommendations (present as draft for review)
  - Never: present conclusions without citing sources
  - Add: "All outputs are drafts requiring human review"
  - Shrink the "autonomous" list significantly

  DATA ENGINEERING:
  - Proactive on: code edits, local test runs, schema design
  - Ask on: running queries against production, modifying pipeline configs
  - Ask on: data backfills, schema migrations on shared databases
  - Never: modify production data without explicit user instruction
-->

<!-- ANTI-PATTERNS

  1. ASK FOR EVERYTHING
     Problem: Codex asks "May I read this file?" or "Can I search the codebase?"
     User gets frustrated by constant interruptions for safe operations.
     Fix: Classify local reversible operations as autonomous.

  2. NEVER ASK FOR ANYTHING
     Problem: Codex pushes to main, deletes branches, runs migrations without asking.
     Fix: Classify externally visible and hard-to-reverse operations as ask-first.

  3. MISSING OVERENGINEERING PREVENTION
     Problem: User asks for a one-line fix. Codex adds 200 lines of error handling,
     creates new utility files, and adds documentation for unchanged functions.
     Fix: Include the overengineering prevention section. Especially important for GPT-5.5.

  4. GENERIC BOUNDARIES WITHOUT EXAMPLES
     Problem: "Ask before destructive operations" -- Codex is unsure what counts.
     Fix: List concrete examples (git push, rm -rf, database migration).

  5. NO DOMAIN-SPECIFIC RULES
     Problem: General rules miss domain-specific risks (binary assets, production data).
     Fix: Add domain-specific section with project-relevant examples.

  6. CONTRADICTING THE ORCHESTRATOR RULE
     Problem: Autonomy rule says "always ask before committing" but orchestrator
     routes include "commit with descriptive message" as a standard step.
     Fix: Ensure autonomy and routing rules are consistent.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 120 lines in generated output
  [ ] Three-tier classification (autonomous / ask / never)
  [ ] Concrete examples in each tier (not just categories)
  [ ] Domain-specific rules section present
  [ ] Overengineering prevention section present with all 6 bullet points
  [ ] Consistent with orchestrator rule (no contradictions)
  [ ] Covers VCS operations appropriate to the project's VCS
  [ ] Covers file operations (read/write/delete)
  [ ] Covers external operations (push, publish, API calls)
  [ ] "Never" tier includes security-critical items
  [ ] Core principle stated in one sentence at the top
  [ ] ASCII-only
-->

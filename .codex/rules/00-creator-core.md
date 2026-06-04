# Creator core (orchestrator rule)

The Harness Generator uses an orchestrator pattern: the main conversation stays lean,
delegates complex work to specialized agents via the Codex subagent tools, and returns
concise summaries pointing to artifacts on disk.

## Routing table

| User request | Route | Fallback | Notes |
|---|---|---|---|
| /create (bare) | Skill trigger -> orchestrator pipeline | Prompt user for project context | See AGENTS.md pipeline steps |
| /create + project context | Handle directly (skip skill) | Skill trigger if context is complex | User already gave info; ask for path, then intake |
| /update | Skill (fork context) | Manual topic file edit | Ingests ProvideKnowledge/ then web-researches; local-only mode skips web |
| /validate-environment | Skill (fork context) | Manual checklist review | Runs validator, presents report |
| /upgrade-environment | Skill trigger -> orchestrator pipeline | Prompt user for environment path | See AGENTS.md upgrade pipeline steps |
| Upgrade interview questions | Handle directly (2-3 rounds) | Re-read UPGRADE_CONTEXT.md | Append answers to UPGRADE_CONTEXT.md |
| Upgrade analysis | Delegate to upgrade-analyzer | Re-run with narrower scope | Input: UPGRADE_CONTEXT.md path |
| Upgrade implementation | Delegate to component-generator | Re-run failed edits (max 2) | Pass approved recommendation IDs + UPGRADE_RECOMMENDATIONS.md |
| "How does the Harness Generator work?" | Answer directly | Refer to OVERVIEW.md | Use AGENTS.md + plan knowledge |
| "What will my environment include?" | Answer directly | Load relevant starter profile | Use plan + starter profiles |
| Profile-first intake questions | Handle directly | Delegate to intake-interviewer | Do not delegate simple Q&A rounds |
| Deep interview (no profile fit) | Delegate to intake-interviewer | Ask user for clarification | Use question relay protocol |
| Architecture design | Delegate to environment-architect | Ask user for clarification | Input: GENESIS.md path (single) or HUB_GENESIS.md path (hub) |
| File generation (passes 1-5) | Delegate to component-generator | Re-run failed pass (max 2 retries) | One invocation per pass. Hub: shell pass once, then 5 passes per work area |
| Post-generation validation | Delegate to environment-validator | Manual review checklist | Input: target directory path |
| /create inside existing hub | Detect parent HUB_GENESIS.md, add-area flow | Prompt user to confirm hub match | Skips shared-basics intake, writes new `<area-slug>/` under hub |
| Convert single environment to hub | Route via /upgrade-environment | Ask user to run /upgrade-environment | Moves existing `.codex/`, AGENTS.md, Docs/ into `<current-area-name>/`, generates parent shell |
| Collapse hub to single environment | Route via /upgrade-environment | Ask user to run /upgrade-environment | Only offered when hub has exactly one remaining area |

## Artifact-first handoff

Every delegated job MUST produce an artifact on disk:
- Intake (single) -> `<target>/Docs/Environment/GENESIS.md`
- Intake (hub) -> `<target>/Docs/Environment/HUB_GENESIS.md` plus one
  `<target>/<area-slug>/Docs/Environment/GENESIS.md` per work area
- Architect (single) -> `<target>/Docs/Environment/ARCHITECTURE.md`
- Architect (hub) -> `<target>/Docs/Environment/HUB_ARCHITECTURE.md` plus one
  `<target>/<area-slug>/Docs/Environment/ARCHITECTURE.md` per work area
- Generator -> generated files + GENERATION_PROGRESS.md (hub: progress tracks
  shell pass + per-area passes)
- Validator -> validation report at `<target>/Docs/Environment/`
- Upgrade skill -> UPGRADE_CONTEXT.md at `<target>/Docs/Environment/`
- Upgrade analyzer -> UPGRADE_RECOMMENDATIONS.md at `<target>/Docs/Environment/`

Return to the user: a short summary (3-10 lines) + paths to artifacts written.
Do NOT paste full file contents into chat.

## Autonomy

See AGENTS.md for full autonomy rules. Summary: all file operations within
Codex-Harness-Generator/ are pre-approved. Act and report.

## Vocabulary

Plain language for all user-facing output. Technical vocabulary only in
generated environment files. See AGENTS.md vocabulary section.

## Progress reporting

Between generation passes, report progress:
- "Creating foundation files... done (1/5)"
- "Creating assistant definitions... done (2/5)"
- etc.

This keeps the user informed during a process that involves multiple
agent delegations.

## Context discipline

The orchestrator keeps ONLY:
- Current pipeline step (intake / architect / generate / validate / done)
- Target directory path
- Last agent result summary (replaced each step)

Everything else lives on disk. Do not load templates, research docs,
or topic files into the orchestrator. Agents load what they need.

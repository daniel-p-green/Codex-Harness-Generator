# Generation Standards Reference

Conditional components and detailed standards for environment generation.
Loaded by the component-generator and environment-validator agents on demand.

See .codex/rules/02-generation-standards.md for the always-loaded core standards.

## Conditional components (intake-driven)

These are generated ONLY when intake answers justify them.

**Complexity gating**: Components that require third-party tools or external
dependencies are gated by the Environment Complexity decision table in
ARCHITECTURE.md. Each such component must have been presented to the user
during architecture confirmation (pipeline step 5) with its benefit, setup
cost, and simpler alternative. Only generate components the user approved.
See ARCHITECTURE.md Environment Complexity section for the user's decisions.

16. **Self-learning execution trigger**: When self-learning rule is generated,
   include a trigger mechanism (SessionStart hook or /state-load check) that
   counts unprocessed retro/ entries and recommends /update after 5+ entries.
   Without a trigger, observations accumulate but never get acted on.
17. **State file pruning**: /state-save skill MUST include pruning logic:
   SESSION_CONTEXT.md capped at 100 lines, compaction log separated,
   validation artifacts auto-archived after 3 per topic.
18. **Wiki staleness watermark** (for projects with /map-codebase): Generate
   `Docs/_working/state/WIKI_WATERMARK.json` initialized on first map run.
   /state-load compares VCS head to watermark and flags stale wiki sections.
19. **Document parsing setup** (when intake reveals external docs): Include
   tool recommendation and setup instructions in GETTING_STARTED.md. Options:
   PaddleOCR (light), MinerU (structured markdown), Docling (hierarchical).
20. **Multi-model routing notes** (when intake reveals multi-model usage):
   Document which model for which task type in routing table comments.
   Configure MCP bridges for cross-model access where applicable.
21. **Semantic search MCP** (for codebases 1000+ files): Recommend and document
   Codex Context MCP or Code-Graph-RAG setup in GETTING_STARTED.md.
22. **Session-segmented working memory** (for parallel sessions or teams):
   Use `_working/state/<session-slug>/` instead of a single state file.
   /state-save creates a slug from the task or user-provided name.
   /state-load lists available sessions for the user to resume.
23. **Multi-role support** (for teams with different roles sharing one project):
   Generate `Docs/Roles/` with AGENTS.override.md and local config profile
   templates per role. Add role-prefixed routing entries. Add "Setting up
   your role" to GETTING_STARTED.md. Keep shared rules role-neutral.
24. **Beads task tracker** (for complex multi-session projects with many
   interdependent subtasks, any domain, intermediate+ users): Include
   `bd init` setup, Codex hooks, .codex/config.toml permissions. Requires
   Git as persistence layer. For non-Git VCS projects, flag the trade-off
   of maintaining a parallel Git repo. Complements (does not replace)
   markdown wiki and /state-save. NOT for simple projects or beginners.
25. **Compliance enforcement hooks** (when intake reveals sensitive/regulated data
   AND user requests deterministic enforcement, not just advisory): Generate
   PreToolUse PII content gate hook + pii-patterns.conf with domain-appropriate
   patterns. Optionally generate UserPromptSubmit input screening hook. Always
   pair with the sensitive-data advisory rule (defense-in-depth). Include
   PostToolUse audit trail hook if regulatory compliance requires action logging.
   Document hook setup and pattern customization in GETTING_STARTED.md. Use
   PowerShell or prompt-type hooks on Windows for portability. See
   hooks-template.md Compliance section for implementation patterns.
26. **Token optimization guidance** (when GENESIS.md indicates cost-conscious or
   balanced efficiency priority): Generate environment settings calibrated to
   the efficiency tier from GENESIS.md Token Efficiency Priority section.
   - Cost-conscious: Set `CODEX_AUTOCOMPACT_PCT_OVERRIDE: "85"` in
     .codex/config.toml env block. Default all agents to medium-effort GPT-5.5. Target AGENTS.md at
     150 lines. Generate aggressive VCS ignore rules (domain + generic patterns).
     Include full RTK setup instructions in GETTING_STARTED.md. Consider agent
     consolidation where roles overlap.
   - Balanced: Use standard model selection policy (high-effort GPT-5.5 for plan/review, medium-effort GPT-5.5
     for implementation). Default compaction (95%). Standard domain-specific
     VCS ignore rules. Mention RTK as an option in GETTING_STARTED.md.
   - Quality-first: GPT-5.5 available for all agents per standard policy. Default
     compaction. Minimal VCS ignore rules (only binaries and build artifacts). No
     RTK mention. No optimization pressure.
   Include a "Monitoring and Optimizing Costs" section in GETTING_STARTED.md
   scaled to the tier (full setup for cost-conscious, brief for balanced,
   awareness-only for quality-first).
27. **Official plugin recommendations** (when ARCHITECTURE.md Recommended Plugins
   section lists matching plugins): Generate an "Optional Plugins" section in
   GETTING_STARTED.md with marketplace setup command and install commands for
   each recommended collection from `developers.openai.com/codex/concepts/customization`. Include
   relevant bundled skills (/code-review, /batch, /debug) as "Built-in Skills"
   subsection. Do NOT auto-install; document commands for user choice. Match
   intake signals per Topics/20-plugins.md section 20.4 matching rules.
28. **Skill eval recommendation** (when environment includes 3+ custom skills AND
   user is intermediate+): Include skill-creator install command and brief eval
   workflow in GETTING_STARTED.md "Refining Your Skills" section. Command:
   `codex skill install example-skills`. The skill-creator's Eval
   mode validates that generated skills actually improve model behavior beyond
   the no-skill baseline.
29. **Memory plugin recommendation** (when ARCHITECTURE.md Recommended Plugins
   section lists a memory plugin): Include setup instructions in GETTING_STARTED.md
   as an optional enhancement. Document: install/MCP registration command,
   one-sentence purpose, hook conflict notes if applicable. Frame as optional --
   the environment's /state-save and wiki structure work without it. Recommend
   ONE plugin (Synabun, codex memories, or mcp-memory-service) per Topics/05-memory.md
   section 5.10 matching rules.

30. **Status line configuration** (when intake reveals complex projects or large
   codebases): Generate status line setup instructions in GETTING_STARTED.md
   showing context health (used percentage, turn count) and optionally cost.
   Zero context cost. Tier-aware defaults: cost-conscious shows cost+duration,
   balanced shows context health, quality-first omits unless requested.
31. **InstructionsLoaded self-learning trigger** (when self-learning rule included):
   Generate InstructionsLoaded hook that checks retro/ entry count and recommends
   /update after 5+ entries. Preferred over SessionStart because it fires on rule
   reload too (e.g., after compaction or agent spawn). See Topics/16-hook-system.md
   section 16.10 for implementation pattern.
32. **MCP Tool Search threshold** (when 3+ MCP servers in architecture): Document
   ENABLE_TOOL_SEARCH setting in GETTING_STARTED.md with recommended threshold.
   Include guidance on writing server `instructions` fields to improve tool
   selection accuracy. See Topics/10-integration.md section 10.11.
33. **Service tier documentation** (when GENESIS.md indicates cost-conscious or
   balanced tier): Document available Codex service-tier trade-offs in
   GETTING_STARTED.md. Do not auto-enable a premium or latency-focused tier in
   shared `.codex/config.toml`; let the user opt in per project or session.
   See Topics/18-cost-awareness.md section 18.6.

34. **MCP server validation** (when any MCP servers in architecture): Every MCP
   server in the generated `.mcp.json` or .codex/config.toml must reference a verified
   server from `Docs/Templates/References/tool-registry.md` (section "Verified MCP
   Servers"). Do NOT generate MCP configurations for services without a verified
   server package. If the architecture references an unverified MCP server, flag it
   as a generation error and omit it from the output.

## Required: Working memory VCS exclusion

Every generated environment MUST exclude `Docs/_working/` from version control:
- Git: add `Docs/_working/` to `.gitignore`
- Perforce: add `Docs/_working/...` to `.p4ignore`
- Other VCS: document the exclusion in GETTING_STARTED.md

Without this, working state from one developer bleeds into another's sessions,
and state-save/state-load creates noisy VCS commits.

## State file format

Agent-managed state files (SESSION_SNAPSHOT, etc.) use JSON format.
JSON is less prone to model corruption than Markdown for programmatic state.
Human-readable context (SESSION_CONTEXT) uses Markdown.

## Routing table rules

- Every routing entry must be domain-specific, not generic
- Every entry must have a fallback chain
- Include complexity scaling: simple (direct), standard (2-3 agents),
  complex (pipeline with planning)
- Set proactive vs conservative action default per domain
- Include conditional workflow branching with explicit decision points

## Execution mode (required in every environment)

Every generated environment MUST include all three execution modes in
.codex/config.toml and the orchestrator rule:

1. **Sequential subagents** (default): Serial pipeline (plan -> implement ->
   review -> build). Used for most tasks with natural dependencies.
2. **Parallel subagents**: Multiple independent Codex subagent tools calls in a single
   message. Used when work can be split into independent streams.
3. **Agent Teams**: Experimental feature enabled via
   `CODEX_EXPERIMENTAL_AGENT_TEAMS: "1"` in .codex/config.toml env block.
   Used for large parallel investigations or multi-system work with
   non-overlapping file ownership.

The orchestrator rule (00-orchestrator.md) must include a decision matrix:
- Sequential: Tasks with natural serial flow or data dependencies
- Parallel subagents: 2-3 independent queries or investigations
- Agent Teams: Large tasks with 3+ independent streams, each owning
  distinct files, where the parallel speedup outweighs token cost (~15x)

Windows note: Split-pane mode does not work on Windows; use in-process mode.

For Git-based projects, prefer `--worktree` flag for parallel agent isolation
over Agent Teams. Worktrees provide filesystem isolation at ~4x cost (vs ~15x
for Teams) and prevent file conflicts entirely.

## Status line (recommended)

When the intake reveals complex projects or large codebases, recommend configuring
the Codex status line to display context health (used percentage, turn count).
This provides zero-context-cost monitoring. Include setup instructions in
GETTING_STARTED.md rather than auto-generating status line hooks (they require
platform-specific shell scripts).

## Optional skills (pattern-triggered)

- **/map-codebase** (Pattern F -- Codebase Mapping): Included for game-development
  profiles (always) and software-development profiles when 2+ codebase complexity
  signals are present. Scans source tree, classifies declarations into areas,
  updates wiki pages. Template: `Docs/Templates/Skills/map-codebase.md`.

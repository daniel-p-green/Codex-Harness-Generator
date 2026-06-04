# 5. Memory, Context, and State Architecture

This topic covers three tightly-related concerns: how persistent project
memory is structured (tiers, retrieval, promotion), how live conversation
context is managed (pressure thresholds, compaction, monitoring), and how
session state is checkpointed and resumed (the six-category taxonomy and
save/load symmetry).

## Table of contents

- Part A -- Memory architecture
  - 5.1 Just-In-Time Retrieval
  - 5.2 Metadata Signaling
  - 5.3 Auto-Memory Integration
  - 5.4 Tiered Architecture (Lite / Standard / Enterprise)
  - 5.5 Multi-Level Retrieval Guide
  - 5.6 Canonical Mappings Cache
  - 5.7 Code Landmarks
  - 5.8 Multi-Role Environments
  - 5.9 Working Memory Isolation and Promotion
  - 5.10 Third-Party Persistent Memory Plugins
  - 5.11 Personal Knowledge Management (PKM) Integration
- Part B -- Context management
  - 5.12 Compaction Strategy
  - 5.13 Tool Result Clearing
  - 5.14 Single-Feature-Per-Session
  - 5.15 Technique Selection
  - 5.16 1M Context Window
  - 5.17 Context Pressure Detection
  - 5.18 PreCompact Auto-Save Hook
  - 5.19 Status Line Monitoring
- Part C -- State management
  - 5.20 Six-Category Taxonomy
  - 5.21 JSON for Programmatic State
  - 5.22 Session Startup Protocol (save/load symmetry)
  - 5.23 Checkpoints (Built-in Rollback)
  - 5.24 Beads: Persistent Task Tracking (Optional)

---

## Part A -- Memory architecture

### 5.1 Just-In-Time Retrieval [ALL]

- **Established**: Baseline
- **Source**: context-engineering.md | Tier 1
- **Recommendation**: Maintain lightweight identifiers (file paths, stored queries, summary
  lines) and dynamically load full data at runtime. Do not pre-load everything into context.

  Implementation: INDEX.md files serve as ToCs, always loaded (~small). Detailed files
  loaded on-demand when the agent needs them. File hierarchies, naming conventions, and
  timestamps provide contextual signals without loading content.

  Trade-off: runtime exploration is slower than pre-computed data but avoids context
  pollution. Use opinionated engineering to prevent agents from misusing tools or chasing
  dead-ends during discovery.
- **Anti-pattern**: Loading all project documentation into context at startup. This fills
  context with potentially irrelevant information, causing context rot that degrades
  performance on the actual task.

### 5.2 Metadata Signaling [ALL]

- **Established**: Baseline
- **Source**: context-engineering.md | Tier 1
- **Recommendation**: Use meaningful naming, timestamps, and structural conventions as
  contextual signals:
  - File names indicate purpose: `2026-01-15_auth-refactor.md` is self-describing
  - Directory structure implies relationships: files in `Decisions/` are architectural decisions
  - Timestamps as proxy for relevance: more recent = likely more relevant
  - File sizes suggest complexity: large files merit deeper investigation
  - "Last Updated" and "Last Verified" fields on documents indicate staleness

  Every document should start with a 2-3 line summary so agents can quickly assess relevance
  without reading the full content.
- **Anti-pattern**: Generic filenames (notes.md, data.txt) and flat directory structures that
  provide no contextual signals. Agents must read full files to determine relevance, wasting
  context tokens.

### 5.3 Auto-Memory Integration [ALL]

- **Established**: Baseline
- **Source**: https://developers.openai.com/codex | Tier 1
- **Recommendation**: Codex has built-in auto-memory at
  `~/.codex/projects/<project>/memory/`. First 200 lines of MEMORY.md are loaded into the
  system prompt each session. Topic files load on demand.

  Generated environments should document how their custom Docs/ wiki structure relates to
  this built-in auto-memory. The wiki (Docs/) is for structured, shared project knowledge.
  Auto-memory is for Codex's own learnings per-user. Both complement each other.

  Control: `CODEX_DISABLE_AUTO_MEMORY=0` (force on) or `=1` (force off). Use
  `/memory` command to open the file selector.
- **Anti-pattern**: Ignoring auto-memory or fighting against it. Understand that Codex
  already maintains its own memory alongside any custom memory structure.

### 5.4 Tiered Architecture [ALL]

- **Established**: Baseline
- **Source**: context-engineering.md, https://developers.openai.com/codex/concepts/customization | Tier 1
- **Recommendation**: Scale memory structure to project complexity:

  **Lite** (solo, quick tasks, <3 people casual):
  ```
  Docs/
    index.md          # Home page + project context (always loaded)
    GETTING_STARTED.md
  Docs/_working/
    state/            # Session state
    retro/            # Friction logs
  ```

  **Standard** (1-5 people, medium complexity):
  ```
  Docs/
    index.md          # Home page (always loaded)
    overview.md
    Areas/            # Subsystem documentation
    Decisions/        # Key decisions with rationale
    Symbols/          # Key class reference (optional)
  Docs/_working/
    state/            # Session state
    sessions/         # Session history (auto-prune >30 days)
    retro/            # Friction logs
  ```

  **Enterprise** (large teams, complex domains):
  ```
  Docs/
    index.md
    overview.md
    Areas/
      <area>/
        index.md      # Sub-index per area
    Decisions/        # ADR format with status
    Symbols/
    Teams/            # Team-specific context
  Docs/_working/
    state/
    sessions/
    retro/
  ```

  The INDEX.md file is the ONLY file loaded by default. Everything else is on-demand.
- **Anti-pattern**: Using enterprise-scale memory for solo projects (overhead without benefit)
  or lite memory for team projects (insufficient structure for shared knowledge).

### 5.5 Multi-Level Retrieval Guide [ALL]

- **Established**: 2026-02
- **Source**: production game project production environment | Tier 2
- **Recommendation**: Structure wiki retrieval as a cascading guide with 3-4 levels
  of depth. Each level narrows the search before loading detailed content:

  - **Level 1 (Router)**: Master index.md -- determines which wiki section to enter
    (e.g., Design/ vs Dev/, or Areas/Combat/ vs Areas/Networking/)
  - **Level 2 (Section)**: Section index -- overviews and subsystem summaries
  - **Level 3 (Detail)**: Individual system or topic pages
  - **Level 4 (Entity)**: Per-entity pages (individual classes, characters, endpoints)

  The master index.md is the ONLY file loaded by default. It contains a retrieval
  guide telling the assistant exactly which path to follow based on the current task:
  - Working on character balance? -> Design/Characters/<name>.md
  - Debugging combat code? -> Dev/Systems/Combat/overview.md
  - Cross-cutting issue? -> Load BOTH the relevant design page AND system page

  For domains with multiple knowledge dimensions (e.g., game design + code architecture,
  business rules + technical implementation), use separate wiki sections rather than
  mixing concerns in one hierarchy.
- **Anti-pattern**: Loading all wiki pages on startup. Even a moderately-sized wiki
  (10-15 pages) can consume 2,000+ lines of context. Multi-level retrieval ensures
  only the 1-2 relevant pages are loaded per task.

### 5.6 Canonical Mappings Cache [ALL]

- **Established**: 2026-02
- **Source**: production game project production environment | Tier 2
- **Recommendation**: When skills need to disambiguate assets, configurations, or
  resources, store resolved mappings in a JSON cache file (e.g.,
  `_working/blueprints/canonical-mappings.json`). On subsequent runs, check the cache
  before re-asking the user.

  This prevents repeated disambiguation questions across sessions for resources that
  rarely change. Include a staleness mechanism (e.g., file date comparison) to
  invalidate cached mappings when source assets change.
- **Anti-pattern**: Re-asking users to disambiguate the same resources every session.
  Users expect the assistant to remember previous choices.

### 5.7 Code Landmarks [ALL]

- **Established**: 2026-02
- **Source**: codex-bootstrap project, community patterns | Tier 2
- **Recommendation**: For large codebases, generate a lightweight "landmarks" file
  listing the most important files and their purposes. Unlike full wiki pages
  (from /map-codebase), landmarks are a quick-reference cheat sheet:

  ```markdown
  # Code Landmarks
  - src/auth/middleware.ts -- Authentication middleware (JWT validation)
  - src/api/routes/index.ts -- API route registration
  - src/db/schema.ts -- Database schema definitions
  - src/config.ts -- Environment configuration
  - tests/fixtures/ -- Shared test fixtures
  ```

  Landmarks are small enough to stay in context (~20-30 lines) and help both Codex
  and humans navigate the codebase quickly. They complement detailed wiki pages by
  providing instant orientation.

  Generate landmarks during /map-codebase as a byproduct, or let users create them
  manually. Store in `Docs/landmarks.md` or `Docs/Dev/landmarks.md`.
- **Anti-pattern**: Loading full wiki pages for quick navigation. A 200-line system
  overview is overkill when you just need to know which file handles authentication.

### 5.8 Multi-Role Environments [ALL]

- **Established**: 2026-03
- **Source**: production game project production analysis, Codex memory hierarchy | Tier 2
- **Recommendation**: When multiple human roles work from the same project directory
  (developers, designers, QA, marketing, producers, etc.), each role needs different
  routing, context loading, permissions, and autonomy levels — but they share the same
  underlying data (source code, VCS history, assets, documents).

  Codex does NOT support conditional rule loading — all `.codex/rules/*.md`
  files load for every user. This means multi-role support requires a layered approach
  using the native override hierarchy:

  **Layer 1 — Shared foundation (checked into VCS, everyone gets it):**
  - `AGENTS.md`: Project purpose, universal constraints, command reference
  - `.codex/rules/`: Rules applicable to ALL roles (orchestrator, autonomy,
    error handling, memory management). Keep role-specific detail OUT of shared rules.
  - `.codex/agents/`: ALL agents for all roles. Each agent is small (~80 lines)
    so unused agents have low context cost.
  - `.agents/skills/`: ALL skills for all roles. Skills fork context on invocation
    so unused skills cost nothing.
  - `.codex/config.toml`: Permissions safe for ALL roles (conservative — only allow what
    every role needs). Role-specific permissions go in local config profile.
  - `Docs/`: Shared wiki accessible to all roles.

  **Layer 2 — Role-specific overrides (NOT checked in, per-user):**
  - `AGENTS.override.md`: Role declaration, role-specific priorities, routing hints.
    Each role gets a template from `Docs/Roles/<role-name>.local.md` that they
    copy to the project root as `AGENTS.override.md`.
  - `local config profile`: Role-specific permissions (e.g., social media role
    gets read-only P4 access, developers get full edit access).
  - `~/.codex/AGENTS.md`: User's global identity and preferences.
  - Auto-memory (`~/.codex/projects/<project>/memory/`): Already per-user per-project.

  **Layer 3 — Role-aware orchestrator:**
  The routing rule should detect the user's role from `AGENTS.override.md` and adjust
  behavior. Include a role-detection section at the top of the orchestrator rule:
  ```
  ## Role Detection
  If AGENTS.override.md declares a role, use role-specific routing entries.
  If no role is declared, ask on first interaction: "What is your role on
  this project?" and suggest the user set up AGENTS.override.md.
  ```

  The routing table includes role-prefixed entries:
  ```
  | User Intent | Role | Route |
  | find social media content | social-media | explorer (scan recent P4 commits + screenshots) |
  | review recent changes | social-media | explorer (P4 changelists, plain-language summary) |
  | implement combat feature | developer | planner -> implementer -> reviewer |
  | check build status | developer | build agent |
  | update design doc | designer | writer (update Docs/Design/) |
  ```

  **What to generate for multi-role environments:**
  - `Docs/Roles/` directory with a `.local.md` template per role
  - Role-prefixed routing entries in the orchestrator rule
  - GETTING_STARTED.md section: "Setting up your role" with copy instructions
  - `local config profile` templates per role (in `Docs/Roles/<role>..codex/config.toml`)
  - Role-appropriate wiki retrieval hints in each `.local.md` template

  **Context cost management:**
  All rules load for everyone — this is the hard constraint. Mitigate by:
  - Keeping shared rules lean and role-neutral
  - Putting role-specific detail in `AGENTS.override.md` (not shared rules)
  - Using skill descriptions to ensure role-irrelevant skills don't trigger
  - Documenting which wiki sections each role should load (in their `.local.md`)

  **When to use multi-role vs separate environments:**
  - Same project, shared data, different tasks → multi-role (one environment)
  - Completely different projects → separate environments
  - Different data sets, no shared context → separate environments

- **Anti-pattern**: Putting role-specific instructions in shared AGENTS.md or rules
  (wastes context for other roles). Also: creating separate environments for each role
  when they share the same project data (duplication, drift, maintenance burden). Also:
  assuming "team" means "everyone does the same thing" — team size and role diversity
  are separate questions.

### 5.9 Working Memory Isolation and Promotion [ALL]

- **Established**: 2026-03
- **Source**: production game project production environment, multi-user workflow analysis | Tier 2
- **Recommendation**: The `Docs/_working/` directory serves as **session-scoped scratch
  space** isolated from the shared wiki. Three aspects need explicit configuration:

  **1. VCS exclusion**: `_working/` MUST be excluded from version control so each
  developer (or each machine) has independent working state. Add to the appropriate
  ignore file during generation:
  - Git: `Docs/_working/` in `.gitignore`
  - Perforce: `Docs/_working/...` in `.p4ignore`
  - SVN: `svn:ignore` property on `Docs/` directory
  - Other VCS: Document the exclusion pattern in GETTING_STARTED.md

  Without VCS exclusion, working state from one developer bleeds into another's
  sessions, and state-save/state-load creates noisy commits on every session.

  **2. Session segmentation (concurrent chats)**: When a user runs multiple Codex
  Code sessions simultaneously on the same project (common for parallel work streams),
  each session's state can collide in `_working/state/`. Two strategies:

  - **Default (overwrite)**: Latest session wins. Simple, works for most solo users
    who run one session at a time. SESSION_SNAPSHOT.json is a single file overwritten
    on each save.
  - **Segmented (recommended for parallel sessions)**: State files include a session
    identifier: `_working/state/<session-slug>/SESSION_SNAPSHOT.json`. Each chat works
    in its own subdirectory. /state-save creates the slug from the task description
    or a user-provided name. /state-load lists available sessions and lets the user
    pick which to resume.

  During intake, ask about concurrent sessions when the user indicates parallel work
  or team usage. Default to overwrite for solo; recommend segmented for team or
  parallel-session workflows.

  **3. Promote-on-commit pattern**: Working memory stays local and transient. Shared
  wiki (Docs/Areas/, Docs/Decisions/, etc.) is only updated at "commit points" --
  moments when the user considers work done and ready to share. The commit point
  varies by domain:

  | Domain | Commit Point | Promotion Trigger |
  |---|---|---|
  | Software dev | VCS commit (git commit, p4 submit) | After successful build + tests |
  | Legal | Section draft approved by reviewer | After review signoff |
  | Research | Paper section finalized | After peer review or self-review |
  | Data analysis | Report delivered to stakeholder | After validation + presentation |
  | Game dev | Feature passes playtest gate | After playtest + VCS submit |
  | Knowledge work | Deliverable sent to client/audience | After quality review |

  What gets promoted:
  - New architectural decisions -> `Docs/Decisions/`
  - Updated system/area knowledge -> `Docs/Areas/<area>/`
  - New conventions or patterns discovered -> `Docs/` or AGENTS.md
  - Reusable session artifacts (scripts, templates) -> `Docs/` or appropriate location

  What stays in `_working/`:
  - Session snapshots and context (replaced next session)
  - In-progress drafts and exploration notes
  - Friction log entries (consumed by /update, then archived)
  - Validation artifacts (pruned after 30 days)

  During intake, identify the domain-specific commit point. Generate the promotion
  trigger in the /state-save skill or as a post-commit hook. The key principle:
  **working memory is private and disposable; shared wiki is curated and durable.**

- **Anti-pattern**: Committing `_working/` to VCS (state conflicts, noisy history).
  Also: updating the shared wiki mid-session before work is validated (premature
  promotion pollutes shared knowledge with unverified information). Also: never
  promoting anything (knowledge stays trapped in `_working/` and is lost on prune).

### 5.10 Third-Party Persistent Memory Plugins [ALL]

- **Established**: 2026-03
- **Source**: github.com/danilokhury/Synabun, github.com/thedotmack/codex memories,
  github.com/doobidoo/mcp-memory-service | Tier 2
- **Recommendation**: Several open-source memory plugins extend Codex's
  built-in memory with semantic vector search, cross-session recall, and
  automated context capture. These complement (do not replace) the generated
  environment's markdown-based memory structure.

  **When to recommend during generation**: When intake reveals multi-session
  projects with complex context that exceeds what markdown files and /state-save
  can track -- especially projects where the user reports "Codex keeps forgetting"
  or "I have to re-explain the architecture every session."

  **Evaluation criteria for recommending a plugin**:
  1. No external API dependencies (runs fully local)
  2. No paid subscription required for core features
  3. Open-source with permissive or copyleft license
  4. Compatible with Codex's hook/MCP system
  5. Does not conflict with the generated environment's own hooks and memory

  **Recommended plugins** (all free, local-first, open-source):

  | Plugin | Memory Model | Integration | Best For | Dependencies |
  |--------|-------------|-------------|----------|-------------|
  | **Synabun** | Semantic vectors in SQLite via Transformers.js (all-MiniLM-L6-v2, fully local) | MCP server (11 tools) + Codex hooks + /synabun command | Projects needing semantic recall across sessions without any external API; multi-project support; visual memory graph (3D Neural Interface) | Node.js 22.5+ only |
  | **codex memories** | SQLite FTS5 + Chroma vector DB, AI-compressed summaries via Agent SDK | Plugin install + 5 lifecycle hooks + MCP tools | Long sessions hitting context limits; "Endless Mode" extends ~50 tool uses to ~1,000 via progressive 3-layer recall (~10x token efficiency) | Node.js 18+, Bun, uv (auto-installed) |
  | **mcp-memory-service** | SQLite + ONNX embeddings, knowledge graph with typed edges (causes, fixes, contradicts) | MCP server + REST API | Multi-agent pipelines needing structured knowledge with causal relationships; autonomous consolidation prevents unbounded growth | Python 3.10+ |

  **How to integrate with generated environments**: These plugins add a
  persistent semantic layer alongside the environment's file-based memory.
  They do NOT replace:
  - /state-save and /state-load (checkpoint-based session state)
  - Docs/ wiki structure (curated, promoted knowledge)
  - .codex/auto-memory (Codex's built-in preference learning)

  They DO add:
  - Semantic recall across sessions ("what did we decide about X last week?")
  - Automated context capture without manual /state-save
  - Cross-project knowledge sharing (Synabun, mcp-memory-service)

  **For generated environments**: Document the recommended plugin in
  GETTING_STARTED.md as an optional enhancement, not a requirement. Include
  install command and one-sentence description. The choice of plugin depends
  on the user's stack:
  - Node.js project or no coding: Synabun (zero external deps, visual UI)
  - Heavy coding with long sessions: codex memories (Endless Mode, compression)
  - Python/multi-agent pipelines: mcp-memory-service (knowledge graph)

  **Hook conflicts**: If the generated environment uses SessionStart, Stop, or
  PreCompact hooks, document potential ordering issues with plugins that use
  the same hooks. Codex runs hooks in registration order.

- **Anti-pattern**: Recommending memory plugins for simple or short-session
  projects where file-based /state-save is sufficient. Adding a vector DB
  and MCP server to a project that fits in one session is overengineering.
  Also: recommending plugins with external API dependencies (cloud vector DBs,
  paid embedding services) without the user requesting them.

### 5.11 Personal Knowledge Management (PKM) Integration [ALL]

- **Established**: 2026-03
- **Source**: Community workflows (Obsidian + Codex pipelines) | Tier 2
- **Recommendation**: Some users maintain a personal knowledge management system
  (Obsidian, Logseq, Notion local, etc.) as their long-term memory and research
  hub. This is a different category from Codex-specific memory plugins (5.10):

  | Approach | What it is | Codex's role | Persistence |
  |----------|-----------|---------------|-------------|
  | Memory plugins (5.10) | Codex-specific tools (Synabun, codex memories) | Codex owns the memory store | Codex-managed |
  | PKM integration (5.11) | User's existing knowledge tool (Obsidian, Logseq) | Codex reads/writes to user's vault | User-managed |

  **Pattern: PKM as Shared Knowledge Layer**

  Codex writes structured markdown notes to the user's PKM vault. The PKM tool
  indexes, links, and surfaces them. Codex reads them back in future sessions
  for continuity. The user curates and extends the knowledge independently.

  **Integration approaches** (from lightest to heaviest):
  1. **File-based** (simplest): Point Codex at the vault directory. Codex
     reads/writes markdown files directly. Works with any PKM tool.
     Generated environment: add vault path to .codex/config.toml allowed paths,
     add vault structure conventions to AGENTS.md.
  2. **MCP-based**: Use a PKM-specific MCP server (e.g., obsidian-mcp) for
     richer integration (search, metadata, graph traversal).
     Generated environment: add MCP server config to .mcp.json.
  3. **Pipeline**: Codex generates content -> formats for PKM conventions
     (frontmatter, tags, links) -> writes to vault -> PKM indexes.
     Generated environment: add formatting conventions to a rule file,
     generate a pipeline skill for structured knowledge capture.

  **When to include PKM integration**:
  - User explicitly mentions Obsidian, Logseq, Notion, or "my notes"
  - User describes a research workflow where findings accumulate over time
  - User says "I want Codex to add to my knowledge base"

  **When NOT to include**:
  - User doesn't mention a PKM tool (don't suggest one speculatively)
  - User's workflow doesn't involve research or knowledge accumulation
  - The built-in wiki + /state-save is sufficient for their needs

  **Intake signal**: Add to external services probe: "Do you use a personal
  knowledge management tool like Obsidian, Logseq, or Notion?" If yes, ask
  for the vault/workspace path and their conventions (tags, folder structure).

  **For generated environments**: Include vault path configuration in
  .codex/config.toml, add PKM conventions to a rule file, and optionally generate
  a `/capture-knowledge` skill that formats Codex's findings for the PKM tool.

- **Anti-pattern**: Recommending Obsidian or Logseq to users who don't already
  use them. PKM integration is about connecting to the user's *existing* tool,
  not adding a new tool to their stack. Also: writing unstructured notes to a
  PKM vault without following the user's conventions (tags, frontmatter, folder
  structure) -- this creates noise the user has to clean up.

---

## Part B -- Context management

### 5.12 Compaction Strategy [ALL]

- **Established**: Baseline
- **Source**: context-engineering.md, https://developers.openai.com/codex/concepts/customization, https://developers.openai.com/codex | Tier 1
- **Recommendation**: Auto-compaction triggers at ~95% context capacity (configurable via
  `CODEX_AUTOCOMPACT_PCT_OVERRIDE`). Design environments with compaction in mind:

  Preserve during compaction:
  - Architectural decisions
  - Unresolved bugs and issues
  - Implementation details for current work
  - List of modified files
  - Current task status and remaining steps
  - Test commands and results

  Discard during compaction:
  - Redundant tool outputs
  - Redundant messages
  - Raw file contents that can be re-read
  - Exploratory tangents that did not lead anywhere

  Include compaction hints in AGENTS.md: "When compacting, always preserve the full list of
  modified files, any test commands and results, and the current task status."

  Manual compaction: `/compact [focus instructions]` for targeted compaction with guidance
  on what to preserve.
- **Anti-pattern**: Relying on compaction alone for long-running tasks. Compaction inevitably
  loses subtle context. Use structured note-taking and disk-based state for information that
  must survive compaction.

### 5.13 Tool Result Clearing [ALL]

- **Established**: 2025-09
- **Source**: context-engineering.md | Tier 1
- **Recommendation**: Old tool results deep in conversation history are "one of the safest,
  lightest touch forms of compaction." Once a tool has been called and the result processed,
  the raw result is unlikely to be needed again. Clear these proactively to free context.

  This is particularly important for file reads -- the raw content of a 500-line file read
  10 turns ago is consuming tokens without providing value if the agent has already
  extracted the relevant information.
- **Anti-pattern**: Keeping all raw tool results in context history indefinitely. A single
  debugging session can consume tens of thousands of tokens in tool output alone.

### 5.14 Single-Feature-Per-Session [ALL]

- **Established**: Baseline
- **Source**: long-running-agent-harnesses.md, https://developers.openai.com/codex/concepts/customization | Tier 1
- **Recommendation**: Scope each session to one feature, one bugfix, or one refactor.
  This prevents context exhaustion. Use `/clear` between unrelated tasks.

  Rule of thumb: if you have corrected Codex more than twice on the same issue, `/clear`
  and start fresh with a better prompt. A clean session + better prompt almost always
  outperforms a long session + accumulated corrections.

  The "kitchen sink session" anti-pattern (starting with one task, asking unrelated things,
  going back) fills context with irrelevant information and degrades performance on all tasks.
- **Anti-pattern**: Multi-topic sessions. Context pollution from unrelated work degrades
  performance. Each topic change adds irrelevant tokens that compete with relevant context.

### 5.15 Technique Selection [ALL]

- **Established**: 2025-09
- **Source**: context-engineering.md | Tier 1
- **Recommendation**: Choose context management technique based on task pattern:
  - **Compaction**: Best for tasks requiring extensive back-and-forth conversation. Use when
    the work is inherently conversational and iterative.
  - **Structured note-taking**: Best for iterative development with clear milestones. Agent
    writes to a state/notes file at milestones, reads it back after compaction or session
    restart.
  - **Multi-agent (subagents)**: Best for complex research/analysis where parallel exploration
    pays dividends. Each subagent explores in separate context, returns compressed summary.

  These techniques compose: use subagents for investigation, note-taking for progress
  tracking, and compaction for long conversations.
- **Anti-pattern**: Using one technique for all situations. Compaction alone fails for
  truly long-running tasks. Note-taking alone is insufficient for conversational back-and-forth.
  Subagents are overkill for simple sequential work.

### 5.16 1M Context Window [ALL]

- **Established**: 2026-03
- **Source**: developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**: For large contexts, prefer GPT-5.5 with explicit
  `model_reasoning_effort` and confirm the active context-window behavior in current
  OpenAI docs before promising a specific limit or pricing tier.

  For generated environments with large codebases, mention 1M context in GETTING_STARTED.md
  as an option for sessions involving broad codebase analysis. Disable with
  `CODEX_DISABLE_1M_CONTEXT=1` if cost control is a priority.

  1M context does NOT eliminate the need for good context management. Even with 1M tokens,
  signal-to-noise ratio degrades as context grows. Continue to use wiki retrieval, subagent
  delegation, and compaction strategies.
- **Anti-pattern**: Assuming 1M context eliminates context management concerns. Larger context
  windows increase cost and can degrade response quality when filled with low-relevance content.

### 5.17 Context Pressure Detection [ALL]

- **Established**: Baseline
- **Source**: https://developers.openai.com/codex/subagents, context-engineering.md | Tier 1
- **Recommendation**: Track multiple signals for context pressure:
  - Turn count threshold: ~30 turns suggests approaching limits
  - Delegation count: ~10 subagent invocations in one session
  - File reads: ~15 file reads accumulates significant context

  Two-stage approach:
  - 70% capacity: Proactively summarize progress, write state to disk
  - 100% capacity: Auto-save state, prompt user to `/clear`

  Include in generated environments: "Your context window will be automatically compacted as
  it approaches its limit. Do not stop tasks early due to token budget concerns. Save your
  current progress and state to memory before the context window refreshes."
- **Anti-pattern**: No context pressure awareness. Without proactive management, the session
  hits compaction unexpectedly and may lose critical context.

### 5.18 PreCompact Auto-Save Hook [ALL]

- **Established**: 2026-02
- **Source**: production game project production environment, https://developers.openai.com/codex | Tier 2
- **Recommendation**: Use the PreCompact hook event to automatically save session state
  before auto-compaction triggers. This is a safety net for progress that has not yet
  been written to disk.

  Implementation: A PreCompact hook script appends the current activity summary
  to SESSION_CONTEXT.md. Combined with a status line tracking turn count and activity,
  this ensures no progress is silently lost during compaction.

  ```json
  {
    "hooks": {
      "PreCompact": [{
        "hooks": [{
          "type": "command",
          "command": ".codex/hooks/pre-compact-save.sh",
          "timeout": 10,
          "statusMessage": "Saving state before compaction..."
        }]
      }]
    }
  }
  ```

  The hook should read the status line state file (if using status line monitoring)
  and append a timestamped summary to the session context file.
- **Anti-pattern**: Relying solely on Codex to remember to save state before compaction.
  Auto-compaction triggers at ~95% without warning. Only a deterministic hook guarantees
  state is saved.

### 5.19 Status Line Monitoring [ALL]

- **Established**: 2026-02
- **Source**: production game project production environment, https://developers.openai.com/codex | Tier 2
- **Recommendation**: Use the Codex status line feature to display context health
  passively. The status line shows information in the terminal without consuming
  conversation context.

  Useful status line content:
  - `context_window.used_percentage` -- shows how full the context is
  - Turn count (tracked by a PostToolUse hook)
  - Current activity description (set by a UserPromptSubmit hook)
  - Session ID or task identifier

  Status line is configured via `CODEX_STATUSLINE` environment variable pointing
  to a script or via .codex/config.toml status line configuration.

  **Portability note**: Status line scripts that use bash (.sh) require WSL on Windows.
  For cross-platform environments, consider PowerShell alternatives or document the WSL
  dependency. When generating environments for Windows users, prefer PowerShell hooks
  or document the bash/WSL requirement in GETTING_STARTED.md.
- **Anti-pattern**: Using conversation messages to report context health. This consumes
  the very context it is trying to monitor. Status line is zero-context-cost monitoring.

---

## Part C -- State management

State management bridges memory (durable) and context (live): it checkpoints
the live session to disk so that work survives compaction and session
boundaries. The /state-save skill writes the six categories below; /state-load
reads everything /state-save writes (save/load symmetry, enforced by quality
gate 12).

### 5.20 Six-Category Taxonomy [ALL]

- **Established**: Baseline
- **Source**: long-running-agent-harnesses.md, common-workflows.md | Tier 1
- **Recommendation**: Capture state across six universal categories:
  1. **Tool state**: VCS status (branch, modified files), build status, external tool state.
     Skip gracefully if a tool is not configured.
  2. **Task state**: Current goal, what is done, what remains, priority of remaining items.
  3. **Artifact state**: Files and documents created or modified (paths only, not content).
  4. **Decision state**: Key decisions made and their rationale. These are the hardest to
     reconstruct and most valuable to preserve.
  5. **Blocked state**: What is waiting on the user or an external process.
  6. **Drift risk**: What could change externally between sessions (other developers'
     commits, dependency updates, API changes).
- **Anti-pattern**: Saving only task state and forgetting decisions. When a session resumes,
  the agent may revisit decisions that were already made, wasting time and potentially
  choosing differently.

### 5.21 JSON for Programmatic State [ALL]

- **Established**: 2025-09
- **Source**: long-running-agent-harnesses.md | Tier 1
- **Recommendation**: Use JSON format for agent-managed state files. Models are less likely
  to inappropriately change or overwrite JSON files compared to Markdown. JSON provides
  structural protection against accidental modification.

  Use dual format: `SESSION_SNAPSHOT.json` (programmatic, parseable) +
  `SESSION_CONTEXT.md` (human-readable narrative for quick orientation).

  The JSON file is the source of truth for automated processing. The Markdown file provides
  context for human review and for Codex's initial orientation on session load.
- **Anti-pattern**: Using Markdown for all state files. Models corrupt Markdown more easily
  than JSON -- they may add content, reformat sections, or merge entries incorrectly during
  state updates.

### 5.22 Session Startup Protocol (save/load symmetry) [ALL]

- **Established**: 2025-09
- **Source**: long-running-agent-harnesses.md, common-workflows.md | Tier 1
- **Recommendation**: Every session should begin with a structured startup sequence:
  1. `pwd` -- confirm working directory
  2. Read progress/state files (SESSION_SNAPSHOT.json, SESSION_CONTEXT.md)
  3. Read git log or VCS state
  4. Verify baseline (existing tests still pass, build succeeds)
  5. Select highest-priority incomplete task

  This protocol prevents starting new work on a broken foundation and ensures continuity
  with prior sessions. /state-load must read every category /state-save writes (the six
  categories of 5.20); a load step that omits a saved category silently drops continuity.
- **Anti-pattern**: Starting work immediately without checking state. This leads to building
  on broken foundations, duplicating completed work, or missing context from prior sessions.

### 5.23 Checkpoints (Built-in Rollback) [ALL]

- **Established**: 2026-03
- **Source**: developers.openai.com/api/docs/guides/reasoning, Codex v2.0 | Tier 1
- **Recommendation**: Codex now supports built-in checkpoints that save progress and
  allow instant rollback to a previous state. This is a native alternative to the /state-save
  skill for file-level rollback (not context-level).

  Checkpoints complement, but do not replace, the /state-save skill. Checkpoints handle
  file-system rollback (undo file changes). /state-save preserves cognitive state (decisions,
  task progress, blocked items) that survives session boundaries and compaction.

  For generated environments, mention checkpoints in GETTING_STARTED.md as a safety net
  for exploratory work. Keep /state-save for structured session continuity.
- **Anti-pattern**: Relying solely on checkpoints for session continuity. Checkpoints restore
  files but do not restore the assistant's understanding of decisions, context, or task state.

### 5.24 Beads: Persistent Task Tracking (Optional) [ALL]

- **Established**: 2026-03
- **Source**: github.com/steveyegge/beads (~18k stars), Steve Yegge blog posts, community patterns | Tier 2
- **Recommendation**: Beads (`bd` CLI) is a Git-backed issue tracker designed for AI agents.
  It stores tasks as JSONL in `.beads/`, uses SQLite for fast queries, and persists across
  sessions via Git. It is an **optional complement** to the markdown wiki and /state-save
  system, NOT a replacement.

  Although marketed for coding agents, the underlying mechanics -- task dependency graphs,
  cross-session persistence, topological sorting of unblocked work -- are domain-agnostic.
  Any complex multi-session project with interdependent subtasks benefits: drafting a legal
  document with 30 sections each needing case law verification, a research paper with
  parallel literature review tracks, or an infrastructure migration with phased rollouts.

  **What Beads does well** (that markdown state files struggle with):
  - Persistent task dependency graph surviving compaction and session boundaries
  - `bd ready` returns only unblocked tasks (topological sort) -- no parsing needed
  - Atomic CLI operations prevent state corruption from concurrent or interrupted edits
  - Hash-based IDs prevent merge conflicts in multi-agent or team workflows
  - `bd compact` uses LLM to summarize old closed tasks (semantic memory decay)
  - ~1-2k tokens per query vs 5-50k for loading full markdown plans

  **What Beads does NOT do** (markdown wiki still required for):
  - Knowledge management (architecture decisions, conventions, gotchas, preferences)
  - Non-task context (domain reference, design docs, learned patterns)
  - Human-readable documentation (JSONL is not human-friendly)

  **When to include in generated environments:**
  - Complex multi-session work with many interdependent subtasks (any domain)
  - Parallel agent workflows (conflict-free by design)
  - User is intermediate/advanced with CLI tools
  - Git is acceptable as the persistence layer

  **When NOT to include:**
  - Simple/single-session work where a TODO list suffices
  - Beginner users unfamiliar with CLI tools
  - User wants to minimize local tooling dependencies
  - Non-Git VCS environments where the user does not want to add a Git repo alongside
    their primary VCS (Beads requires Git; for Perforce/SVN projects, adding a parallel
    Git repo solely for Beads is possible but adds complexity -- flag the trade-off)
  - Projects where Git commit noise from `.beads/` is a concern

  **Non-Git VCS note**: Beads requires Git for persistence. For projects using Perforce,
  SVN, or other non-Git VCS, including Beads means maintaining a parallel Git repo (or
  Git within the project) solely for task tracking. This is viable but adds setup
  complexity. During intake, present this trade-off explicitly rather than silently
  excluding Beads.

  **Integration with Codex** (three methods, in order of preference):
  1. Plugin: `/plugin marketplace add steveyegge/beads` (simplest)
  2. CLI + hooks: `bd setup codex` installs SessionStart and PreCompact hooks
  3. MCP server: `beads-mcp` package (least efficient, 10-50k token schema overhead)

  **When generating with Beads, include:**
  - `bd init` and `bd setup codex` in GETTING_STARTED.md setup steps
  - `bd` command usage documented in AGENTS.md and GETTING_STARTED.md
  - Chain PreCompact hook: `bd sync && <existing state-save>`
  - Note in AGENTS.md: "Use `bd ready` to find next task, `bd create` for new tasks"
  - Keep /state-save and /state-load for cognitive state (decisions, blocked, drift)
  - Keep markdown wiki for knowledge management

  **Maturity warning**: v0.58 as of March 2026 (alpha, pre-1.0). API may change.
  Document this risk in GETTING_STARTED.md when including Beads.

- **Anti-pattern**: Replacing the entire markdown wiki with Beads. Beads is a task tracker,
  not a knowledge base. Also: including Beads for simple projects or beginner environments
  where it adds complexity without proportional benefit.

---

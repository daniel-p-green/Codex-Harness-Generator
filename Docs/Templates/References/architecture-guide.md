# Architecture Guide

Reference document for the environment-architect agent. Contains architecture
section templates, generation patterns, output format, and quality gates.

Loaded by the environment-architect agent in Step 2 of its procedure.

## Architecture Sections

### 1. Component Manifest

Map every output file to its generation pass (1-5) and its reference template. This is the single source of truth for what the component-generator produces.

Format:
```
| Pass | File Path | Reference Template | Notes |
|------|-----------|-------------------|-------|
| 1 | CLAUDE.md | Core/claude-md.md | ... |
| 1 | .claude/rules/00-orchestrator.md | Core/orchestrator-rule.md | ... |
| ... | ... | ... | ... |
```

Every file that will be generated must appear in this table, and nothing is generated that is not in it (validator check 16b). This includes every shipped file -- `.gitignore`, and `.mcp.json` whenever an MCP server is recommended -- not only the obvious components.

Pass assignments:
- Pass 1 (Foundation): CLAUDE.md, all rules, settings.json, .claudeignore, `.gitignore` (must exclude `Docs/_working/`), hooks (including the REQUIRED self-learning trigger hook -- see Hook configuration), and `.mcp.json` when any MCP server is recommended
- Pass 2 (Agents): All agent definition files
- Pass 3 (Skills): All skill definitions (SKILL.md + scripts/ + references/)
- Pass 4 (Infrastructure): Wiki scaffold (Docs/index.md, overview.md, area stubs), working memory scaffold (Docs/_working/state/, sessions/, retro/), self-learning seeds
- Pass 5 (Documentation): GETTING_STARTED.md, README.md, VERSION.md, cross-reference verification pass

### 2. Routing Table

IMPORTANT: The routing table must be FULLY ENUMERATED with DOMAIN-SPECIFIC entries. Generic entries like "code question -> researcher" are insufficient. Every entry must reflect the user's actual project domain, using vocabulary and concepts from GENESIS.md.

Each entry must include:
- User intent (phrased as the user would say it, in domain-specific language)
- Complexity level (simple / standard / complex)
- Primary route (which agent, with specific context about what to check)
- Fallback chain (what to try if the primary route does not resolve it)

Minimum 10 routing entries covering at least 8 distinct intent categories. Include entries for:
- Every distinct work type the user described
- Error/debugging scenarios specific to their domain
- Ambiguous requests (with resolution strategy: investigate vs. ask)
- "Where is X" / exploration requests

Specify the default action posture: proactive (act first, report after) or conservative (ask before external actions). Base this on the domain -- engineering defaults to proactive, regulated/sensitive domains default to conservative. Record the reasoning.

### 3. State Taxonomy

Define what gets saved and loaded for this specific domain, organized into the 6 universal categories:

1. **Tool state**: What VCS, build, and external tool state matters? (Skip gracefully if not configured.)
2. **Task state**: What does "current task" look like in this domain?
3. **Artifact state**: What file types and paths does this domain produce?
4. **Decision state**: What kinds of decisions need to be preserved across sessions?
5. **Blocked state**: What external dependencies could block progress?
6. **Drift risk**: What could change externally between sessions?

Fill each category with domain-specific examples from GENESIS.md. If a category does not apply, write "N/A for this project" with a brief reason.

### 4. Memory Tier Selection

Select one of: Lite, Standard, Enterprise.

Decision criteria:
- Lite: Solo user, simple project, < 50 files of interest
- Standard: 1-5 people, medium complexity, multiple areas of concern
- Enterprise: Large team, complex domain, multiple sub-areas with their own indexes

Write a 2-3 sentence justification referencing the user's team size, project complexity, and information density from GENESIS.md.

Specify the initial memory structure (directories and files to create in Pass 4).

### 4b. Directory Structure Preview

Generate a complete visual folder tree showing every directory and file that will
be created. This tree is presented to the user during architecture confirmation
(pipeline step 5) so they can see exactly what their environment will look like
before generation begins.

**Construction rules:**
1. Derive the tree from the Component Manifest (every file listed must appear).
2. Add directories from the Memory Tier structure (Docs/Areas/, _working/, etc.).
3. Add directories from active patterns (Inbox/Outbox for Pattern E, Brand/ for
   brand sub-pattern, Entities/ for Pattern B, etc.).
4. Group by purpose with inline comments explaining each top-level section.
5. Use standard tree notation (├──, └──, │).

**Annotation style:**
- Top-level directories get a brief comment: `# Core assistant configuration`
- Files that are always loaded get marked: `(always loaded)`
- Files excluded from VCS get marked: `(gitignored)`
- Directories the user interacts with directly get marked: `(your workspace)`

**Tier-specific structure:**

Lite (solo, simple):
```
project-root/
├── CLAUDE.md                          # (always loaded)
├── .claude/
│   ├── rules/                         # 3-5 rule files (always loaded)
│   └── skills/                        # Commands you can use
├── .claudeignore
├── settings.json
└── Docs/
    ├── index.md                       # (always loaded)
    ├── GETTING_STARTED.md
    └── _working/                      # (gitignored)
        ├── state/
        └── retro/
```

Standard (small team, medium complexity):
```
project-root/
├── CLAUDE.md                          # (always loaded)
├── .claude/
│   ├── rules/                         # 5-8 rule files (always loaded)
│   ├── agents/                        # Specialist assistants
│   └── skills/                        # Commands you can use
├── .claudeignore
├── settings.json
├── Docs/
│   ├── index.md                       # (always loaded)
│   ├── GETTING_STARTED.md
│   ├── Areas/                         # Project knowledge by topic
│   ├── Decisions/                     # Why we chose X over Y
│   ├── Environment/                   # Generator metadata
│   └── _working/                      # (gitignored)
│       ├── state/
│       ├── sessions/
│       └── retro/
```

Enterprise (large team, complex domain):
```
project-root/
├── CLAUDE.md                          # (always loaded)
├── .claude/
│   ├── rules/                         # 8-10 rule files (always loaded)
│   ├── agents/
│   └── skills/
├── .claudeignore
├── settings.json
├── Docs/
│   ├── index.md                       # (always loaded)
│   ├── GETTING_STARTED.md
│   ├── Areas/                         # Sub-indexed by topic
│   │   ├── <area>/
│   │   │   ├── index.md
│   │   │   └── [topic pages]
│   ├── Decisions/
│   ├── Roles/                         # Per-role CLAUDE.local.md templates
│   ├── Environment/
│   └── _working/                      # (gitignored)
```

Start from the tier template, then overlay active patterns. The final tree
in ARCHITECTURE.md must reflect the EXACT set of files and directories that
will be generated -- no more, no less.

**User-facing presentation guidance:**
When the orchestrator presents this tree to the user, it should:
- Show the tree with annotations
- Highlight which directories are for the assistant vs. for the user
- Explain any directories that might be unfamiliar (e.g., _working/)
- Ask: "Does this structure work for you? Want to add, remove, or rename anything?"
- If the user requests changes, update the component manifest and tree to match

### Environment Complexity Decisions

Read the Setup Tolerance section from GENESIS.md for the user's general
inclination (lean simple / no preference / lean full-featured). Use this to
calibrate recommendations, but do NOT treat it as a binding decision.

For every recommendation that adds an external dependency (MCP server, plugin,
third-party tool install, automated pipeline), generate a complexity decision
entry in the architecture. Each entry must include:

1. **What it adds**: the specific capability or improvement (one sentence)
2. **What it costs**: install steps, configuration, ongoing maintenance (one sentence)
3. **Simpler alternative**: what the user gets without it and what degrades
4. **Recommendation**: include or skip, based on intake signals and inclination

The orchestrator presents these decisions to the user during architecture
confirmation (pipeline step 5). The user accepts or rejects each individually.
After user decisions, the architect records the final choices.

**Calibration by inclination**:
- Lean simple: default recommendation is "skip" unless benefit is compelling.
  Always show the simpler alternative prominently.
- No preference: recommend based on benefit/effort ratio. Prefer lighter
  alternatives when they cover 80%+ of the need (e.g., `gh` CLI over GitHub
  MCP, direct file access over Obsidian MCP).
- Lean full-featured: default recommendation is "include" for all applicable
  tools. Still show alternatives so the user can opt out.

**Common trade-offs to evaluate** (generate only those relevant to the project):
- MCP servers vs. built-in tools + CLI
- Third-party memory plugins vs. markdown wiki + /state-save
- Vector DB / semantic search vs. Glob/Grep
- Pandoc (formatted output) vs. markdown-only output
- Automated file pipelines (Inbox/Outbox) vs. manual file handling
- Browser automation MCP vs. manual browser + `gh` CLI
- PKM MCP server vs. direct file read/write to vault
- AI ecosystem tool integrations vs. manual use of those tools

Write a `## Environment Complexity` section to ARCHITECTURE.md with:
- User's stated inclination from intake
- Decision table (one row per external dependency recommendation)
- Column: Component | Benefit | Setup Cost | Simpler Alternative | Recommendation
- Status: in interactive mode mark PENDING until step-5 approval. In preset/automated
  mode (no per-trade-off confirmation step ran) stamp `Auto-confirmed (preset mode)`
  instead. NEVER leave a PENDING marker the generator would silently bake in -- the
  generator must refuse to act on any row still marked PENDING.

### Token Optimization

Read the Token Efficiency Priority section from GENESIS.md (default: balanced if
not specified). Write a `## Token Optimization` section to ARCHITECTURE.md with:

- **Efficiency tier**: cost-conscious / balanced / quality-first
- **Model override policy**: Whether all agents default to Sonnet (cost-conscious),
  standard mixed selection (balanced), or Opus-available (quality-first)
- **Compaction threshold**: 85% (cost-conscious) or 95% default (balanced/quality-first)
- **.claudeignore aggressiveness**: aggressive (cost-conscious), standard (balanced),
  minimal (quality-first) -- with domain-specific pattern lists
- **RTK recommendation level**: full setup (cost-conscious), mention (balanced),
  omit (quality-first)
- **Agent consolidation notes**: For cost-conscious, identify agents whose roles
  overlap and could be merged (e.g., explorer into debugger, reviewer functions
  into planner). For balanced/quality-first, use the standard roster.
- **CLAUDE.md line target**: 150 (cost-conscious), 200 (balanced), 250 (quality-first)

This section informs Pass 1 (settings.json, .claudeignore, CLAUDE.md) and Pass 5
(GETTING_STARTED.md cost monitoring section).

### 5. settings.json Specification

Define the complete permissions configuration:

**Allow rules**: Start with the base permissions (Read all, Write/Edit Docs and .claude, WebSearch, WebFetch). Add ecosystem-specific permissions based on GENESIS.md:
- Language-specific Bash commands (npm, pip, cargo, dotnet, etc.)
- Build commands
- Test commands
- VCS commands (git, p4, etc.)
- Any CLI tools mentioned in External Services

**Deny rules**: Start with base deny rules (.env, secrets, sudo, rm -rf /). Add domain-specific deny rules:
- Destructive VCS operations (force push, branch delete)
- Production database access (if applicable)
- Any operations the user marked as "never do without asking"

**Sandbox configuration**: Recommend auto-allow scope with appropriate boundaries.

**Autocompact**: Only include CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE if the
project genuinely has very large context needs (many large files read per
session, complex multi-system codebases). When included, use 85 -- never
lower. Lower values (like 70) cut sessions too short. For most projects,
omit the setting entirely and let the default (95) apply.

**Agent Teams** (required in every environment): Always include
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: "1"` in the env block. The orchestrator
rule must include a decision matrix for choosing between sequential subagents,
parallel subagents, and agent teams based on task characteristics.

**Hook configuration**:
- REQUIRED -- self-learning trigger hook (InstructionsLoaded, preferred over
  SessionStart): counts `Docs/_working/retro/` entries and recommends `/update` at
  threshold. The self-learning rule is a core component in EVERY environment, so this
  hook is always in the Pass-1 manifest -- the rule is logging-only without it
  (validator check 26 FAILs otherwise). Template: hooks-template.md "InstructionsLoaded:
  Self-learning trigger" (bash + PowerShell variants).
- REQUIRED -- PreCompact auto-save hook.
- Recommend only when the GENESIS workflow warrants: PostToolUse verification
  (tests/lint after edits), PreToolUse protection (binary/PII gates), Stop self-review
  (software/game dev). Do not over-hook.

**Fast mode configuration** (when cost-conscious or balanced tier):
- `"fastModePerSessionOptIn": true` -- requires per-session opt-in, prevents persistent
  cost increases. Required for cost-conscious tier; recommended for balanced tier.

**MCP Tool Search** (when 3+ MCP servers):
- `ENABLE_TOOL_SEARCH` in env block with recommended threshold (e.g., `"auto:5"`)
- Ensure all MCP server configs include an `instructions` field for accurate tool selection

**Status line** (when complex project or large codebase):
- Document status line setup in GETTING_STARTED.md (not auto-generated -- requires
  platform-specific shell scripts). Tier-aware: cost-conscious shows cost+duration,
  balanced shows context health, quality-first omits unless requested.

### 6. Self-Learning Configuration

Define the friction categories to track. Always include the base categories:
- FRICTION, WIN, CORRECTION, PATTERN

Add domain-specific categories if warranted (e.g., SKILL_UNDERTRIGGER, SKILL_OVERTRIGGER, ROUTING_CORRECTION).

Define 3-5 cold-start seed entries based on common friction patterns for this domain. Each seed entry should be a known issue that many users in this domain encounter. Mark them as `[PATTERN] (pre-seeded)`.

Set bootstrapping thresholds: 2 entries for the first 30 days, 3 after. Pre-seeded patterns trigger improvement proposals on 1 matching real entry.

### 7. Context Pressure Thresholds

Define when context management actions trigger:

- Turn count threshold (default: 30)
- Delegation count threshold (default: 10)
- File read count threshold (default: 15)
- Proactive summarize: at 70% of thresholds
- Auto-save + prompt /clear: at 100% of thresholds

Adjust these defaults based on the domain's typical task size. Small tasks (knowledge work, quick fixes) can use lower thresholds. Large tasks (refactoring, research projects) may need higher thresholds.

Define domain-specific compaction preservation hints: what must survive compaction for this project.

### 8. Agent Roster

List every agent to generate, with:
- name (kebab-case)
- model (opus / sonnet / haiku) with reasoning
- tools list
- disallowedTools list (if any)
- maxTurns
- 1-2 sentence description of when the orchestrator should delegate to it
- Key responsibilities (3-5 bullets)

Model selection policy -- default to Opus for maximum quality:
- Opus (default): All agents unless there is a specific reason to deviate.
  This includes: planning, implementation, review, debugging, analysis,
  research, and any task involving code or reasoning.
- Haiku (rare exception): Only when ALL of these are true: (1) the task is
  a simple lookup or file search with no reasoning required, (2) quality
  difference vs Opus is negligible, (3) speed is the primary concern.
- Sonnet: Avoid. Use Opus instead for better quality.

Do not over-generate agents. Each agent must serve a distinct, identifiable need from GENESIS.md. If the user's workflow can be served by 2-3 agents, do not generate 6.

### 9. Skill Roster

List every skill to generate, with:
- name (kebab-case)
- description (following the pattern: [What it does]. [When/triggers with 3+ phrases]. [Negative triggers if ambiguity risk].)
- context: fork
- allowed-tools list
- Whether it needs scripts/ or references/ subdirectories
- Key capabilities (3-5 bullets)

Core skills (always generated): state-save, state-load, update, health-check.
Optional skills: based on GENESIS.md needs (build, review, deploy, etc.).

### 10. MCP Server Suggestions

**Complexity decision required**: Every MCP server recommendation must have a
corresponding entry in the Environment Complexity decision table (benefit,
setup cost, simpler alternative). The user approves each during step 5.

**CRITICAL**: Only recommend MCP servers listed in the verified MCP registry in
`Docs/Templates/References/tool-registry.md` (section "Verified MCP Servers").
Do NOT invent, guess, or hallucinate MCP server packages. If a user mentions an
external service (e.g., Google Workspace, Slack, Jira) that has no verified MCP
server in the registry, do NOT suggest an MCP integration for it. Instead, note
it as "No verified MCP server available -- use browser/API/export workflow."

For each verified MCP server recommended:
- Server name and registry ID
- Install command (from registry)
- Which agents/skills would use it
- One-line justification (why this is worth the setup for this project)

If no external services were mentioned or none match verified servers, write
"No MCP servers recommended."

### 10b. Recommended Plugins (Anthropic Official Skills)

**Complexity decision required**: Each recommended plugin must have a
corresponding entry in the Environment Complexity decision table. Plugins are
optional installs, so frame as "available if you want it" not "required."

Canonical source: `Docs/Templates/References/tool-registry.md` (categories AP, BA, SD).
Match GENESIS.md signals to official Anthropic plugin collections from
`github.com/anthropics/skills`. These are installed via the marketplace
system, not statically copied. Recommend only plugins with clear signal match.

Matching rules:
- Office documents (Excel, Word, PowerPoint, PDF) -> `document-skills`
- Frontend/web development or web testing -> `example-skills`
- Building MCP servers -> `example-skills`
- Brand/design guidelines -> `example-skills`
- Internal communications -> `example-skills`
- Claude API/SDK development -> `claude-api`
- User wants to create custom skills -> `example-skills` (skill-creator)
- Complex codebase, 50k+ lines -> mention `/batch` bundled skill (no install needed)
- Frontend/web dev, testing, web scraping -> Playwright CLI (`npm i -g @playwright/cli`)
- Authenticated browser workflows (logged-in sites) -> Claude in Chrome
- Performance profiling, Core Web Vitals -> Chrome DevTools MCP
- Browser automation without shell access -> Playwright MCP (fallback only)

For each recommended plugin, write:
- Plugin collection name
- Which specific skills are relevant (not the entire collection)
- Install commands (marketplace add + plugin install)
- Why it matches (which GENESIS.md signal triggered it)

If no signals match, write "No official plugins recommended." Do NOT
recommend plugins speculatively. The user can always install them later.

Bundled skills (/code-review, /batch, /debug, /claude-api) do not need
installation. Mention relevant ones in the architecture for inclusion
in GETTING_STARTED.md.

### 10c. Persistent Memory Plugins (Third-Party)

**Complexity decision required**: Memory plugins must have a decision table
entry. The built-in markdown wiki + /state-save is always the simpler
alternative. Only recommend when context loss frustration is explicitly reported.

Canonical source: `Docs/Templates/References/tool-registry.md` (category PM).
When GENESIS.md signals suggest the built-in memory system may be insufficient,
recommend a third-party memory plugin as an optional enhancement. Signals:
- Multi-session projects where the user reports context loss between sessions
- Large codebases (1000+ files) with complex architectural decisions
- Teams sharing context across developers
- User explicitly mentions "Claude keeps forgetting" or similar frustration

Matching rules (recommend ONE, not multiple):
- Node.js or non-coding project, wants visual UI -> Synabun
- Heavy coding, long sessions, context limit issues -> claude-mem
- Python project or multi-agent pipeline -> mcp-memory-service

Write in the Recommended Plugins section:
- Plugin name and one-sentence purpose
- Install/setup summary (MCP registration command)
- Hook conflict notes if the environment uses the same hook events
- "Optional enhancement" framing -- never a requirement

If no memory plugin signals are present, omit entirely. The generated
environment's /state-save and markdown wiki are sufficient for most projects.

### 11. .claudeignore Patterns

List file patterns to ignore, based on the project's ecosystem:
- Build artifacts
- Dependencies (node_modules, venv, etc.)
- Binary assets (if applicable)
- Generated files
- Secrets and credentials

### 12. Output Style

If the domain benefits from multiple output styles (e.g., executive summary vs. technical detail for knowledge work), specify the styles to generate. Otherwise, write "Default output style sufficient."

### 13. Special Patterns

The architect must check GENESIS.md for these patterns and apply corresponding architectural decisions. If a pattern is detected, add the relevant components to the component manifest and architecture sections.

## Pattern Definitions

### Pattern A: Data Classification (Sensitive/Regulated Data)

Trigger: GENESIS.md mentions sensitive data, client information, student records, patient data, PII, PHI, FERPA, HIPAA, attorney-client privilege, financial records requiring confidentiality, or any "never store/display" constraints.

Generate:
- A `sensitive-data.md` rule file defining:
  - Data categories present in this project (PII, PHI, financial, legal, etc.)
  - Handling rules per category (what can be stored in memory, what must be anonymized, what must never appear in logs)
  - Memory isolation requirements (per-client, per-case, per-student folders if applicable)
  - Compaction hints: warn that sensitive data may be in context; preserve anonymization decisions
- Add deny patterns to settings.json for writing sensitive data to shared/public locations
- Add a constraint to CLAUDE.md: "Never include [data type] in memory files. Use identifiers only."
- Add a routing entry: "Handle sensitive data question" -> answer directly with data classification guidance
- **If GENESIS.md Sensitive Data Handling section specifies "deterministic hooks" enforcement**:
  - Add PreToolUse PII content gate hook to settings.json hooks section
  - Add `.claude/hooks/pii-scan.sh` (or `.ps1` on Windows) to component manifest (Pass 1)
  - Add `.claude/hooks/pii-patterns.conf` with domain-specific regex patterns to component manifest (Pass 1)
  - Optionally add UserPromptSubmit input screening hook
  - Add PostToolUse audit trail hook if regulatory compliance requires action logging
  - Document hook setup and pattern customization in GETTING_STARTED.md requirements
  - Reference: hooks-template.md Compliance section for implementation patterns

### Pattern B: Repeatable Engagement / Template Workflow

Trigger: GENESIS.md mentions repeating the same process for different clients, students, cases, projects, or entities. Key phrases: "repeatable," "for each client," "per case," "onboard new [entity]," "same process different [entity]."

Generate:
- A `/new-engagement` skill (or domain-appropriate name like `/new-client`, `/new-case`, `/new-student`) that:
  - Creates a per-entity subfolder in Docs/Entities/<EntityName>/
  - Copies template documents from Docs/Templates/
  - Initializes a deliverable checklist for the entity
  - Records the entity in a master tracking file (Docs/Areas/entity-tracker.md)
- Template documents in Docs/Templates/ (created in Pass 4) based on the workflow described in GENESIS.md
- A routing entry: "Start new [entity type]" -> /new-engagement skill
- Memory structure using the multi-entity variant (Entities/ subfolder pattern)

### Pattern C: Project Management / Deliverable Tracking

Trigger: GENESIS.md mentions deadline tracking, deliverable management, milestone tracking, project phases, or task lists that need persistent tracking across sessions.

Generate:
- A deliverable tracking document: `Docs/Areas/deliverables.md` with columns: Item, Status, Due Date, Owner, Notes
- Routing entries for:
  - "What is overdue / what is next" -> answer directly (read deliverables.md)
  - "Update status of X" -> answer directly (edit deliverables.md)
  - "Show project status" -> answer directly (summarize deliverables.md)
- State-save must capture: deliverable statuses, current phase, next milestones
- If multi-phase project: include phase markers in deliverables.md and routing entries for "move to next phase"

### Pattern D: Binary File Protection (Generalized)

Trigger: GENESIS.md mentions working with images, videos, audio, design files (PSD, AI, Figma), or any non-text files that the assistant should not edit. This is SEPARATE from the Game Dev profile's binary protection -- it applies to any domain with binary files.

Generate:
- .claudeignore patterns for the specific binary file types mentioned
- A PreToolUse hook blocking Write/Edit on the relevant binary extensions (same pattern as the game development profile but with domain-appropriate extensions)
- A routing entry: "Change/edit [binary file type]" -> answer directly with step-by-step instructions for the appropriate tool (Figma, Photoshop, video editor, etc.)
- A rule in the autonomy file: "Do not edit [file types]. If a change requires editing these files, describe the exact steps in the appropriate application and stop for the user."

### Pattern E: File Processing Pipeline

**Complexity decision required**: Outbound tools (Pandoc, python-pptx) and
Inbox/Outbox scaffolding each need a decision table entry. Inbound (MarkItDown,
single pip install) is lightweight enough to include without a decision entry.
Simpler alternative for outbound: markdown-only output, user converts manually.

Trigger: GENESIS.md indicates the user works with non-text files (office documents, spreadsheets, PDFs, presentations, media) OR needs to produce formatted document output. Detection signals:
- Office document formats mentioned (.docx, .xlsx, .pptx, .pdf)
- Keywords: "reports", "proposals", "briefs", "presentations", "deliverables"
- Data files requiring conversion or processing
- Output intended for external audiences (clients, boards, stakeholders)
- Data processing probe flagged file format needs during intake

**INBOUND (always the same -- no decision needed):**
- MarkItDown (`pip install 'markitdown[all]'`) is ALWAYS the inbound converter
- Converts office docs, PDFs, spreadsheets, presentations -> Markdown for Claude to process
- Also available as MCP server (markitdown-mcp) for seamless integration
- If MCP server variant is used, add to settings.json MCP config

**OUTBOUND (decision tree -- architect follows top to bottom, first match wins):**

```
IF user produces presentations (.pptx):
    -> Pandoc RECOMMENDED (exe install)
    -> python-pptx is NOT practical (100+ lines per deck vs ~20 lines Markdown + Pandoc)

ELIF user produces formatted documents for external audiences:
    -> Pandoc RECOMMENDED (exe install)
    -> Professional formatting, custom templates, one-command conversion

ELIF user produces PDF reports:
    -> Pandoc RECOMMENDED (exe install)
    -> Needs LaTeX engine or wkhtmltopdf for best results

ELIF user produces basic internal .docx (notes, drafts):
    -> python-docx SUFFICIENT (pip only)
    -> Basic headings, tables, images -- no exe install needed

ELIF user only needs Excel output:
    -> openpyxl (pip) + ImportExcel (PowerShell module) SUFFICIENT
    -> No Pandoc needed

ELIF user only produces text/markdown:
    -> No outbound tools needed
```

**DUAL-MODE (for mixed environments):**
When the user does BOTH quick analysis AND formatted deliverables, include:
- A routing rule selecting low-context mode (MarkItDown -> text output) for analysis tasks
- A routing rule selecting high-fidelity mode (MarkItDown -> Pandoc -> formatted output) for deliverable tasks
- The same environment supports both -- tool selection happens per interaction, not globally

**SCAFFOLDED DIRECTORIES:**
When file processing is active, add to the environment's directory structure:
- `Inbox/` -- User drops files here for Claude to process
- `Outbox/` -- Claude places converted/generated files here for user
- `Data/` -- Working data files (intermediate processing, reference data)

Include a routing rule or skill that watches `Inbox/` and auto-processes new files.

Generate:
- An `Inbox/README.md` explaining: drop files here for processing, supported formats, what happens automatically
- An `Outbox/README.md` explaining: find generated output here, naming conventions, cleanup policy
- A routing entry for file processing requests that selects the correct mode (analysis vs. deliverable)
- Tool permissions in settings.json matching ONLY the selected tools (do not grant Python permissions if only PowerShell tools are used)
- If Pandoc is recommended: setup instructions in GETTING_STARTED.md (download link, PATH config, verification command)
- If markitdown-mcp is used: MCP server config block in settings.json
- Reference `Docs/Templates/References/tool-catalog.md` for detailed tool specifications

**BRAND GUIDANCE SUB-PATTERN (within Pattern E):**

Detection triggers (in addition to Pattern E's existing triggers):
- GENESIS mentions "brand", "style guide", "design standards", "corporate identity", "templates"
- GENESIS mentions producing documents for external audiences AND has organizational context
- Brand requirements probe was flagged during intake

When brand guidance is active, generate the following additional components:

**1. Brand/ directory structure:**
```
Brand/
  Templates/        # User drops branded .docx/.pptx templates here
  Guidelines/       # User drops brand guide PDFs/docs here
  brand-rules.md    # Auto-generated: extracted brand rules (persistent)
  README.md         # Explains what goes here and how it works
```

Add these to the component manifest (Pass 4 -- Infrastructure) alongside the Inbox/Outbox directories.

**2. brand-rules.md auto-generation and auto-update workflow:**

The generated environment must include a mechanism (skill or routing rule) that:
- On first run or when triggered: scans Brand/Guidelines/ and Brand/Templates/
- Converts guideline documents via MarkItDown
- Analyzes content for: tone/voice, terminology preferences, color palette, font preferences, required sections/headers, legal disclaimers, logo/header placement rules, formatting conventions
- Writes/updates Brand/brand-rules.md with extracted rules in a structured format

Auto-update mechanism (critical):
brand-rules.md must include a metadata section tracking source files:
```markdown
## Source Tracking
Last Generated: YYYY-MM-DD HH:MM
Sources:
- Guidelines/brand-guide.pdf (modified: YYYY-MM-DD HH:MM)
- Templates/company-report.docx (modified: YYYY-MM-DD HH:MM)
- Templates/company-deck.pptx (modified: YYYY-MM-DD HH:MM)
```

Before any quality-mode output (deliverables, external-facing documents), the assistant checks:
- Are there files in Brand/Guidelines/ or Brand/Templates/ NOT listed in Source Tracking?
- Are any listed files' modification dates newer than the Last Generated date?
- If either condition is true: re-analyze changed/new files, update brand-rules.md, then proceed

This makes brand-rules.md self-maintaining -- the user drops updated brand assets and the rules refresh automatically on next use.

**3. Brand-aware Pandoc commands:**
When brand templates exist in Brand/Templates/:
- For .docx output: `pandoc output.md -o result.docx --reference-doc=Brand/Templates/<template>.docx`
- For .pptx output: `pandoc slides.md -t pptx -o deck.pptx --reference-doc=Brand/Templates/<template>.pptx`
- Template selection: match the template type to the output type (e.g., use a .docx reference doc for .docx output, .pptx for .pptx output)

**4. Brand-aware content generation:**
When brand-rules.md exists, the assistant should:
- Reference tone/voice rules when drafting content
- Use preferred terminology (not generic alternatives)
- Include required sections/headers as defined in the brand guide
- Add legal disclaimers where specified
- Follow formatting conventions (heading styles, list formats, etc.)

Add a routing entry: "Generate branded document / apply brand standards" -> check brand-rules.md freshness, re-extract if stale, then proceed with brand-aware generation.

### Pattern F: Codebase Mapping

Trigger: Game-development profile (always include). For software-development profile, include when 2+ of these signals are present:
- Project has multiple modules or packages (detected from GENESIS.md)
- GENESIS.md mentions 50+ source files or "large codebase"
- User mentions difficulty navigating existing code, finding classes, or keeping track of project structure
- Software-development profile with medium or large codebase indication

Generate:
- A `/map-codebase` skill that scans the source tree, extracts declarations, classifies them into areas, and updates area pages. Uses Glob/Grep/Read only (no Bash) because classification requires LLM reasoning about inheritance, naming, and domain semantics.
- A routing entry: "Map codebase / scan source files / update area maps" -> /map-codebase skill, fallback: explorer agent
- A mapping preflight note in the orchestrator rule: before debug, feature, refactor, or performance tasks, check if relevant area maps exist and are fresh; suggest running /map-codebase if area pages contain placeholder content or are stale (>30 days old)
- Reference template: `Docs/Templates/Skills/map-codebase.md`

### Pattern G: Pipeline Skills (Multi-Tool Workflows)

Trigger: GENESIS.md describes a workflow chaining 2+ external tools in sequence
where the output of one tool feeds into the next. Key signals:
- "I use [tool A] to get data, then [tool B] to process it"
- Repeatable research or content pipelines
- Workflow description mentions 3+ named tools used together
- User is intermediate+ (beginners need simpler skills)

Generate:
- Individual tool-wrapper steps within a single pipeline skill (NOT separate skills)
- Each step: invoke tool via Bash, parse output, format for next step
- Step 1 always: verify all required tools are installed
- Working directory: `Docs/_working/pipelines/<skill-name>/` for intermediate files
- Error handling: if step N fails, report what completed and what's needed
- A routing entry for the workflow trigger phrases

Also generate: Bash permissions for each CLI tool in settings.json.

Do NOT generate separate skills for each tool step (violates 3.6 composability
intent). The pipeline is one skill with internal sequential steps.

If the workflow also involves a PKM tool (Obsidian, Logseq), add a final step
that formats output for the user's PKM conventions and writes to their vault.

### Pattern H: PKM Integration

Trigger: GENESIS.md mentions Obsidian, Logseq, Notion local, or "personal
knowledge base" with a vault/workspace path.

Generate:
- Vault path in settings.json allowed paths (Read + Write permissions)
- A `pkm-conventions.md` rule file documenting the user's folder structure,
  tag conventions, and frontmatter format
- A `/capture-knowledge` skill that formats findings as PKM-compatible markdown
  (with frontmatter, tags, wiki-links per the user's conventions)
- A routing entry: "Add to my notes / save to knowledge base" -> /capture-knowledge
- State-save integration: include vault path in artifact state tracking

If the user also has a PKM MCP server (obsidian-mcp, etc.), configure it in
.mcp.json instead of direct file access.

### Pattern I: AI Capability Extension

**Complexity decision required**: Each AI ecosystem tool needs a decision table
entry. These tools are chosen during intake (not speculative), so the decision
is about confirming the setup cost is acceptable, not whether the tool is wanted.

Trigger: GENESIS.md "AI Ecosystem Extensions" section lists capability gaps
and chosen tools (image generation, video generation, local inference, audio,
etc.). This section is populated during intake when the Harness Generator identifies
capabilities Claude can't do natively.

For each chosen tool, generate based on its integration type:

**MCP integration** (ComfyUI, ModelsLab, OllamaClaude, obsidian-mcp):
- Add MCP server config to .mcp.json (or settings.json mcpServers)
- Add fully qualified tool permissions to settings.json
- Add routing entries for the capability ("generate an image" -> use ComfyUI tools)

**CLI wrapping** (Ollama CLI, Bark, Coqui, ffmpeg):
- Generate a wrapper skill (using Pattern G pipeline structure if multi-step)
- Add `Bash(<tool> *)` permission to settings.json
- Add routing entry and install verification step in the skill

**API integration** (DALL-E, ElevenLabs, Nano Banana, Kling, Runway):
- Generate an API skill that makes HTTP calls via Bash (curl)
- API keys in settings.local.json (NEVER settings.json)
- Add routing entry for the capability
- Include rate limiting and error handling in the skill

**For all types**:
- Document setup (install commands, API key setup) in GETTING_STARTED.md
- Add to the routing table with domain-specific trigger phrases
- If user chose multiple tools for same capability (local + cloud), add
  routing logic: "draft/iterate" -> local, "final/publish" -> cloud

Consult `Docs/Templates/References/tool-registry.md` for specific tools,
install commands, and matching rules per category.

### Pattern J: Adverse decisions about people (high-stakes)

Trigger: agents will score, rank, screen, evaluate, or recommend decisions ABOUT
IDENTIFIABLE PEOPLE -- hiring, admissions, lending/credit, tenant screening,
performance review, benefits eligibility. (Bundled domains: hiring-pipeline.)
These are legally high-risk (US EEOC/Title VII/ADA/ADEA, NYC Local Law 144 +
Illinois AIVIA for hiring, ECOA/FCRA for credit, EU AI Act "high-risk").

Generate:
- A REQUIRED `adverse-decision-rule.md` (template in `Optional/`) pinning:
  decision-SUPPORT-only positioning, human review of every adverse action (no
  automated rejection/screen-out), job/decision-relatedness of criteria + a
  disparate-impact caution, bias-engineered scoring (fix rubric first; exclude
  bias-correlated fields; independent absolute scoring; per-score rationale).
- `sensitive-data-rule.md` REQUIRED (the people's data is Restricted): exclude
  subject identifiers/scores/decision-reasons from retro/state/PreCompact (opaque
  per-case label), BUT retain the structured decision rationale in the per-case dir
  as the defensible record (retention per jurisdiction).
- A Safeguards section in the profile/CLAUDE.md naming the governing law, plus a
  disclaimer ("draft for human review -- not legal advice; verify compliance + any
  required bias audit / subject notice with counsel") on every decision deliverable.
- Optional deterministic PreToolUse gate: block writes to a decision/adverse-action
  artifact lacking the disclaimer or containing a verdict/ranking without a recorded
  human reviewer.

### Pattern K: Authorized security testing (offensive)

Trigger: agents will scan, probe, fingerprint, or build exploits/PoCs -- security
audit, pentest, vulnerability assessment, red-team. (Bundled domains: security-audit.)

Generate:
- A REQUIRED `authorization-scope-rule.md` (template in `Optional/`) pinning:
  authorized-only posture; a recorded in-scope/out-of-scope + authorization artifact
  before active testing; the always-loaded no-exploitation/no-exfiltration/
  no-destructive-payload constraint; responsible disclosure; and finding provenance
  (report only tool-confirmed or retrieved CVEs, never recalled-from-memory).
- `sensitive-data-rule.md` REQUIRED (discovered secrets/PII/evidence are Restricted;
  redact when summarizing scanner output; keep secrets/PoC out of retro/state/PreCompact).
- Optional deterministic PreToolUse gates: (a) authorization gate -- network-touching
  scanners gated to an authorized-host allow-list (settings.local.json); (b)
  finding-integrity gate -- a reported CVE token must trace to a scanner run or
  retrieval. Deterministic by default for live/network targets; advisory for local
  source-only audits.

## Hub Architecture (Multi-Area Mode)

Activated when the orchestrator invokes the architect with `mode: hub` and a
HUB_GENESIS.md path. Produces a shared-layer architecture at the parent plus
one full architecture per work area.

### What lives at the parent (HUB_ARCHITECTURE.md)

The parent layer contains only what every area shares:

- Parent CLAUDE.md (thin orchestrator, 80 lines max; lists work areas with
  one-line descriptions; Claude Code discovers child CLAUDE.md files by
  walking the tree)
- Shared rules: vocabulary, autonomy, cross-area routing
- Shared skills and agents: only components used unchanged by every area
  (e.g., a /state-save skill identical across areas; a reviewer agent that
  works for any area's code)
- Shared MCP servers declared once in parent settings.json
- Shared permissions and PreCompact hook in parent settings.json
- Work-area registry: list of `<area-slug>` values with one-line descriptions

### What lives per area (each per-area ARCHITECTURE.md)

Each work area is a full environment *minus* anything the parent already
provides. A per-area ARCHITECTURE.md contains its own Component Manifest,
Routing Table, State Taxonomy, Memory Tier, Directory Structure, etc. --
same sections as a single-environment ARCHITECTURE.md.

Per-area ARCHITECTURE.md additionally includes a `## Parent Overrides`
section listing any parent components the area supersedes. Format:

```
| Parent component | Area component | Reason |
|---|---|---|
| shared /state-save | area-specific /state-save | Policy area needs different state taxonomy |
```

### Override mechanism

When a per-area component overrides a parent component, the generated file
includes `overrides: <parent-component-name>` in its frontmatter. At runtime,
Claude Code's hierarchical loading means the child naturally wins for its own
scope; the override declaration makes the supersession explicit for the
validator.

Without an override declaration, component name collisions across
parent + areas are a validation error.

### Cumulative line budgets

Hub mode tightens budgets because files stack:

| Budget | Limit | Note |
|---|---|---|
| Parent CLAUDE.md | 80 lines | Thin orchestrator, registry, shared routing |
| Per-area CLAUDE.md | 170 lines | Full area instructions |
| Cumulative CLAUDE.md (parent + any one child) | 250 lines | Hard limit |
| Parent rule files | 120 lines each | Same as single mode |
| Per-area rule files | 120 lines each | Same as single mode |

The architect must verify cumulative budgets before writing. If the user's
shared basics would push the parent beyond 80 lines, the architect promotes
the parent into a "fat hub" mode: parent CLAUDE.md stays under 80 but shared
rules absorb the overflow (they are loaded only when referenced).

### Hub generation manifest

The hub HUB_ARCHITECTURE.md manifest uses the pass column `shell` for parent
files. Each per-area ARCHITECTURE.md uses passes 1-5 as in single mode.
The generator runs in this order:

1. Parent shell pass (once)
2. For each work area in the registry: passes 1, 2, 3, 4, 5

### Hub templates

For the shell pass, the component-generator reads:

- `Docs/Templates/Core/parent-claude-md.md` for the thin parent orchestrator
- `Docs/Templates/Core/settings-json.md` for parent settings (shared subset only)
- Shared rule templates from `Docs/Templates/Core/` (autonomy-rule, etc.)
  only for rules designated shared in HUB_ARCHITECTURE.md

The intake step (orchestrator) writes:

- `Docs/Templates/Core/hub-genesis.md` as the structure reference when
  composing HUB_GENESIS.md

### Hub-specific quality gates

Run these in addition to the single-mode gates:

- Every entry in the work-area registry has a corresponding
  `<target>/<area-slug>/Docs/Environment/ARCHITECTURE.md` file written
- No component name collides across parent + areas unless declared in
  `## Parent Overrides`
- Cumulative CLAUDE.md budget: parent + longest child < 250 lines
- Cross-area references in any per-area routing table resolve through the
  parent routing table, not direct sibling file paths (areas must not know
  about each other's internal file structure)
- Parent settings.json permissions are a subset of the union of permissions
  each area would need (no parent-only permissions that no area uses)

### HUB_ARCHITECTURE.md output format

```markdown
# Hub Architecture

Generated: YYYY-MM-DD
Based on: HUB_GENESIS.md at <path>
Target: <target_path>
Work areas: <count>

## Work Area Registry
| Area slug | Display name | One-line description | Profile | Per-area ARCHITECTURE.md |
|---|---|---|---|---|
| policy | Policy Framework | ... | knowledge-work | <target>/policy/Docs/Environment/ARCHITECTURE.md |

## Shared Component Manifest
[Table: every parent file, pass column = "shell", reference template]

## Shared Routing Table
[Cross-area routing: "if request matches area X's vocabulary, suggest switching to that area"]

## Shared Rules
[Vocabulary, autonomy, cross-area routing -- what every area inherits]

## Shared Skills and Agents
[Only components identical for every area]

## Shared Settings
[Parent settings.json: shared permissions, MCP servers, PreCompact hook]

## Cumulative Budget Check
[Parent CLAUDE.md projected lines; each area's CLAUDE.md projected lines;
 cumulative for each area; any budget flags]
```

## Output Format

Write ARCHITECTURE.md with the following structure:

```markdown
# Environment Architecture

Generated: YYYY-MM-DD
Based on: GENESIS.md (Intake Path: <path>, Base Profile: <profile>)
Target: <target_path>

## Component Manifest
[Table mapping every file to pass and template]

## Routing Table
[Fully enumerated, domain-specific routing entries]

## State Taxonomy
[6 categories filled with domain-specific content]

## Memory Tier
[Selection + justification + initial structure]

## Directory Structure
[Visual folder tree with annotations -- presented to user for confirmation]

## Settings Specification
[Allow rules, deny rules, sandbox config, hooks]

## Self-Learning Configuration
[Categories, seed entries, thresholds]

## Context Pressure
[Thresholds + compaction hints]

## Agent Roster
[Each agent with full specification]

## Skill Roster
[Each skill with full specification]

## MCP Servers
[Recommendations or "none"]

## Recommended Plugins
[Matching official plugins from anthropics/skills or "none"]

## Ignore Patterns
[.claudeignore content]

## Output Styles
[Style specs or "default"]

## Environment Complexity
User inclination: [lean simple / no preference / lean full-featured]

| Component | Benefit | Setup Cost | Simpler Alternative | Recommendation |
|-----------|---------|------------|---------------------|----------------|
| [tool/server] | [what it adds] | [install + maintain] | [what you get without it] | Include / Skip |

Status: PENDING USER CONFIRMATION

## Token Optimization
[Efficiency tier, model override policy, compaction threshold, .claudeignore
aggressiveness, RTK recommendation level, agent consolidation notes, CLAUDE.md
line target]

## Special Patterns

Active patterns and their components:
- Pattern A (Data Classification): [ACTIVE/INACTIVE] -- [components if active]
- Pattern B (Repeatable Engagement): [ACTIVE/INACTIVE] -- [components if active]
- Pattern C (Project Management): [ACTIVE/INACTIVE] -- [components if active]
- Pattern D (Binary File Protection): [ACTIVE/INACTIVE] -- [components if active]
- Pattern E (File Processing Pipeline): [ACTIVE/INACTIVE] -- [tool selections, scaffolding choices]
  - Brand sub-pattern: [ACTIVE/INACTIVE] -- [Brand/ directory components if active]
- Pattern F (Codebase Mapping): [ACTIVE/INACTIVE] -- [/map-codebase skill, routing entry, preflight note]
```

## Quality Gates

Before writing the final ARCHITECTURE.md, verify:

1. Every file in the component manifest has a clear pass assignment (1-5).
2. The routing table has at least 10 domain-specific entries (not generic).
3. Each routing entry has a fallback chain.
4. All 6 state taxonomy categories are addressed (even if "N/A").
5. The agent roster does not exceed what GENESIS.md justifies.
6. Every agent has model, tools, disallowedTools, and maxTurns specified.
7. Every skill description has 3+ trigger phrases.
8. settings.json deny rules cover all operations the user marked as requiring approval.
9. The memory tier matches the stated team size and complexity.
10. Seed entries are domain-specific (not generic "context exhaustion").
11. If GENESIS.md mentions sensitive data, Pattern A components are in the manifest.
12. If GENESIS.md mentions repeatable workflows, Pattern B components are in the manifest.
13. If GENESIS.md mentions binary files outside of Game Dev profile, Pattern D is applied.
16. If Pattern F is active, verify /map-codebase skill is in the skill roster and the routing table includes a mapping entry.
14. If Pattern E active, verify tool selection matches intake signals (no over-provisioning -- do not include Pandoc if only Excel output is needed, do not include openpyxl if only presentations are needed).
15. If brand guidance sub-pattern is active, verify: Brand/ directory has README.md in the manifest, brand-rules.md template includes Source Tracking section, quality mode routing references brand assets.
17. Every MCP server in section 10 must have a matching entry in tool-registry.md "Verified MCP Servers". No invented/unverified MCP packages.
18. Directory Structure tree includes every file from the Component Manifest and every directory from the Memory Tier and active patterns. No file appears in the manifest without appearing in the tree.

## Anti-Overengineering

Design only what GENESIS.md justifies. If the user described a simple solo project, do not architect an enterprise-grade environment. If they did not mention external services, do not suggest MCP servers. Every component must trace back to a stated need or a best-practice requirement from the relevant topic file in Docs/AgentGuidelines/Topics/ (core components like state-save, health-check are always justified by best practice).

# Claude Harness Generator -- Overview

This document describes the project's goal, what it does, and how it works internally.

---

## Section 1: Goal

Setting up a Claude Code environment that works well for a specific project is a non-trivial task. A complete environment involves a CLAUDE.md orchestrator file, rule files for autonomy and context management, specialized agent definitions, skill definitions with trigger phrases, a settings.json with carefully scoped permissions and deny rules, memory structures, self-learning scaffolding, and onboarding documentation. Getting all of these pieces to work together -- without contradictions, orphan references, or bloated files that exhaust context -- requires knowledge that most users do not have and should not need to acquire.

The Claude Harness Generator solves this problem. It is a Claude Code project that, when run, interviews a user about their work and then generates a complete, tailored Claude Code environment for their project. It is designed for anyone using Claude Code, regardless of technical background or industry. A software developer building a Node.js API, a lawyer managing case research, a game developer working in Unreal Engine, and an accountant analyzing financial data all receive environments built for their specific domain, tools, and workflow.

The output is a full environment: CLAUDE.md with routing and orchestration, rule files, agent definitions, skill definitions, settings.json with permissions, a memory structure, self-learning infrastructure, and a plain-language getting-started guide. None of it is generic. Every component traces back to what the user said during intake.

The key insight behind the Harness Generator is that the right environment depends entirely on how someone works. Rather than shipping a one-size-fits-all template, the Harness Generator interviews the user -- asking about their project, tools, workflows, team size, pain points, and preferences -- then generates an environment matched to those answers. Starter profiles accelerate the common cases, but the system can build a fully custom configuration from scratch for any domain.

---

## Section 2: Functionality

### The /create pipeline

The primary command is `/create`. It launches a multi-stage pipeline that takes the user from a blank directory to a fully validated environment:

1. **Trigger and verification.** The `/create` skill asks for a target directory, verifies it exists and is writable, checks for existing Claude Code files, and writes a `CREATION_CONTEXT.md` state file.

2. **Intake.** The orchestrator asks the experience level and work-area shape, then presents starter profiles and conducts a customization interview (2-3 rounds of follow-up questions covering languages, frameworks, workflows, team size, external services, data handling, sensitive data, repeatable processes, output formats, and brand guidelines). Intake also offers a preset path (a slim base profile or a bundled domain profile -- fast) versus a custom path (the architect synthesizes a reusable DOMAIN_PROFILE.md -- more tokens and time, for long-term harnesses). The result is written to `GENESIS.md` in the target directory.

3. **Architecture design.** The environment-architect agent reads GENESIS.md and the knowledge base, then designs the complete architecture: a component manifest mapping every file to a generation pass, a domain-specific routing table with at least 10 entries, a 6-category state taxonomy, memory tier selection, settings.json specification, agent and skill rosters, self-learning configuration, context pressure thresholds, and more. It picks one of six named team-architecture patterns (Pipeline, Fan-out/Fan-in, Expert Pool, Producer-Reviewer, Supervisor, Hierarchical Delegation) and a Team/Subagent/Hybrid execution mode; in custom mode it also writes DOMAIN_PROFILE.md. This is written to `ARCHITECTURE.md`.

4. **Five-pass generation.** The component-generator agent is invoked five times, once per pass:
   - **Pass 1 -- Foundation:** CLAUDE.md, all rule files, settings.json, .claudeignore, hooks
   - **Pass 2 -- Agents:** All agent definition files
   - **Pass 3 -- Skills:** All skill definitions with progressive disclosure structure
   - **Pass 4 -- Infrastructure:** Memory scaffold, self-learning scaffold, state management templates
   - **Pass 5 -- Documentation:** GETTING_STARTED.md, VERSION.md, cross-reference verification

5. **Validation.** The environment-validator agent runs the validation checklist (see Docs/Templates/References/validation-guide.md -- the single source of truth) covering structural correctness (file references, frontmatter validity, JSON validity), routing and logic checks (routing coverage, state-save/load symmetry, contradictions), size and quality checks (line limits, cross-references, no role-setting prompts), and completeness checks (GETTING_STARTED.md, .claudeignore, intent behind rules). The validator also runs a Phase-0 drift audit and boundary-crossing checks. Critical failures trigger a fix-and-revalidate cycle (up to 2 retries).

6. **Summary.** The orchestrator presents what was generated, how to get started, and smoke test instructions (start the environment, send a greeting, try /state-save, try /health-check, ask a domain question, request a small task).

### Starter profiles and the domain library

Four slim base profiles cover the broad use cases (roughly 110-170 lines each, written to the format spec in `Docs/StarterProfiles/PROFILE_FORMAT.md`):

| Profile | Target audience |
|---------|----------------|
| **software-development** | Developers building web apps, APIs, CLIs, libraries, or services in Python, Node/TypeScript, Go, Rust, Java, or C# |
| **knowledge-work** | Researchers, lawyers, financial analysts, technical writers, and other document-centric professionals |
| **data-analysis** | Accountants, analysts, and anyone working primarily with structured data -- reporting, dashboards, spreadsheet analysis |
| **devops-infrastructure** | DevOps engineers, SRE teams, platform engineers managing cloud infrastructure, CI/CD, and reliability |

Each base profile is a functionally distinct way of working with AI (code gated by execution; cited prose gated by review; computed data gated by methodology checks; live-system mutations gated by blast-radius approval). Profiles are not copied verbatim -- they serve as starting points that the architect and generator adapt to the user's specifics.

Alongside the base profiles, the Harness Generator bundles 16 domain profiles in `Docs/DomainLibrary/` for narrower, ready-made starting points. `Docs/StarterProfiles/DOMAIN_REFERENCE.md` maps roughly 20 common domains to a recommended start point.

Intake offers two paths:

- **Preset** -- start from a base profile or a bundled domain profile. Fast; minimal tokens.
- **Custom** -- the architect synthesizes a reusable `DOMAIN_PROFILE.md` from the intake answers. More tokens and time, intended for long-term harnesses.

### Deep interview fallback

When no starter profile fits (or the user selects "none of these"), the intake-interviewer agent conducts a 5-stage deep interview:

1. **Project overview** -- domain, work type, scale, team, experience level
2. **Technical environment** -- languages, VCS, build system, external services, data processing needs, binary files (skipped for purely non-technical projects)
3. **Workflow** -- typical task flow, quality gates, pain points, repeatable processes, output formats, brand requirements
4. **Roles and constraints** -- desired specializations, hard constraints, sensitive data handling
5. **Preferences** -- communication style, autonomy level, documentation needs

Because the interviewer agent cannot talk to the user directly, it uses a question relay protocol: it writes pending questions to GENESIS.md, the orchestrator presents them to the user in plain language, writes the answers back, and re-invokes the agent. This cycle repeats up to 5 rounds.

### File processing pipeline

The the Harness Generator detects when users work with non-text files (office documents, spreadsheets, PDFs, presentations) or need to produce formatted output. When this pattern is detected, the generated environment includes:

- **Inbound conversion:** MarkItDown (always the same) converts office docs, PDFs, spreadsheets, and presentations into Markdown for Claude to process. Available as a pip package or MCP server.
- **Outbound conversion:** Pandoc for professional formatted output (.docx, .pptx, PDF), python-docx for basic internal documents, openpyxl or ImportExcel for Excel output. The architect selects only the tools justified by the intake -- no over-provisioning.
- **Directory scaffolding:** `Inbox/` (user drops files for processing), `Outbox/` (Claude places generated output), and `Data/` (working data files) directories with README files explaining usage.
- **Dual-mode routing:** For environments that need both quick analysis and formatted deliverables, routing rules select the appropriate mode per interaction.

### Brand guidance support

When the intake reveals that the user's organization has brand guidelines or document templates, the generated environment includes:

- A `Brand/` directory with `Templates/`, `Guidelines/`, and `brand-rules.md`
- An auto-update mechanism: before producing formatted output, the assistant checks whether brand assets have changed since the last analysis, re-extracts rules if needed, and applies them
- Brand-aware Pandoc commands using `--reference-doc` for branded .docx and .pptx output

### Other commands

- **/validate-environment** -- Validates an existing Claude Code environment against the same checklist used during generation. Produces a report with PASS/WARN/FAIL verdicts per check, then offers to create a fix plan for any issues found.
- **/upgrade-environment** -- Audits an existing environment against current best practices, interviews the user about pain points, and implements approved improvements (including single <-> multi-area hub shape conversions). Recommendations are tiered (quick wins / medium / large) so the user picks what to implement.
- **/update** -- Refreshes the Harness Generator's own knowledge base. Ingests any pending user-contributed documents from `Docs/ProvideKnowledge/` first, then searches Anthropic documentation for updates, and incorporates validated findings into the topic files in `Docs/AgentGuidelines/Topics/` with source attribution and tier classification. It also has a local-only mode (ingest `Docs/ProvideKnowledge/` without web research) triggered by phrasings like "process knowledge" or "I added docs".

### Work areas: one focused project vs. several

The Harness Generator supports two shapes, chosen during intake and reversible at any time via `/upgrade-environment`:

- **One focused area** -- a single environment in one directory. Everything in it shares context: one set of rules, one memory, one self-learning log. Right when the work is closely related: a single codebase, a research effort with multiple outputs, a novel plus its reference bible.
- **A set of separate work areas that share some basics** (internally: a *hub*) -- one environment per work area, each with its own `.claude/`, CLAUDE.md, memory, and state, all living as subfolders under a shared parent. The parent holds vocabulary, autonomy rules, and any shared skills/agents that every area uses. Claude Code walks the directory tree so when you work inside `<hub>/<area>/`, it loads both the parent and that area's configuration -- but not the siblings.

The distinguishing question is **not** whether the work is on related subjects, but whether Claude should share context between them. Concrete examples:

| Scenario | Shape |
|---|---|
| Three client codebases, each with its own stakeholders | Separate work areas |
| A game studio with a shooter + a racing game + shared tools | Separate work areas |
| AI governance consultant: policy project, training curriculum, compliance audit tool (different deliverables, different audiences) | Separate work areas |
| One research effort producing three outputs (paper, slides, notes) that cross-reference constantly | One focused area |
| A novel with a companion reference bible | One focused area |
| Policy doc + training curriculum that share all the source material; audit tool is a separate codebase | Two work areas -- `policy-and-training` together, `audit-tool` separate |

The beginner heuristic: *"Imagine you're deep in thing A and Claude suddenly pulls up notes from thing B. Helpful? One focused area. Annoying? Separate."*

Switching shapes after the fact:

- `/upgrade-environment` on a single environment, then choose *"Convert to multi-area hub"* -- your current setup moves under a subfolder and a thin parent appears above it.
- `/upgrade-environment` on a hub with one remaining area, then choose *"Collapse hub to single area"* -- the area contents move up and the parent disappears.
- `/create` run inside an existing hub -- detected automatically; you're asked to name the new area and skip the shared-basics intake.

Neither conversion loses work. Both take about a minute.

### What a generated environment includes

A generated environment contains:

- **CLAUDE.md** -- Orchestrator behavior, routing, first-run onboarding, constraints with intent, canonical behavior examples, compaction hints, and domain-specific verification commands (under 250 lines)
- **Rule files** (`.claude/rules/`) -- Orchestration, autonomy, context management, self-learning, error handling, and domain-specific rules (e.g., VCS integration, binary asset protection, data safety). Each under 120 lines.
- **Agent definitions** (`.claude/agents/`) -- Domain-specific agents with model selection (opus/sonnet/haiku), tool lists, maxTurns limits, and focused instructions. Each under 80 lines.
- **Skill definitions** (`.claude/skills/`) -- Commands like /state-save, /state-load, /update, /health-check, plus domain-specific skills. Each skill uses a progressive disclosure structure (SKILL.md + optional scripts/ + optional references/).
- **settings.json** -- Permissions with allow rules for the user's ecosystem (language tools, VCS, external services) and deny rules for destructive operations
- **.claudeignore** -- Patterns for build artifacts, dependencies, binary assets, secrets
- **Project wiki** (`Docs/`) -- Dual-purpose: Claude's knowledge base AND human-readable documentation. Tiered (Lite/Standard/Enterprise) with index.md as the sole default-loaded file, area documents, decisions, and optional symbol reference. Publishable via GitHub Pages.
- **Working memory** (`Docs/_working/`) -- Transient session data excluded from wiki publishing: state snapshots, session history (auto-pruned after 30 days), and self-learning friction logs with pre-seeded patterns
- **Documentation** -- GETTING_STARTED.md (plain-language onboarding adapted to the user's technical level), VERSION.md, and environment metadata (GENESIS.md, ARCHITECTURE.md)

---

## Section 3: Architecture

### Orchestrator pattern

The Harness Generator follows an orchestrator + subagents pattern. The main conversation (governed by `CLAUDE.md` and `.claude/rules/`) acts as a router and coordinator. It classifies the user's intent, delegates work to specialized agents via the Task tool, and returns concise summaries pointing to artifacts on disk. The orchestrator intentionally keeps its own context lean -- tracking only the current pipeline step, target directory path, and last agent result summary. Templates, research documents, and best practices are never loaded into the orchestrator context; agents load what they need independently.

### Agent roster

The Harness Generator has five specialized agents, defined in `.claude/agents/`:

| Agent | Model | Role |
|-------|-------|------|
| **intake-interviewer** | sonnet | Conducts deep 5-stage project interviews when no starter profile fits. Uses the question relay protocol to communicate with users indirectly through the orchestrator. Writes GENESIS.md incrementally across up to 5 relay rounds. Cannot use Edit (write-only to GENESIS.md). |
| **environment-architect** | opus | Reads completed GENESIS.md, the relevant topic files from `Docs/AgentGuidelines/Topics/`, and the relevant starter or domain profile, then designs the full environment architecture. Produces ARCHITECTURE.md with component manifest, routing table, state taxonomy, memory tier, agent/skill rosters, the chosen team-architecture pattern and execution mode, and all configuration specifications. In custom mode it also writes DOMAIN_PROFILE.md. Does not generate environment files. |
| **component-generator** | opus | Writes environment files for one pass of the 5-pass pipeline per invocation. Reads ARCHITECTURE.md for what to generate, reference templates for how to structure it, and GENESIS.md for domain context. Tracks progress in GENERATION_PROGRESS.md. Invoked 5 times total during a /create run (hubs add a shell pass). |
| **environment-validator** | sonnet | Runs the full validation checklist (see validation-guide.md) against a generated environment, including the Phase-0 drift audit and boundary-crossing checks. Produces a detailed VALIDATION_REPORT.md with PASS/WARN/FAIL per check, skill triggering tests, and recommendations. Read-only with respect to the environment (writes only the report). |
| **upgrade-analyzer** | opus | Drives the `/upgrade-environment` analysis: reads the relevant topic files, the UpgradeChecklist playbook, and the target environment, then writes UPGRADE_RECOMMENDATIONS.md with improvements tiered as quick wins / medium / large. Does not implement changes (the component-generator does, after user approval). |

### Skill roster

The Harness Generator has four skills, defined in `.claude/skills/`:

| Skill | Role |
|-------|------|
| **create** | Trigger skill for the /create pipeline. Verifies the target directory, tests writability, checks for existing files, creates the state and environment directories, writes CREATION_CONTEXT.md, and returns control to the orchestrator. Does not run the full pipeline itself. |
| **validate-environment** | Standalone validation of any existing Claude Code environment. Runs structural, consistency, quality, and functional checks. Writes a validation report and offers to create a fix plan for issues found. |
| **upgrade-environment** | Audits an existing environment against current best practices, inventories it, and drives the interview + analyzer + implementation pipeline. Handles single <-> multi-area hub shape conversions. |
| **update** | Updates the Harness Generator's own knowledge base. Ingests pending ProvideKnowledge/ items first, then checks topic files for staleness, searches Anthropic documentation for updates, and incorporates validated findings with source attribution and conflict tracking. Has a local-only mode that ingests ProvideKnowledge/ without web search. |

### Pipeline flow

The `/create` pipeline proceeds as a sequence of agent handoffs:

```
1. [Skill: create]
   Verify target directory, write CREATION_CONTEXT.md
        |
2. [Orchestrator]
   Read CREATION_CONTEXT.md, present starter profiles
        |
3. [Orchestrator or Agent: intake-interviewer]
   Profile-first: orchestrator handles directly (2-3 Q&A rounds)
   Deep interview: delegated to intake-interviewer (up to 5 relay rounds)
   Output: GENESIS.md
        |
4. [Agent: environment-architect]
   Read GENESIS.md + topic files + starter/domain profile
   Pick team-architecture pattern + execution mode; custom mode writes DOMAIN_PROFILE.md
   Output: ARCHITECTURE.md
        |
5. [Orchestrator]
   Present architecture summary and file tree preview
   Get user confirmation
        |
6. [Agent: component-generator] x5 invocations (hubs add a shell pass)
   Pass 1: Foundation (CLAUDE.md, rules, settings, .claudeignore)
   Pass 2: Agents
   Pass 3: Skills
   Pass 4: Infrastructure (memory, self-learning, state)
   Pass 5: Documentation (GETTING_STARTED.md, VERSION.md, cross-refs)
   Output: all environment files + GENERATION_PROGRESS.md
        |
7. [Agent: environment-validator]
   Validation checklist (see validation-guide.md) + Phase-0 drift audit
   + boundary-crossing checks + skill triggering tests
   Output: VALIDATION_REPORT.md
        |
8. [Orchestrator]
   Present final summary with smoke test instructions
```

### Artifact-first handoff

Every delegated job produces a durable artifact on disk. The orchestrator never receives large payloads in the conversation -- only short summaries and file paths:

- Intake writes `<target>/Docs/Environment/GENESIS.md`
- Architect writes `<target>/Docs/Environment/ARCHITECTURE.md`
- Generator writes all environment files plus `<target>/Docs/Environment/GENERATION_PROGRESS.md`
- Validator writes `<target>/Docs/Environment/VALIDATION_REPORT.md`

This approach keeps the main conversation context lean and ensures that all intermediate state survives context compaction or session interruption.

### Template system

Templates live in `Docs/Templates/` -- 50 files in all, organized into five categories (plus a README at the root):

| Directory | Count | Contents |
|-----------|-------|----------|
| `Core/` | 16 templates | CLAUDE.md, parent (hub) CLAUDE.md, hub GENESIS, orchestrator rule, routing rule, autonomy rule, context management rule, memory management rule, self-learning rule, error handling rule, settings.json, memory scaffold, state-save skill, state-load skill, update skill, health-check skill |
| `Optional/` | 10 templates | VCS (Git), VCS (Perforce), build system, testing gates, review workflow, team coordination, hooks, output styles, data handling rule, sensitive data rule |
| `Agents/` | 9 templates | Researcher, implementer, reviewer, planner, explorer, debugger, analyst, drafter, performance analyst |
| `Skills/` | 6 templates | Build, review, health-check, map-codebase, process-data, process-inbox |
| `References/` | 8 reference docs | architecture-guide, component-generator-guide, interview-guide, generation-standards-reference, validation-guide (validation single source of truth), tool-registry, tool-catalog (file processing tools), ecosystem-permissions (per-language permission sets) |

Templates are annotated reference implementations, not fill-in-the-blank forms. They contain HTML comments (using tags like `ANNOTATION:`, `VARIATION:`, `ANTI-PATTERN:`, `QUALITY:`, `EXAMPLE:`) that explain why each section exists, how to adapt it for different domains, what to avoid, and what the validator will check. The component-generator reads templates for structural guidance and composes original content tailored to each project's GENESIS.md and ARCHITECTURE.md.

### Knowledge base

The Harness Generator maintains a knowledge base that informs architecture and generation decisions:

- **Topic files** (`Docs/AgentGuidelines/Topics/`) -- 18 topic files (consolidated down from 26, so numbering is non-contiguous) covering rules, agents, skills, teams, memory, self-learning, routing, integration, permissions, user experience, Opus specifics, testing/validation, hooks, cost awareness, official plugins, RAG strategies, and multi-modal workflows, plus a `00-appendix.md`. Each topic file includes sourced recommendations, anti-patterns, and actionable thresholds. Indexed by `Docs/AgentGuidelines/INDEX.md`. Loaded selectively by the architect and generator, never by the orchestrator.

- **Agent Playbooks** (`Docs/AgentPlaybooks/`) -- 6 step-by-step process guides (plus INDEX) loaded into agent context on demand:
  - `OrchestratorWorkflow.md` -- The end-to-end pipeline contract for the orchestrator
  - `IntakeChecklist.md` -- Full intake protocol for both paths
  - `ComponentQuality.md` -- Quality standards per component type
  - `EnvironmentValidation.md` -- Validation protocol with test scenarios
  - `UpgradeChecklist.md` -- The /upgrade-environment audit and recommendation protocol
  - `HubPipelineTests.md` -- Manual end-to-end hub scenarios

- **Tool catalog** (`Docs/Templates/References/tool-catalog.md`) -- Detailed specifications for file processing tools (MarkItDown, Pandoc, python-docx, openpyxl, ImportExcel, pdfplumber, ffmpeg) including installation methods, permission patterns, and MCP configuration.

- **ProvideKnowledge** (`Docs/ProvideKnowledge/`) -- A drop zone where users can contribute knowledge. The `/update` skill (in its local-only mode) reads from this directory, classifies items, validates them, and incorporates findings into the topic files.

### Context discipline

The Harness Generator enforces strict context management at two levels:

**Orchestrator level:** The main conversation tracks only the current pipeline step, target path, and last agent result. It does not load templates, research, or topic files. Knowledge base indexes (`Docs/AgentGuidelines/INDEX.md`, `Docs/AgentPlaybooks/INDEX.md`) are loaded on demand, not preloaded.

**Agent level:** Each agent loads only the references it needs for its specific job. The architect loads the relevant topic files and the relevant starter or domain profile. The generator loads ARCHITECTURE.md, GENESIS.md, ComponentQuality.md, and the specific templates for its current pass. The validator loads EnvironmentValidation.md (and validation-guide.md) plus ComponentQuality.md. This prevents any single context from being overwhelmed.

### Quality enforcement

Quality is enforced through four mechanisms:

1. **Generation standards** (`.claude/rules/02-generation-standards.md`) -- Hard limits on file sizes (CLAUDE.md under 250 lines, rules under 120, agents under 80, skills under 500 lines / 5,000 words), required component structure, prompt engineering rules for Opus 4.8 / 4.7 (compatible with 4.6; no temperature/top_p/top_k -- tune via effort), and anti-overengineering principles.

2. **Quality gates** (`.claude/rules/03-quality-gates.md`) -- Pre-generation checks (directory writability, existing files), a file preview gate before writing, and the post-generation validation checklist (see validation-guide.md).

3. **The validator agent** -- Runs structural checks (file existence, frontmatter validity, JSON validity), logic checks (routing coverage, state symmetry, contradictions), size checks, and functional checks (skill triggering tests). Produces a graded report.

4. **Anti-overengineering** -- A principle enforced throughout: generate only what the intake justifies. If the intake does not mention VCS, no VCS rules. If the user is solo, no team coordination. If the project is simple, use Lite memory tier. Every component must trace back to a stated need or a core best-practice requirement.

### Special patterns

The architect detects specific signals in GENESIS.md and applies corresponding architectural patterns:

- **Pattern A -- Sensitive data:** Generates data classification rules, memory isolation, deny patterns, and handling rules per data category (PII, PHI, financial, legal)
- **Pattern B -- Repeatable engagements:** Generates a `/new-engagement` skill with per-entity folder creation, template copying, checklist initialization, and entity tracking
- **Pattern C -- Deliverable tracking:** Generates persistent deliverable tracking documents with status, due dates, and phase markers
- **Pattern D -- Binary file protection:** Generates .claudeignore patterns, PreToolUse hooks blocking edits on binary extensions, and routing entries with step-by-step instructions for the appropriate external tool
- **Pattern E -- File processing pipeline:** Generates Inbox/Outbox/Data directories, tool permissions, dual-mode routing, and optionally brand guidance infrastructure

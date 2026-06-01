# Intake Checklist

Step-by-step intake protocol for gathering requirements and producing GENESIS.md.
Loaded by the orchestrator during /create and by the intake-interviewer agent.

---

## Path Selection

Two intake paths exist. The orchestrator selects based on user behavior:

- **Profile-first** (primary): User can identify with a starter profile. Orchestrator
  handles directly -- no subagent needed. Covers ~80% of users.
- **Deep interview** (fallback): User says "none of these," describes something unusual,
  or the orchestrator cannot confidently map them to a profile. Delegated to
  intake-interviewer agent.

Decision rule: If the user's project clearly maps to one of the starter profiles
(software-development, knowledge-work, data-analysis, devops-infrastructure) -- or
a bundled domain such as game-development -- with at most 3-5 modifications,
use profile-first. Otherwise, use deep interview.

---

## Profile-First Path (Orchestrator-Direct)

### Step 0: Experience level (preamble)

Before presenting profiles, gauge the user's comfort level:

"How familiar are you with AI assistants and command-line tools?
(Just getting started / Somewhat familiar / Very comfortable)"

This determines:
- **Agent count**: Fewer agents for novices (avoid overwhelming them).
- **Language complexity**: Simpler wording in generated CLAUDE.md and rules for beginners.
- **GETTING_STARTED.md depth**: Detailed walkthrough for beginners, concise for experts.
- **Terminal basics**: Whether to include basic terminal/CLI guidance in generated docs.

Record the answer in GENESIS.md under `## Preferences` (or `## Intake Notes` if
Preferences is not yet written). Proceed regardless of the answer -- this is
informational, not a gate.

### Step 0b: Work-area shape

Ask how Claude should treat this work (say "work area", never "hub"):

- *One focused area* -- everything is closely related, shared context (a single
  codebase; a research effort with multiple outputs; a novel + its reference bible).
- *Separate work areas that share some basics* -- Claude keeps each mentally
  separate but remembers shared rules and style (three client codebases; a studio
  with a shooter + a racing game + shared tools; a consultant with a policy
  project + a training curriculum + an audit tool).
- *Not sure yet* -- run the two-question branch below.

Always reassure: "You can change this later -- converting between one focused
area and multiple work areas takes about a minute. Nothing here is locked in."

**"Not sure" branch**: (1) "List the main things you'll work on here -- short
names are fine." (2) "Imagine you're deep in [thing A] and Claude suddenly pulls
up notes from [thing B]. For each pair: helpful, annoying, or depends?" Decision
rule: all "helpful" -> one focused area; any "annoying" -> separate work areas
(group the "helpful" pairs); mostly "depends" -> default to separate, explain
it's reversible. For multiple areas, collect one-line descriptions and loop the
profile-first steps per area (shared basics collected once -> HUB_GENESIS.md).

### Step 0c: Preset vs custom generation

Ask which generation mode fits before presenting options:

- **Preset** -- start from a tested, validated base profile or a bundled domain
  (`Docs/DomainLibrary/`). Fast, fewer tokens, fewer interview rounds. Best for
  one-off or short-term harnesses, or when a preset clearly matches.
- **Custom** -- the environment-architect synthesizes a tailored, reusable
  `DOMAIN_PROFILE.md` in the target environment from a deeper interview, then
  designs from it. More tokens and time, but the profile is reusable across
  future /create and /upgrade runs. Best for long-term harnesses or novel domains.

Recommend preset when a base profile or bundled domain clearly matches; recommend
custom for novel or long-lived domains. Record `GENERATION_MODE: preset|custom`
(plus the preset name, if any) in GENESIS.md. Custom mode routes the architect
through its profile-synthesis substep; preset mode adapts the chosen profile.

### Step 1: Present starter profiles

Show the user the four starter profiles in plain language. Do not use
technical jargon. Example presentation:

```
I have four starting templates that cover most projects:

1. Software Development -- For building and maintaining code (web apps, APIs,
   libraries, CLI tools, data pipelines). Includes code review, debugging,
   and build automation.

2. Knowledge Work -- For research, writing, analysis, and document-heavy work
   (legal, academic, consulting, content creation). Focused on research and
   drafting with conservative safety defaults.

3. Data & Analysis -- For data-centric projects (analytics, reporting,
   dashboards, spreadsheet analysis). Includes data exploration,
   transformation workflows, and calculation verification.

4. DevOps & Infrastructure -- For infrastructure, cloud platforms, and
   reliability engineering (Terraform, Kubernetes, CI/CD, monitoring).
   Includes infrastructure safety gates, IaC protection, and incident response.

Which of these is closest to your project? Or describe your project and
I will figure out the best fit.
```

If a bundled domain under `Docs/DomainLibrary/` matches the user's field more
precisely than a base profile (e.g., "security audit", "grant writing",
"customer support", "game development", "data science / ML"), present it alongside
the four base profiles as a fifth option, noting it is a pre-built, tested
starting point for that domain.

**Validation**: User must select a profile OR describe their project. If they
describe something, attempt to map it to a profile or bundled domain. If none
fits, switch to deep interview path (or offer custom generation per Step 0c).

### Step 2: Present profile summary

After selection, present the profile's key choices in plain language:

- What assistants (agents) it includes and what they do
- What commands (skills) it provides
- What tools/permissions it sets up
- What workflow style it uses (proactive vs. conservative)

Ask: "Does this sound right for your project, or would you like to adjust anything?"

**Validation**: User confirms or requests changes. Proceed when the user
expresses general agreement (even with modifications noted).

### Step 3: Gather modifications (2-3 rounds max)

If the user requested changes, ask targeted follow-up questions. Examples:

- "You mentioned you use Perforce instead of Git. I will set that up. Anything
  else about your version control workflow?"
- "You said you work solo. I will simplify the memory structure and remove
  team coordination. Sound good?"
- "You mentioned a Python FastAPI project. I will add Python-specific
  permissions and testing commands."

Also ask these probes explicitly if not already covered by the profile or
user-volunteered information:

- **Team and role diversity**: "Is it just you, or does a team work on this
  project? If a team, does everyone do the same type of work, or are there
  different roles -- like developers, designers, QA, marketing, etc. -- who
  would each use the assistant differently?"
  This determines: multi-role environment configuration.
  Signals:
  - Solo -> skip multi-role entirely
  - Team, same role (e.g., all developers) -> standard team setup, no role config
  - Team, different roles -> generate multi-role support:
    - `Docs/Roles/` directory with CLAUDE.local.md templates per role
    - Role-prefixed routing entries in the orchestrator rule
    - Per-role settings.local.json templates
    - Per-role wiki retrieval hints
    - "Setting up your role" section in GETTING_STARTED.md
  Follow up: "What roles use or would use this project? For each role, what
  would they typically ask the assistant to help with?"

- **Data processing**: "Do you work with data files like spreadsheets, CSV
  files, or databases? If so, what do you typically need to do with them --
  read them, analyze them, transform them, or produce reports from them?"
  This determines: Python/data tool permissions, data-analyst agent,
  data processing routing entries.

- **Sensitive data**: "Does your work involve sensitive or regulated data --
  such as client information, student records, patient data, or financial
  records? Are there any types of information the assistant should never
  store or display?"
  This determines: data classification rules, restricted memory paths,
  PII handling rules, deny patterns.
  **Follow-up if yes**: "Should the assistant automatically block sensitive
  data from appearing in output files -- for example, scanning for SSNs,
  account numbers, or patient IDs before writing? Or is guidance-only
  (advisory rules) sufficient for your needs?"
  This determines: compliance enforcement hooks (deterministic PreToolUse
  PII content gate + pii-patterns.conf) vs advisory-only sensitive-data rule.
  For regulated industries (HIPAA, SOX, PCI-DSS), recommend enforcement hooks.

- **Repeatable processes**: "Do you repeat the same process for different
  clients, students, cases, or projects? If so, describe one such repeatable
  workflow from start to finish."
  This determines: template-management skills, per-entity folder structures,
  /new-engagement style skills. (Replaces a generic "do you repeat tasks?"
  question with a more actionable probe.)

- **Output format requirements**: "What kinds of documents or files does your
  work produce? For example: plain text notes, Word documents, presentations,
  PDFs, spreadsheets, or data exports. For the formatted documents you produce,
  do they go to external audiences like clients, boards, regulators, or
  publishers -- where professional formatting and layout matter?"
  This determines: whether the environment needs document conversion/formatting
  tools (Pandoc exe install for high-quality .docx/.pptx/.pdf output) vs
  simpler pip-only tools (python-docx, openpyxl). Signals:
  - Text/markdown only -> no special tooling
  - Excel/data files -> pip-only (openpyxl)
  - Basic internal .docx -> pip-only (python-docx)
  - Formatted .docx/.pptx/.pdf for external audiences -> Pandoc recommended
  - Presentations -> Pandoc strongly recommended

- **Brand requirements**: "Does your organization have brand guidelines, a
  style guide, or design standards that your work output should follow? Do
  you have existing document or presentation templates that produced files
  should match? For example: specific colors, fonts, logos, or a particular
  tone of voice."
  This determines: whether the environment needs brand-aware output scaffolding.
  Signals:
  - No brand requirements -> skip Brand/ setup entirely
  - Has a brand guide or style document -> generate Brand/Guidelines/ directory
    + brand analysis workflow + brand-rules.md auto-generation
  - Has existing templates (.docx/.pptx) that output must match -> generate
    Brand/Templates/ directory + Pandoc reference-doc integration
  - Both brand guide and templates -> full Brand/ scaffolding with brand-rules
    auto-generation and template-aware output routing

- **Codebase scale** (technical projects only): "Is your project built on an
  existing codebase with many files, or starting fresh? Roughly how many
  source files are there -- under a hundred, hundreds, or thousands? Do you
  find it hard to keep track of where things are?"
  This determines: RAG strategy for codebase retrieval.
  Signals:
  - Fresh/small (<100 files) -> standard agentic search (Glob/Grep/Read)
  - Medium (100-1000 files) -> /map-codebase skill + wiki hierarchy
  - Large (1000+ files) -> /map-codebase + hierarchical summaries + recommend
    semantic search MCP (Claude Context MCP or Code-Graph-RAG)
  - Dense inheritance (UE5, Unity, large OOP) -> tree-sitter dependency graphs

- **Reference documents**: "Do you work with reference documents like design
  specs, API docs, legal references, or technical manuals? If so, what
  formats are they in (PDF, Word, web pages, etc.) and roughly how many?"
  This determines: document parsing pipeline recommendation.
  Signals:
  - No external docs -> skip document integration
  - Few markdown/text docs -> store directly in Docs/Reference/
  - PDFs/Word docs (under 20) -> recommend MinerU for markdown conversion
  - Complex docs with tables/hierarchy -> recommend Docling
  - Scanned docs/images with text -> recommend PaddleOCR
  - Large doc sets (100+) -> recommend dedicated document search MCP
  - Exploratory/research use -> recommend NotebookLM for interactive analysis

- **Task complexity and session patterns**: "Do your tasks tend to finish
  in one session, or do they span multiple sessions with interdependent
  steps? Do you ever run multiple assistant chats at the same time on
  the same project?"
  This determines: Beads, session segmentation, and promote-on-commit config.
  Signals:
  - Simple/single-session tasks -> standard /state-save only
  - Multi-session with dependencies + intermediate+ user -> recommend Beads
    for persistent task tracking alongside markdown wiki (any domain)
  - Non-Git VCS (Perforce, SVN) -> present trade-off: Beads requires Git,
    so user would need a parallel Git repo for task tracking. Flag this
    explicitly and let the user decide, rather than silently excluding.
  - Parallel agent workflows -> Beads strongly recommended (conflict-free design)
  - Concurrent chats on same project -> enable session-segmented working memory
    (_working/state/<session-slug>/ instead of single state file)
  - User wants minimal tooling footprint -> /state-save only
  Also identify the domain-specific "commit point" -- the moment when working
  memory should be promoted to the shared wiki:
  - Software dev: VCS commit after build + tests pass
  - Legal: section draft approved by reviewer
  - Research: paper section finalized after review
  - Game dev: feature passes playtest gate + VCS submit
  - Knowledge work: deliverable sent to audience
  - Data analysis: report delivered after validation
  This commit point determines when /state-save or a post-commit hook should
  trigger wiki promotion (extracting decisions, patterns, and area updates
  from _working/ into shared Docs/).

- **AI tool budget and multi-model interest**: "Are you using only Claude Code,
  or do you also use other AI tools like ChatGPT, Gemini, Copilot, or local
  models? What is your rough monthly budget for AI tools?"
  This determines: multi-model workflow configuration.
  Signals:
  - Claude only ($20-200/mo) -> optimize environment for Claude strengths
  - Claude + free tools ($20-50/mo) -> document which free tools for which tasks
  - Claude + paid tools ($100-300/mo) -> configure MCP bridges, document routing
  - Unlimited budget ($500+/mo) -> API-first routing, multi-model orchestration
  Present budget tiers as suggestions, not requirements. Many users are unaware
  of free/local options that could augment their workflow.

- **Token efficiency priority**: "How important is keeping token costs low versus
  getting the most thorough results? Some options:"
  - **Cost-conscious**: "Use the fastest, cheapest model for everything. Compact
    context aggressively. Recommend tools that reduce token usage. Best for teams
    watching spend closely."
  - **Balanced** (default): "Use faster models for routine work, more capable models
    for planning and review. Standard context management. Good for most projects."
  - **Quality-first**: "Use the most capable model wherever it helps. Generous
    context. No optimization pressure. Best when quality matters more than cost."
  This determines:
  - Model defaults in settings.json (all-Sonnet vs mixed vs Opus-available)
  - Compaction threshold (85% vs 95% default vs 95% default)
  - .claudeignore aggressiveness (aggressive + generic vs domain-specific vs minimal)
  - RTK install instructions in GETTING_STARTED.md (full setup vs mention vs omit)
  - CLAUDE.md line target (150 vs 200 vs 250)
  - Agent roster size (consolidated vs standard vs full)
  Default: balanced if no preference stated.

**Validation**: Each modification must be concrete enough to act on.
Vague requests like "make it better" should prompt a specific clarifying
question (e.g., "Better in what way -- faster responses, more thorough
reviews, or something else?").

### Step 4: External services and MCP integrations

Ask about external tools and services. This is a dedicated step because it
directly affects settings.json permissions, MCP configuration, and potentially
which agents are generated.

Questions to ask:
1. "Do you use any external services that your assistant should connect to?
   For example: GitHub, Jira, Notion, Slack, databases, cloud providers."
2. "Do you use any additional Claude Code plugins or tool integrations that extend what the assistant can do? (These are sometimes called MCP servers -- if you are not sure, the answer is probably no.)"
3. "Are there any websites or documentation sources your assistant should be
   able to search or reference?"

If the user mentions specific services:
- Record each service name and how they use it
- Note whether it needs read access, write access, or both
- Flag any that would require MCP server configuration

If the user says "none" or is unsure, skip. Do not push.

**Validation**: Each mentioned service has a stated purpose (what the user
uses it for). Services without clear purpose are noted but not acted on.

### Step 5: Confirm and write GENESIS.md

Present a final summary of what will be generated:
- Profile base + modifications
- External services/MCP (if any)
- Target directory

Ask: "Ready to proceed? I will design your environment based on this."

On confirmation, write GENESIS.md to `<target>/Docs/Environment/GENESIS.md`.

**Validation**: GENESIS.md must contain all sections listed in the
GENESIS.md Format section below. All sections must have content (even if
"None specified" for optional sections).

---

## Deep Interview Path (intake-interviewer Agent)

Used when the user's needs do not map to a starter profile. The agent runs
a 5-stage funnel, writing findings incrementally to GENESIS.md.

### Stage 1: Project Overview

Goal: Understand domain, work type, scale, and team.

Questions:
- "What kind of project is this? What does it do or produce?"
- "Is this mostly code, documents, research, data, or a mix?"
- "How many people work on it? Just you, a small team, or a large org?"
- "What is the main thing you want an AI assistant to help with?"
- "How familiar are you with AI assistants and command-line tools?
  (Just getting started / Somewhat familiar / Very comfortable)"
  This determines: agent count, language complexity in generated docs,
  GETTING_STARTED.md depth, whether to include terminal basics.

Skip conditions: None. This stage always runs.

**Validation**: After this stage, the agent must be able to state in one sentence
what the project is and what the user wants help with. If not, ask one more
clarifying question before proceeding.

Write to GENESIS.md: `## Project Overview` section.

### Stage 2: Technical Environment

Goal: Languages, VCS, build system, external services, plugin/tool integration needs.

Questions:
- "What programming languages or tools does the project use?"
- "Do you use version control? If so, which one (Git, Perforce, SVN, etc.)?"
- "Do you have a build system, test suite, or CI/CD pipeline?"
- "What external services does your project connect to (databases, APIs,
  cloud platforms, project management tools)?"
- "Do you use any additional Claude Code plugins or tool integrations that extend what the assistant can do? (These are sometimes called MCP servers -- if you are not sure, the answer is probably no.)"
- "Do you work with data files like spreadsheets, CSV files, or databases?
  If so, what do you typically need to do with them -- read them, analyze
  them, transform them, or produce reports from them?"
  This determines: Python/data tool permissions, data-analyst agent,
  data processing routing entries.
- "Does your project include files like images, videos, audio, design files,
  or other files that cannot be edited as text?"
  This determines: .claudeignore patterns, binary protection hooks,
  "describe editor steps" routing entries.

Skip condition: If Stage 1 reveals a purely non-technical project (e.g.,
pure writing, legal analysis with no code), skip this stage entirely.
Record "Technical environment: N/A -- non-technical project" in GENESIS.md.

**Validation**: For technical projects, at minimum the primary language and
VCS must be identified. If the user says "I don't know" about build/CI, record
"Build system: Not specified" rather than leaving blank.

Write to GENESIS.md: `## Technical Environment` section.

### Stage 3: Workflow

Goal: Understand work patterns, quality gates, pain points.

Questions:
- "Walk me through a typical task from start to finish. What steps do you
  usually take?"
- "Are there any approval steps or quality checks in your process?"
- "What are the most frustrating or time-consuming parts of your workflow?"
- "Do you repeat the same process for different clients, students, cases, or
  projects? If so, describe one such repeatable workflow from start to finish."
  This determines: template-management skills, per-entity folder structures,
  /new-engagement style skills.

Skip condition: None. This stage always runs, but questions adapt based on
whether the project is technical or non-technical.

**Validation**: At least one workflow pattern must be described. At least one
pain point should be identified (if none, record "No specific pain points
identified").

Write to GENESIS.md: `## Workflow` section.

### Stage 4: Roles and Specializations

Goal: What specialized assistants would be useful, what needs human approval.

Questions:
- "If you could have specialized AI assistants, what would each one do?"
- "Are there any actions the assistant should NEVER do without asking you first?"
- "Are there any actions the assistant should ALWAYS do automatically?"
- "How much do you want the assistant to explain its reasoning versus just
  doing the work?"
- "Does your work involve sensitive or regulated data -- such as client
  information, student records, patient data, or financial records? Are there
  any types of information the assistant should never store or display?"
  This determines: data classification rules, restricted memory paths,
  PII handling rules, deny patterns.
  Follow-up if yes: "Should sensitive data be blocked automatically
  (deterministic scanning) or handled by advisory guidelines only?"
  This determines: compliance enforcement hooks vs advisory-only.

Skip condition: If the project is very simple (solo, single-purpose), condense
to: "What should the assistant always ask about before acting?"

**Validation**: The hard constraints (never-do-without-asking) must be
explicitly recorded. If the user cannot think of any, record
"No hard constraints specified -- default to domain-appropriate safety level."

Write to GENESIS.md: `## Roles and Constraints` section.

### Stage 5: Preferences

Goal: Communication style, autonomy level, documentation needs.

Questions:
- "How do you prefer the assistant to communicate -- brief and direct, or
  detailed and explanatory?"
- "Should the assistant write documentation as it works, or only when asked?"
- "Any other preferences or requirements I should know about?"

Skip condition: Can be condensed to a single question if earlier stages
have already revealed clear preferences.

**Validation**: At minimum, communication style preference must be recorded.

Write to GENESIS.md: `## Preferences` section.

---

## Question Relay Protocol

When the intake-interviewer agent needs user answers but cannot ask the user
directly (agents communicate only through the orchestrator), it uses this
protocol:

### Agent Side

1. Write findings so far to GENESIS.md.
2. Add a `## Pending Questions` section at the bottom of GENESIS.md:
   ```
   ## Pending Questions

   STATUS: AWAITING_ANSWERS

   1. [Question text here]
   2. [Question text here]
   3. [Question text here]
   ```
3. Return control to the orchestrator with a summary of progress and note
   that questions are pending.

### Orchestrator Side

1. Read GENESIS.md, find the Pending Questions section.
2. Present each question to the user via AskUserQuestion (one at a time
   or grouped logically).
3. Write the user's answers into GENESIS.md, replacing the questions:
   ```
   ## Pending Questions

   STATUS: ANSWERS_PROVIDED

   1. Q: [Question text]
      A: [User's answer]
   2. Q: [Question text]
      A: [User's answer]
   ```
4. Re-invoke the intake-interviewer agent to continue.

### Constraints

- Maximum 5 relay rounds. If the agent still needs answers after 5 rounds,
  it must proceed with what it has and note assumptions in GENESIS.md.
- Each round should ask 2-5 questions (not 1, not 10).
- Questions must be in plain language.
- Questions must not repeat information already gathered.

---

## External Services / MCP Questions

These questions are asked in both paths (Step 4 of profile-first, Stage 2 of
deep interview). They determine:
- settings.json permission additions (WebFetch domain restrictions, Bash commands)
- MCP server configuration suggestions in ARCHITECTURE.md
- Whether specialized agents need tool access

### Service Categories to Probe

| Category | Example Services | What to Record |
|----------|-----------------|----------------|
| Version control hosting | GitHub, GitLab, Bitbucket | Read/write access level, PR workflow |
| Project management | Jira, Linear, Notion, Trello | Read-only or read-write, what to track |
| Communication | Slack, Discord, Teams | Notification needs, channel targets |
| Cloud platforms | AWS, GCP, Azure | Which services, CLI tools used |
| Databases | PostgreSQL, MongoDB, Redis | Local dev? Connection strings? |
| Documentation | Confluence, Notion, Google Docs | Read-only reference or write access |
| CI/CD | GitHub Actions, Jenkins, CircleCI | Trigger builds? Read results? |
| Monitoring | Datadog, Sentry, PagerDuty | Read alerts? Acknowledge? |

### For Each Service Identified

Record:
- Service name
- How the user uses it (1 sentence)
- Access level needed (read / write / admin)
- Whether an MCP server exists for it (known MCP servers: GitHub via gh CLI,
  filesystem, Postgres, Puppeteer, Brave Search, Google Maps, Sentry, Slack)
- Whether a CLI tool exists (gh, aws, gcloud, az, kubectl, etc.)

---

## GENESIS.md Format

The output of intake (either path) is a GENESIS.md file written to
`<target>/Docs/Environment/GENESIS.md`. This file is immutable after
creation -- it serves as the permanent record of the user's original
requirements.

Required sections:

```markdown
# Environment Genesis

Created: YYYY-MM-DD
Intake Path: Profile-First | Deep Interview
Generation Mode: preset | custom
Base Profile: <base profile name> | <bundled domain name> | Custom (DOMAIN_PROFILE.md)

## Project Overview
[What the project is, what it does, team size, primary need]

## Technical Environment
[Languages, VCS, build system, test framework, CI/CD]
[Or "N/A -- non-technical project"]

## Workflow
[Typical task flow, quality gates, pain points, automation desires]

## Roles and Constraints
[Desired specializations, hard constraints, autonomy preferences]

## Team Role Diversity
[Solo / Team-same-role / Team-multi-role. If multi-role: list each role,
what they use the assistant for, and permission differences. Or "N/A -- solo"]

## External Services
[Service list with access levels, or "None specified"]

## Codebase Scale and RAG Strategy
[Codebase size estimate, retrieval approach recommendation, or "N/A -- fresh project"]

## Reference Documents
[Document types, formats, volume, recommended parsing tool, or "None"]

## Task Complexity and Tracking
[Single-session vs multi-session, task dependencies, parallel work, VCS type,
Beads recommendation, or "Simple -- standard state management"]

## AI Tool Budget and Multi-Model Usage
[Budget tier, other AI tools in use, routing recommendations, or "Claude only"]

## Token Efficiency Priority
[cost-conscious / balanced / quality-first. Determines: model defaults, compaction
threshold, .claudeignore aggressiveness, RTK recommendation level, CLAUDE.md line
target, agent consolidation. Default: balanced if not explicitly stated.]

## Sensitive Data Handling
[Data types present, regulatory frameworks, enforcement preference
(deterministic hooks / advisory only / N/A), domain-specific PII patterns]

## AI Ecosystem Extensions
[Capability gaps identified during intake and chosen tools. For each:
- Capability needed (image gen, video gen, audio, local inference, etc.)
- Tool(s) chosen (from tool-registry.md options presented to user)
- Integration type (MCP / CLI / API)
- Budget consideration
Or "None -- Claude's native capabilities are sufficient"]

## Preferences
[Communication style, documentation preferences, other]

## Modifications from Base Profile
[What was changed from the starter profile, or "N/A -- custom intake"]

## Intake Notes
[Any assumptions made, gaps in information, follow-up suggestions]
```

---

## Validation Criteria for Proceeding to Architecture

The orchestrator checks these criteria before spawning the environment-architect.
ALL must pass:

### Must-have (block if missing)

1. **Project type is clear**: Can state in one sentence what the project is.
2. **Primary need is identified**: What the user wants help with.
3. **Routing is designable**: Enough information to create a domain-specific
   routing table (at least 3 distinct intent categories).
4. **Agent set is identifiable**: Know which agents to generate (at least 1).
5. **Hard constraints are recorded**: Even if "none specified."
6. **Target directory is verified**: Writable, checked for existing files.

### Should-have (warn if missing, proceed anyway)

7. **VCS identified** (for technical projects): Default to Git if not stated.
8. **Communication style stated**: Default to "balanced" if not stated.
9. **External services listed**: Default to "none" if not asked or stated.
10. **Scale/team size known**: Default to "solo" if not stated.

### Handling Missing Information

- For must-have gaps: Ask one targeted question. If still unclear after the
  answer, make a reasonable assumption and record it in Intake Notes.
- For should-have gaps: Record the default in GENESIS.md with a note:
  "(assumed -- not explicitly stated by user)"
- Never block on should-have items.

---

## Edge Cases

### Contradictory Answers

If the user gives contradictory information (e.g., "I want full autonomy"
and later "always ask before making changes"):

1. Note the contradiction.
2. Present it back: "You mentioned wanting full autonomy, but also that the
   assistant should always ask first. Which is closer to what you want?"
3. Record the resolution in GENESIS.md Intake Notes.
4. If unresolved, default to the more conservative option.

### Unclear Domain

If the project does not fit any known category:

1. Focus on workflow (Stage 3) -- how work gets done matters more than
   what the domain is called.
2. Map workflow patterns to the closest starter profile for structural
   guidance.
3. Note in GENESIS.md: "Non-standard domain. Architecture based on
   workflow similarity to [closest profile]."

### Existing Environment

If the target directory already has .claude/ or CLAUDE.md:

1. The /create skill detects this before intake begins.
2. User is offered three options:
   - Backup existing files and create fresh
   - Cancel and use /validate-environment instead
   - Cancel entirely
3. If backup is chosen, existing files are moved to
   `<target>/.claude-backup-YYYYMMDD/` before proceeding.

### User Wants to Stop and Resume Later

1. GENESIS.md is written incrementally. Whatever has been gathered so far
   is already on disk.
2. If the user stops mid-interview, the next /create invocation
   will detect the partial GENESIS.md and offer to resume or start over.
3. Detection: GENESIS.md exists but ARCHITECTURE.md does not.

### User Provides a Spec or Document

If the user shares a document, spec, or detailed description instead of
answering questions:

1. Read the document.
2. Extract answers to the intake questions from it.
3. Present the extracted understanding for confirmation.
4. Fill gaps with targeted questions.
5. Proceed normally.

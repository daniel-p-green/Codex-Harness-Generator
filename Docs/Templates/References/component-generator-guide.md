# Component Generator Guide

Reference document for the component-generator agent. Contains detailed pass
descriptions, template references, and generation patterns.

Loaded by the component-generator agent before starting each pass.

## Template Usage

Templates in `Docs/Templates/` are annotated reference implementations, NOT fill-in-the-blank forms. Read each template to understand:
- The required structure and sections
- The annotations (HTML comments) explaining WHY each section exists
- The variation notes for different domains
- The anti-patterns to avoid
- The quality criteria for validation

Then compose original content adapted to this specific project. Do not copy template text verbatim unless it is genuinely the right content for this project.

## Pass Descriptions

Pass descriptions below apply to single-area mode and to per-area passes in
hub mode. For hub mode, see `Hub Shell Pass` at the end of this section -- it
replaces Pass 1 at the parent layer; the per-area passes below still apply
under each `<area-slug>/` subfolder.

### Pass 1: Foundation

**Topic files to load**: `Docs/AgentGuidelines/Topics/` -- 01-rules, 05-memory, 08-routing, 11-permissions, 13-opus, 16-hooks, 18-cost

Files: CLAUDE.md, all rule files, settings.json, .claudeignore, hooks (if specified in ARCHITECTURE.md)

Key requirements:
- CLAUDE.md must be under 250 lines. Every line must earn its place.
- CLAUDE.md must include: purpose (not role-setting), first-run onboarding, non-negotiable constraints with WHY, autonomy reference, command reference, orchestrator contract, 2-3 canonical behavior examples, compaction hints, verification patterns, self-improvement note.
- CLAUDE.md must NOT include role-setting prompts ("Act as...", "You are a senior...").
- Each rule file must be under 120 lines.
- The orchestrator rule must contain the FULL routing table from ARCHITECTURE.md.
- settings.json must include both allow and deny rules from ARCHITECTURE.md.
- settings.json must be valid JSON.
- .claudeignore must cover patterns from ARCHITECTURE.md. If ARCHITECTURE.md Token
  Optimization section specifies "aggressive" .claudeignore, include both domain-specific
  AND generic patterns (node_modules, dist, build, .cache, coverage, lock files). If
  "minimal", include only binary assets and build output.
- If ARCHITECTURE.md Token Optimization section specifies a compaction threshold (e.g.,
  85% for cost-conscious), set `CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE` in settings.json
  env block. If balanced or quality-first, omit the override (let the 95% default apply).
- Target CLAUDE.md line count from ARCHITECTURE.md Token Optimization section (150/200/250).
  Every line must earn its place; cost-conscious environments require extra discipline.
- VCS ignore file (.gitignore or .p4ignore) must exclude `Docs/_working/` so working
  state is not committed. If generating for a Git project, add to .gitignore. For
  Perforce, add to .p4ignore. Document this in GETTING_STARTED.md either way.

Reference templates:
- `Docs/Templates/Core/claude-md.md`
- `Docs/Templates/Core/orchestrator-rule.md`
- `Docs/Templates/Core/routing-rule.md`
- `Docs/Templates/Core/autonomy-rule.md`
- `Docs/Templates/Core/context-management-rule.md`
- `Docs/Templates/Core/self-learning-rule.md`
- `Docs/Templates/Core/error-handling-rule.md`
- `Docs/Templates/Core/settings-json.md`
- `Docs/Templates/Optional/hooks-template.md` (if hooks are specified)

### Pass 2: Agents

**Topic files to load**: `Docs/AgentGuidelines/Topics/` -- 02-agents, 13-opus, 18-cost

Files: All agent definition files in `.claude/agents/`

Key requirements:
- Each agent file must be under 80 lines.
- Every agent must have valid YAML frontmatter with: name, description, model, tools, maxTurns.
- Include disallowedTools where specified in ARCHITECTURE.md.
- The description must state WHEN to delegate to this agent, not just what it does.
- Instructions must include: objective, output format, tool guidance, task boundaries.
- Instructions must include: "Never speculate about files you have not read."
- For Opus agents: include anti-overengineering instruction.
- Long reference content goes at the TOP, operational instructions at the BOTTOM.

Read agent templates from `Docs/Templates/Agents/` for patterns. Select the template closest to each agent being generated.

### Pass 3: Skills

**Topic files to load**: `Docs/AgentGuidelines/Topics/` -- 03-skills, 20-plugins

Files: All skill directories with SKILL.md files, scripts/, and references/ subdirectories

Key requirements:
- Each skill folder uses kebab-case naming.
- NO README.md inside skill folders.
- SKILL.md must be under 500 lines and 5,000 words.
- SKILL.md frontmatter must include: name, description (with 3+ trigger phrases), context, allowed-tools.
- Critical instructions go at the TOP of SKILL.md with ## Critical or ## Important headers.
- Skills with side effects that should not trigger model invocation use `disable-model-invocation: true`.
- Each skill must check its own state independently (composability -- do not assume prior skill execution).
- Skills referencing MCP tools must use fully qualified tool names.
- Include scripts/ for deterministic validation/capture where applicable.
- Include references/ for detailed docs loaded on demand (one level deep only).
- Include a ToC in files over 100 lines.

Read skill templates from `Docs/Templates/Skills/` and core skill templates from `Docs/Templates/Core/` (state-save-skill.md, state-load-skill.md, update-skill.md, health-check-skill.md).

If Pattern F (Codebase Mapping) is active in ARCHITECTURE.md, also read
`Docs/Templates/Skills/map-codebase.md` for the scan-classify-update pipeline
pattern. Adapt the classification heuristics to the project's language and
framework (UE/C++, Unity/C#, or general software).

### Pass 4: Infrastructure

**Topic files to load**: `Docs/AgentGuidelines/Topics/` -- 05-memory, 07-self-learning, 21-rag, 15-testing-validation

Files: Memory scaffold, self-learning scaffold, state management templates, error handling infrastructure

Key requirements:
- Wiki index (`Docs/index.md`) must include the `Status: NEW_ENVIRONMENT` marker for first-run detection.
- Wiki structure must match the tier specified in ARCHITECTURE.md (Lite/Standard/Enterprise).
- `Docs/index.md` is the ONLY wiki file loaded by default. All others are loaded on demand.
- Each wiki page must start with a blockquote summary and include `Last Updated` date.
- Wiki content must be documentation-quality (useful to both Claude and human developers).
- Working memory (`Docs/_working/`) contains transient state:
  - `Docs/_working/state/` must include empty SESSION_SNAPSHOT.json and SESSION_CONTEXT.md.
  - `Docs/_working/sessions/` directory for session history (auto-pruned after 30 days).
  - `Docs/_working/retro/` must include initial monthly log with seed entries.
- Seed entries from ARCHITECTURE.md must be pre-populated and marked `[PATTERN] (pre-seeded)`.
- Auto-memory integration note: explain how the Docs/ wiki relates to ~/.claude auto memory.

Read `Docs/Templates/Core/memory-scaffold.md` for guidance.

### Pass 5: Documentation

**Topic files to load**: `Docs/AgentGuidelines/Topics/` -- 10-integration, 12-user-experience, 21-rag, 23-multi-modal, 18-cost + `Docs/Templates/References/tool-registry.md`

Files: GETTING_STARTED.md, README.md, VERSION.md, cross-reference verification

Key requirements:
- GETTING_STARTED.md is the primary onboarding document. Written in plain language adapted to the user's technical level from GENESIS.md. Must include:
  - What this environment does (1 paragraph)
  - How to start a session (step by step)
  - Available commands with plain-language descriptions
  - 3 suggested first tasks appropriate to the domain
  - Where to find more information
  - How the environment improves with use
  - "Optional Plugins" section: If ARCHITECTURE.md Recommended Plugins section lists
    any plugins, generate an install guide with marketplace setup command
    (`claude /plugin marketplace add anthropics/skills`) followed by install commands
    for each recommended collection. Include a brief description of what each plugin
    adds and when to use it. If ARCHITECTURE.md also mentions relevant bundled skills
    (/code-review, /batch, /debug), list them separately as "Built-in Skills (no install
    needed)" with one-line descriptions. If no plugins are recommended, omit the section.
  - "Refining Your Skills" section: If the environment includes 3+ custom skills AND
    GENESIS.md indicates intermediate+ user, include skill-creator install command
    (`claude install-plugin anthropic/example-skills`) and brief eval workflow:
    run `/skill-creator` in Eval mode to test each custom skill against synthetic
    prompts, review HTML comparison report, iterate with Improve mode. Explain that
    this validates skills actually improve model behavior. If fewer than 3 custom
    skills or beginner user, omit the section.
  - "Monitoring and Optimizing Costs" section, scaled to the efficiency tier from
    ARCHITECTURE.md Token Optimization section:
    - **Cost-conscious**: Full section with `/cost` command usage, RTK install
      instructions (`brew install rtk && rtk init --global` or platform equivalent),
      compaction explanation, .claudeignore maintenance tips, guidance on when to use
      `/clear` between tasks, and `--max-budget-usd` for automation
    - **Balanced**: Brief section mentioning `/cost` for monitoring, RTK as an optional
      tool for reducing token usage, and a note about `.claudeignore` maintenance
    - **Quality-first**: Single paragraph noting `/cost` is available for cost
      awareness, no optimization recommendations
  - If GENESIS.md indicates the user is a beginner with AI or command-line tools (experience level: "Just getting started"), include a "Getting Started with the Terminal" section at the top of GETTING_STARTED.md that explains:
    - How to open a terminal on their operating system
    - How to navigate to their project directory (cd command)
    - How to run `claude` to start the assistant
    - What the assistant prompt looks like and how to type commands
    - Keep this section concise (10-15 lines) and friendly
  - If GENESIS.md indicates the user's primary tools are web/cloud-based (Google Docs, Figma, Notion, etc.) and their project involves no local coding, include a "What This Assistant Can and Cannot Do" note explaining:
    - The assistant works with files on your computer
    - It cannot directly access web-based tools (Google Docs, Figma, etc.) unless MCP servers are configured
    - For web-based tools: describe how to export/download content for the assistant to work with, then upload results back
    - This is NOT a discouragement -- it sets honest expectations so the user is not confused
- VERSION.md must include:
  - Environment version (1.0.0 -- this is the initial version of the generated environment, tracked by the user)
  - Date generated (YYYY-MM-DD)
  - Harness Generator version used (1.1.0) -- this is the version of the Claude Harness Generator that produced this environment
  - Profile used (the starter profile name from GENESIS.md, or "Custom" if the deep interview path was used)
  - Changelog placeholder for the user to track their own modifications
  - Claude Code compatibility note
  - A note that users can re-run `/validate-environment` to check for structural issues, broken references, or staleness in their environment
- README.md: Brief project-level README if one does not already exist (do not overwrite existing).
- Cross-reference verification: Read every generated file and verify:
  - All file paths referenced in CLAUDE.md exist
  - All agent names referenced in routing rules exist
  - All skill names referenced in CLAUDE.md commands exist
  - All memory paths referenced in rules exist
  - Fix any broken references by updating the referencing file

### Hub Shell Pass (hub mode only)

Triggered when the orchestrator invokes the generator with `pass_number: "shell"`.

**Topic files to load**: 01-rules, 05-memory, 08-routing, 11-permissions, 13-opus-specifics, 16-hooks (same as Pass 1 but trimmed -- no hooks beyond PreCompact at the parent).

Files generated at `<target>/`:
- Parent CLAUDE.md (thin orchestrator, 80 lines max). Must include a "Work areas in this setup" section listing each area-slug and its one-line description from HUB_ARCHITECTURE.md. Do NOT list child file paths -- Claude Code discovers them by walking the tree.
- Shared rules only: vocabulary, autonomy, cross-area routing. Under `<target>/.claude/rules/`.
- Shared skills and agents (only those HUB_ARCHITECTURE.md's Shared Skills/Agents section lists). Under `<target>/.claude/skills/` and `<target>/.claude/agents/`.
- Parent settings.json: shared permissions, shared MCP servers, PreCompact hook. Under `<target>/.claude/settings.json`.
- Parent .claudeignore covering hub-wide patterns.

Key requirements:
- Parent CLAUDE.md budget: 80 lines. This leaves ~170 for the longest per-area CLAUDE.md before the cumulative 250-line limit is reached.
- Parent CLAUDE.md must NOT duplicate instructions that belong in per-area CLAUDE.md (area-specific routing, domain vocabulary, etc.).
- Cross-area routing at the parent must only direct the user to switch focus to a different area -- it must not encode any area's internal file structure.

Per-area passes (pass_number `<area-slug>:1` through `<area-slug>:5`) run the normal Pass 1-5 spec above, writing under `<target>/<area-slug>/` instead of `<target>/`. Any component declared in HUB_ARCHITECTURE.md's Shared Skills/Agents is skipped at the area level unless the area's manifest lists it as an override (frontmatter `overrides: <parent-component-name>`).

## Vocabulary Adaptation

Read GENESIS.md to determine the user's technical level and domain vocabulary:
- For technical users: use standard technical terms in generated instructions
- For non-technical users: use plain language even in generated files (say "save your progress" not "/state-save" in user-facing content; technical terms are acceptable in agent/skill instructions that the user will not read directly)
- Use domain-specific terminology where it makes the instructions clearer (e.g., "playtest" for game development, "draft" for knowledge work, "deploy" for DevOps)
- For beginner users: avoid slash command references in user-facing documentation. Instead of "Run /state-save", say "Type 'save my progress' or '/state-save'". Show the natural language alternative first, command second.
- For beginner users: the GETTING_STARTED.md "3 suggested first tasks" should start with the simplest possible task (e.g., "Ask me a question about your project" rather than "Run /health-check to validate your environment").

## File Processing Tool Generation

When ARCHITECTURE.md includes Pattern E (File Processing Pipeline), apply these
rules during the relevant passes:

### Pass 1 (settings.json)
Include ONLY the tool permissions matching the architect's selection in ARCHITECTURE.md.
Reference `Docs/Templates/References/tool-registry.md` for exact permission patterns
and `Docs/Templates/Core/settings-json.md` for the File Processing Tool Configuration
section. Do not merge permissions from tools the architect did not select.

MCP vs CLI decision: prefer the MCP server approach for MarkItDown when the target
environment's settings.json supports mcpServers. Fall back to CLI permissions if MCP
is not suitable (e.g., user indicated uvx is unavailable).

Anti-pattern: Do NOT include Pandoc permissions if the architect did not select Pandoc.
Do NOT include Python permissions for environments that don't use Python-based tools.

### Pass 3 (skills)
If the Inbox/Outbox pattern is active in ARCHITECTURE.md, generate a `/process-inbox`
skill that:
- Scans Inbox/ for new files
- Converts via MarkItDown (MCP tool or CLI, matching the settings.json approach)
- Processes per user instructions
- Outputs results to Outbox/

### Pass 4 (infrastructure)
If Pattern E is active, generate the Inbox/, Outbox/, and Data/ directories with
their README.md files as specified in `Docs/Templates/Core/memory-scaffold.md`
(Inbox/Outbox/Data Scaffolding section).

### Pass 1 (routing rules)
If ARCHITECTURE.md specifies dual-mode file processing, generate the quick/quality/data
mode routing rule from `Docs/Templates/Core/routing-rule.md` (Dual-Mode File Processing
Pattern section). Omit modes whose tools are not selected (e.g., no quality mode without
Pandoc, no data mode without openpyxl/ImportExcel).

### Pass 5 (GETTING_STARTED.md)
If Pattern E is active, include a "File Processing Setup" section with:
- One-time install commands for selected tools only (do not list tools the architect excluded)
- How to use the Inbox/Outbox workflow (if those directories were scaffolded)
- What file formats are supported by the selected tools
- If Pandoc was selected, explain why it is needed (formatted output quality) and
  how to install it (`winget install pandoc` on Windows, `brew install pandoc` on macOS)

## Brand Setup Generation

When ARCHITECTURE.md includes Pattern E with brand guidance sub-pattern, apply
these additional rules per pass. Brand setup is conditional on BOTH Pattern E
being active AND brand requirements being flagged in intake.

### Pass 4 (Infrastructure)
Generate the Brand/ directory structure:
- `Brand/README.md` -- explains what goes in each subfolder, how auto-update works
  (use template from memory-scaffold.md)
- `Brand/Templates/README.md` -- explains supported template types (.docx, .pptx)
- `Brand/Guidelines/README.md` -- explains supported guideline formats
- Do NOT generate a placeholder brand-rules.md -- it should only be created when
  the user provides actual brand assets

### Pass 3 (Skills)
Generate a `/update-brand` skill or integrate into the existing `/process-inbox` skill:
- Scans Brand/Guidelines/ and Brand/Templates/ for files
- Converts guideline documents via MarkItDown
- Analyzes for: tone/voice, terminology, color palette, fonts, required sections,
  headers, disclaimers, formatting conventions
- Writes or updates Brand/brand-rules.md with:
  - Source Tracking section (file names + last modified dates)
  - Extracted rules organized by category
- Preserves any manual edits the user made to brand-rules.md (merge, don't overwrite)

### Pass 1 (Routing rules)
The quality mode routing should include brand check logic:
- Before generating formatted output, check if Brand/ exists
- If Brand/brand-rules.md exists, check Source Tracking for staleness:
  - Compare listed file modification dates against actual file system dates
  - Check for files in Brand/ not listed in Source Tracking
- If stale or missing: trigger brand analysis (run /update-brand or inline analysis)
- Then apply brand rules to content and use brand templates for Pandoc --reference-doc

### Pass 5 (GETTING_STARTED.md)
When brand support is included, add a section:
```markdown
## Brand Guidelines (Optional)

To produce branded documents that match your organization's style:

1. Drop your brand guide (PDF, Word, etc.) into the `Brand/Guidelines/` folder
2. Drop your document templates (.docx, .pptx) into the `Brand/Templates/` folder
3. Your assistant will automatically read these and apply your brand standards

When you update brand assets, the assistant detects changes and refreshes
its brand knowledge automatically.
```

### Brand Anti-patterns
- Do NOT generate Brand/ if the architect did not flag brand requirements
- Do NOT pre-fill brand-rules.md with generic content
- Do NOT hardcode specific brand rules -- the whole point is auto-extraction
  from user-provided assets

## Opus 4.8 / 4.7 Prompt Engineering in Generated Content

Opus 4.8 (`claude-opus-4-8`, released 2026-05-28) is the current flagship and the default
Claude Code model; 4.7 remains supported and these principles apply unchanged to both
(and to 4.6).
All generated files that contain instructions for Claude must follow these:

- State purpose directly. No role-setting ("Act as...", "You are a senior...").
- State each instruction once. Opus maintains consistency without repetition.
- Include intent behind constraints (WHY, not just WHAT).
- Use few-shot examples over exhaustive rule lists where appropriate.
- Write instructions LITERALLY. Opus 4.7 does not silently generalize -- be explicit about
  scope ("for every file matching X", not "for similar files"). Re-baseline scaffolding
  inherited from 4.6 prompts (e.g., "double-check before returning", "think carefully
  first") -- often unnecessary on 4.7 and can degrade output.
- Include anti-overengineering instructions for Opus agents. Opus 4.7 is less prone than
  4.6 but occasional overbuilding still occurs on open-ended asks.
- Dial back aggressive tool-triggering language. Opus does not need "ALWAYS use X tool" --
  it follows instructions reliably with moderate emphasis. 4.7 defaults to fewer tool
  calls; explicitly request delegation/parallelism when you want it.
- Use XML tags for structured sections where they aid parsing.
- Do NOT emit `temperature`, `top_p`, `top_k`, or `budget_tokens` for 4.7 projects (API
  returns 400). Control behavior via `effort` (low/medium/high/xhigh/max) and adaptive
  thinking (`thinking: {type: "adaptive"}`) only.
- Recommend `effort: xhigh` as the starting point for Claude Code coding/agentic sessions
  on 4.7 (this matches the Claude Code default on 4.7).

## Anti-Overengineering

Generate ONLY the files listed in the component manifest for the current pass. Do not:
- Add extra agents not in ARCHITECTURE.md
- Add extra rules not in ARCHITECTURE.md
- Add extra skills not in ARCHITECTURE.md
- Create additional infrastructure files not specified
- Add "nice to have" features the user did not ask for
- Over-document with redundant README files

For each file you generate, verify it appears in the component manifest. If it does not, do not write it.

## Progress Tracking

Update `<target_path>/Docs/Environment/GENERATION_PROGRESS.md` BEFORE starting each pass (mark IN_PROGRESS) and AFTER completing each pass (mark COMPLETE). This enables the orchestrator to resume from the last completed pass if generation is interrupted.

On your first invocation (pass 1, or the shell pass in hub mode), create the file with all passes listed. On subsequent invocations, read the existing file and update only your pass's status.

The file must use this exact format so the orchestrator can parse it for resume detection:

```markdown
# Generation Progress

## Pass 1 (Foundation): COMPLETE
Files generated: [list]
Completed: YYYY-MM-DD HH:MM

## Pass 2 (Agents): COMPLETE
Files generated: [list]
Completed: YYYY-MM-DD HH:MM

## Pass 3 (Skills): IN_PROGRESS
Started: YYYY-MM-DD HH:MM

## Pass 4 (Infrastructure): PENDING

## Pass 5 (Documentation): PENDING
```

Hub-mode format (single file, tracks shell pass plus every per-area pass):

```markdown
# Generation Progress (Hub)

## Shell: COMPLETE
Files generated: [list]
Completed: YYYY-MM-DD HH:MM

## Area 'policy' Pass 1 (Foundation): COMPLETE
...
## Area 'policy' Pass 5 (Documentation): COMPLETE
## Area 'audit-tool' Pass 1 (Foundation): IN_PROGRESS
## Area 'audit-tool' Pass 2 (Agents): PENDING
...
```

Status values:
- `PENDING` -- not yet started (initial state for all passes)
- `IN_PROGRESS` -- pass has started but not yet finished
- `COMPLETE` -- pass finished successfully

The status keyword must appear on the same line as the pass heading, after the colon. This is the line the orchestrator parses to determine resume points.

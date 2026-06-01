# 3. Skills

### 3.1 Five Canonical Patterns

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md, platform-agent-patterns.md | Tier 1
- **Recommendation**: Choose the pattern matching your skill's use case:
  1. **High-level guide with references**: SKILL.md contains quick start + links to detailed
     files. Claude loads referenced files only when needed.
  2. **Domain-specific organization**: Separate reference files by domain (finance.md,
     sales.md). Claude loads only the relevant domain file.
  3. **Conditional details**: Basic content in SKILL.md, linked advanced content for edge
     cases.
  4. **Workflow + feedback loop**: Checklist with validation steps. Agent tracks progress,
     iterates until validation passes.
  5. **Script-driven execution**: SKILL.md orchestrates execution of bundled scripts. Scripts
     run without loading source into context (only output consumes tokens).
- **Anti-pattern**: Putting everything in SKILL.md without using the directory structure.
  A 2000-line SKILL.md wastes tokens on sections irrelevant to the current invocation.

### 3.2 Progressive Disclosure

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md, context-engineering.md | Tier 1
- **Recommendation**: Skills use 3-level progressive disclosure:
  - Level 1 (always loaded, ~100 tokens): Metadata -- name + description from YAML frontmatter
  - Level 2 (loaded when triggered, target <500 lines): SKILL.md body
  - Level 3+ (loaded as needed, unlimited): Referenced files, scripts, examples

  Directory structure:
  ```
  skill-name/           # kebab-case ONLY
    SKILL.md            # Core instructions (<500 lines, <5000 words)
    scripts/            # Deterministic validation/capture scripts
    references/         # Detailed docs loaded on demand
  ```
  Keep references ONE level deep from SKILL.md. Bad: SKILL.md -> advanced.md -> details.md.
  Good: SKILL.md -> advanced.md, SKILL.md -> reference.md (all direct).
  For reference files >100 lines, include a table of contents at the top.
- **Anti-pattern**: Deeply nested file references. Claude partially reads files referenced
  from other referenced files. Keep the reference graph flat and one level deep.

### 3.3 Description Triggers

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md, platform-agent-patterns.md | Tier 1
- **Recommendation**: The description field is the critical discovery mechanism. Claude uses
  it to choose from 100+ available skills. Format:
  ```
  [What it does]. [When to use it with 3+ trigger phrases]. [Negative triggers if ambiguity risk].
  ```
  Example: "Captures current session state for later restoration. Use when the user says
  'save progress', 'save state', 'save session', 'I need to take a break', or before using
  /clear. Do NOT use for saving files or committing code."

  Requirements:
  - Max 1024 chars
  - Third person ("Processes..." NOT "I can help you..." or "You can use this to...")
  - Include both WHAT and WHEN
  - Include 3+ trigger phrases covering natural variations
  - Include negative triggers when ambiguity risk exists (e.g., "save" could mean save state
    or save file)
- **Anti-pattern**: Vague descriptions like "Helps with documents" or "Processes data."
  These fail at discovery when Claude must choose among many skills.

### 3.4 Degrees of Freedom Matching

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md, guardrails.md | Tier 1
- **Recommendation**: Match instruction specificity to task fragility:
  - **High freedom** (text instructions): Creative tasks, multiple valid approaches, decisions
    depend on context. Example: code review guidelines.
  - **Medium freedom** (pseudocode/scripts with params): Preferred pattern exists but
    variation is acceptable. Example: deployment checklist with configurable steps.
  - **Low freedom** (exact scripts, few params): Operations are fragile, consistency is
    critical, or specific sequence required. Example: database migration scripts, destructive
    operations.

  Analogy: narrow bridge with cliffs (low freedom) vs. open field (high freedom). The degree
  of freedom should match the consequences of deviation.
- **Anti-pattern**: Using high freedom for critical operations (database migrations, production
  deployments) or low freedom for creative tasks (brainstorming, drafting). Mismatched freedom
  either creates dangerous flexibility or unnecessary rigidity.

### 3.5 Script Bundling

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md | Tier 1
- **Recommendation**: Bundle deterministic scripts in the `scripts/` directory within skill
  folders. Benefits:
  - More reliable than generated code
  - Save tokens (code never enters context, only output)
  - Save time (no code generation step)
  - Ensure consistency across uses

  Make execution intent clear: "Run `scripts/validate.py` to check..." (execute) vs.
  "See `scripts/validate.py` for the algorithm..." (read as reference). Execution is
  preferred for most utility scripts.

  Error handling in scripts: handle errors explicitly, provide fallback behavior, document
  all configuration constants (no "voodoo constants" -- magic numbers without explanation).
- **Anti-pattern**: Having Claude generate code each invocation for tasks that could be
  deterministic scripts. This wastes tokens and introduces non-determinism.

### 3.6 Composability

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md | Tier 1
- **Recommendation**: Each skill should check state independently and not assume prior skill
  execution. Skills must be usable in any order. State-save should not assume state-load ran
  first. Health-check should not assume update ran recently.

  For skills with side effects, use `disable-model-invocation: true` so only explicit user
  invocation triggers them. This prevents Claude from autonomously running potentially
  destructive workflows.
- **Anti-pattern**: Building skill chains where skill B assumes skill A has already run.
  Users invoke skills in unexpected orders, and crashed sessions lose intermediate state.

### 3.7 Portability and Naming

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md, claude-code-docs.md | Tier 1
- **Recommendation**: Skill names: max 64 chars, lowercase letters/numbers/hyphens only.
  No XML tags, no reserved words ("anthropic", "claude"). Prefer gerund form
  (processing-pdfs, analyzing-data). Use forward slashes in all paths, even on Windows.

  No README.md inside skill folders. The SKILL.md body serves as documentation.

  Critical instructions go at TOP of SKILL.md with `## Critical` or `## Important` headers.
  Claude reads from top down; late-appearing critical instructions may be missed.
- **Anti-pattern**: Vague names (helper, utils, tools). Windows-style paths (backslash).
  README.md alongside SKILL.md (creates confusion about which file is primary).

### 3.8 Agent Skills Open Specification

- **Established**: 2026-03
- **Source**: agentskills.io/specification, github.com/anthropics/skills | Tier 1
- **Recommendation**: Claude Code skills follow the Agent Skills open specification
  (agentskills.io), which works across multiple AI tools. Generated skills should
  conform to the spec for maximum portability:

  Required frontmatter: `name` (max 64 chars, lowercase+hyphens, must match directory
  name) and `description` (max 1024 chars). Optional: `license`, `compatibility`
  (max 500 chars, environment requirements), `metadata` (key-value pairs),
  `allowed-tools` (space-delimited pre-approved tools).

  Claude Code extends the spec with additional frontmatter:
  - `disable-model-invocation: true`: Only user can invoke (use for side-effect skills)
  - `user-invocable: false`: Only Claude can invoke (background knowledge)
  - `context: fork`: Run in isolated subagent context (honored as of v2.1.101)
  - `context: agent`: Run in a long-lived agent context (honored as of v2.1.101)
  - `agent`: Which subagent type for forked context (Explore, Plan, general-purpose, or custom)
  - `model`: Override model for this skill
  - `effort`: Set model effort level when skill is invoked (added v2.1.76/v2.1.84 -- e.g.,
    `effort: low` for fast confirmation skills, `effort: xhigh` for complex analysis skills)
  - `argument-hint`: Autocomplete hint (e.g., `[issue-number]`)
  - `hooks`: Skill-scoped lifecycle hooks
  - `paths:`: YAML list of globs (v2.1.84+)
  - `disallowed-tools:`: Remove specific tools from the model WHILE the skill is active
    (v2.1.152). Complements `allowed-tools` (which pre-approves) -- use this to narrow the
    model's surface during a focused skill (e.g., a read-only analysis skill that disallows
    Write/Edit).

  Skill reload: `/reload-skills` re-scans skill directories without restarting the session
  (v2.1.152); a SessionStart hook can trigger the same via `reloadSkills: true`. The
  `skillOverrides` setting (v2.1.129) controls visibility per skill: `"off"` (hidden from
  model and `/`), `"user-invocable-only"` (hidden from model only), `"name-only"` (collapse
  the description to save context).

  String substitutions: `$ARGUMENTS` (all args), `$ARGUMENTS[N]` or `$N` (positional),
  `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}`.

  Dynamic context injection: `!`command`` syntax runs shell commands before skill content
  is sent to Claude, replacing the placeholder with command output. Useful for injecting
  live data (git status, PR info, API responses) into skill prompts.

  Validate skills with: `skills-ref validate ./my-skill` (from agentskills/agentskills).

- **Anti-pattern**: Using non-spec frontmatter fields that only work in Claude Code when
  the skill is intended for cross-platform use. If portability matters, stick to the base
  spec fields and note Claude Code extensions separately.

### 3.9 Bundled Skills and Official Skill Ecosystem

- **Established**: 2026-03; updated 2026-05-31
- **Source**: code.claude.com/docs/en/skills, github.com/anthropics/skills | Tier 1
- **Recommendation**: Claude Code ships bundled skills that are always available:
  - `/code-review`: Reports correctness bugs in recently changed files at the chosen
    effort level. `--fix` applies findings; `--comment` posts them as inline PR comments.
    Renamed from `/simplify` (v2.1.147); the old cleanup-only behavior was removed and the
    old `/simplify` invocation no longer works.
  - `/batch <instruction>`: Orchestrates large-scale parallel changes across a codebase.
    Decomposes work into 5-30 units, each in an isolated git worktree with its own PR.
  - `/debug [description]`: Troubleshoots the current Claude Code session via debug log.
  - `/claude-api`: Loads Claude API/SDK reference. Auto-activates on Anthropic SDK imports.

  For generated environments: document relevant bundled skills in GETTING_STARTED.md.
  These do not need to be installed or configured. The `/batch` skill is particularly
  valuable for large codebase migrations and refactors -- mention it in environments
  for projects with 50k+ lines of code.

  Anthropic also maintains an official skills repository (github.com/anthropics/skills)
  with installable skill collections. See section 20.3 for the full catalog and 20.4
  for the matching rules used during environment generation.

  The skill-creator skill from the official repository is especially relevant for users
  who want to extend their generated environment. It provides a complete workflow for
  creating, testing (with eval framework), benchmarking, and optimizing custom skills
  including description optimization for triggering accuracy.

- **Anti-pattern**: Reimplementing functionality that bundled skills already provide.
  Check bundled skills before generating custom equivalents.

### 3.10 Skill Validation with Eval Framework

- **Established**: 2026-03
- **Source**: github.com/anthropics/skills/tree/main/skills/skill-creator,
  tessl.io/blog/anthropic-brings-evals-to-skill-creator, hboon.com | Tier 1 + Tier 2
- **Recommendation**: The skill-creator plugin provides four modes (Create, Eval,
  Improve, Benchmark) backed by four sub-agents (Executor, Grader, Comparator,
  Analyzer). The eval framework generates synthetic test prompts with assertion
  sets, runs skills against them, grades outputs, and produces HTML comparison
  reports for side-by-side review of old vs new versions.

  Key principle: **"Unvalidated context is useless."** Skills are instructions to
  an LLM. Without testing whether the model actually follows those instructions,
  skill authors accumulate redundant or misleading guidance. Evals close the loop
  by measuring whether skills improve behavior compared to the baseline (no skill).

  **For environment generation**: After the component-generator produces custom
  skills (Pass 3), recommend running skill-creator's Eval mode as a post-generation
  quality gate. This catches issues structural validation misses:
  - Trigger phrases that don't actually activate the skill
  - Instructions the model ignores or misinterprets
  - Edge cases where the skill produces wrong behavior
  - Skills that score identically to the no-skill baseline (indicating the
    instructions add no value)

  **For the Harness Generator's own skills**: The Harness Generator's skills (state-save,
  state-load, create, update, clean, etc.) should be periodically benchmarked
  with skill-creator to verify they perform as documented.

  **Eval test structure**: JSON files pairing prompts with assertions. Each
  assertion is a specific, verifiable check. The Comparator does blind A/B
  testing. If both old and new versions score identically, the test cases need
  to be harder or the skill is not adding value.

  Include skill-creator install command in GETTING_STARTED.md for generated
  environments when the user is intermediate+ and the environment includes 3+
  custom skills: `claude install-plugin anthropic/example-skills`

- **Anti-pattern**: Generating skills without any validation that they actually
  improve model behavior. Structural checks (frontmatter, line count, triggers)
  are necessary but insufficient -- they verify form, not function.

### 3.11 Skill Composition (Pipeline Skills)

- **Established**: 2026-03
- **Source**: Community workflow patterns (YouTube research + NotebookLM + Obsidian
  pipeline), skill-creator superskill pattern | Tier 2
- **Recommendation**: When a user's workflow chains multiple external tools in
  sequence (tool A produces output -> tool B consumes it -> structured result),
  generate a **pipeline skill** (sometimes called a "superskill") that orchestrates
  the full flow within a single skill invocation.

  **This does NOT violate section 3.6 (Composability).** Section 3.6 says skills
  should not *assume* other skills ran first. A pipeline skill is different: it
  explicitly invokes the steps internally, not by calling other skills. Each step
  handles its own state. The composability rule still applies -- the pipeline skill
  must work standalone without assuming any prior skill execution.

  **Pattern: Pipeline Skill Architecture**

  A pipeline skill has 3 layers:
  1. **Tool wrapper steps**: Each external tool gets a dedicated step that handles
     invocation, error checking, and output formatting. These are internal to the
     skill, not separate skills.
  2. **Data flow logic**: Steps define what output from step N becomes input for
     step N+1. Use intermediate files in `Docs/_working/pipelines/<skill-name>/`
     (auto-cleaned on completion).
  3. **Composition orchestration**: The skill's main flow invokes steps in sequence,
     handles partial failures (retry or skip with warning), and produces a unified
     result.

  **When to generate pipeline skills** (all conditions must be met):
  - Intake describes a workflow with 2+ external tools producing sequential output
  - The user repeats this workflow regularly (not a one-time task)
  - Each tool step is non-trivial (more than a single CLI command)
  - The user is intermediate+ (beginners need simpler individual skills)

  **When NOT to generate pipeline skills**:
  - When a single skill with bash commands in sequence suffices
  - When the user described the workflow but doesn't repeat it
  - When the tools don't have a clear data flow (they're parallel, not sequential)

  **Example**: User says "I research YouTube videos, send findings to NotebookLM
  for analysis, then structure the results for my knowledge base." Generate a
  `/research-pipeline` skill with steps: (1) search via yt-dlp, (2) format
  results as NotebookLM input, (3) invoke NotebookLM processing, (4) structure
  output for knowledge base. Each step is a section in SKILL.md with its own
  error handling.

- **Anti-pattern**: Creating separate skills for each pipeline step and expecting
  users to invoke them in order. Users will forget steps, invoke out of order,
  or lose intermediate state between invocations. If steps always run together,
  they belong in one skill.

### 3.12 CLI Tool Wrapping as Skill Generation

- **Established**: 2026-03
- **Source**: Community patterns, tool-catalog.md generalization | Tier 2
- **Recommendation**: Any CLI tool a user mentions during intake can potentially
  be wrapped in a skill with structured input/output. The tool-catalog.md covers
  specific known tools, but the **pattern** is general:

  **CLI-to-Skill Bridge Pattern**:
  1. **Identify the tool** from intake ("I use yt-dlp", "I use ffmpeg", "I use
     pandoc", "I use jq to process JSON")
  2. **Determine the I/O contract**: What goes in (query, file, URL)? What comes
     out (structured data, file, text)?
  3. **Generate the skill**: SKILL.md with steps that invoke the CLI tool via Bash,
     parse the output, and present it in a structured format
  4. **Include install verification**: Step 1 of the skill checks if the tool is
     installed (`which <tool>` or equivalent), offers install instructions if not
  5. **Add to settings.json**: `Bash(<tool> *)` permission for the generated skill

  **When the architect detects an unknown CLI tool in GENESIS.md** (not in the
  tool registry): Generate a lightweight wrapper skill rather than just documenting
  the tool in GETTING_STARTED.md. A skill with structured I/O is more useful than
  "run this command manually."

  **Intake signal**: The repeatable-process probe ("Describe one workflow start to
  finish") often reveals CLI tools. The architect should parse tool names from the
  workflow description and generate wrapper skills for each.

- **Anti-pattern**: Only wrapping tools that are in the tool registry. The registry
  tracks *recommended* tools; the CLI-wrapping pattern works for *any* tool the
  user already uses. Also: generating overly complex skills for simple one-liner
  CLI commands -- if `jq '.data' file.json` is the entire workflow, a skill adds
  no value.

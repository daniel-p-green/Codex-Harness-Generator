# Upgrade Checklist

Loaded by the upgrade-analyzer agent. Contains the full best-practice audit
protocol for analyzing existing environments and producing upgrade
recommendations.

Unlike EnvironmentValidation.md (structural correctness), this checklist
evaluates whether an environment follows best practices and is optimally
configured for its use case.

---

## How to Use This Checklist

For each check:
1. Read the relevant file(s) from the target environment
2. Evaluate against the criteria described
3. Record: gap description, best practice reference, effort tier, affected files, specific changes
4. Classify the recommendation as Quick Win, Medium, or Large based on the effort tier

Effort tiers:
- **Quick Win**: 1-2 file edits, no new files, no structural changes
- **Medium**: New files needed or 3-5 file edits, no architectural changes
- **Large**: Structural changes, new components, or significant rewrites

If a check passes (no gap found), record it in the Deferred section of the report.

---

## Part 1 -- Foundation Audit (7 checks)

### F1: CLAUDE.md Line Count

Single environments: Read CLAUDE.md and count lines.

Hub environments: count parent CLAUDE.md AND the longest per-area CLAUDE.md. The cumulative (parent + longest-child) is the number that matters, because both are loaded when working inside that area.

| Condition | Recommendation |
|---|---|
| Single > 250 lines OR hub cumulative > 250 lines | FAIL: Must split. Move detailed instructions into rule files or agent prompts. For hubs: first try trimming the parent (80-line target) before touching areas. |
| Single 200-250 or hub cumulative 200-250 | WARN: Approaching limit. Identify sections that could move to rules. |
| Hub parent > 80 lines | WARN: Parent too thick; shared rules should absorb detail. |
| Below all thresholds | PASS |

Effort: Quick Win (move sections) or Medium (restructure into rules)
Reference: Topics/01-rules.md, Generation Standards item 1, architecture-guide.md Hub Architecture

### F2: Intent-Behind-Rules Coverage

Read CLAUDE.md and all rule files. For each constraint or instruction:
- Does it explain WHY, not just WHAT?
- Bad: "Never modify files outside the project directory."
- Good: "Never modify files outside the project directory -- changes outside the project are irreversible and may affect other work."

Sample at least 10 constraints across all files. Calculate the percentage that include intent.

| Condition | Recommendation |
|---|---|
| < 50% with WHY | Recommend adding intent to all major constraints |
| 50-79% with WHY | Recommend adding intent to remaining constraints |
| >= 80% with WHY | PASS |

Effort: Quick Win (add parenthetical reasons to existing rules)
Reference: Topics/13-opus-specifics.md, Generation Standards Prompt Engineering

### F3: Role-Setting Prompt Scan

Search all generated files for role-setting patterns:
- "Act as a..."
- "You are a [role/title] who..."
- "You are a senior..."
- "You are an expert..."
- "Pretend to be..."
- "Your role is..."
- "Imagine you are..."

Acceptable patterns (not role-setting):
- "You help users with [task]" (states purpose)
- "This environment manages [domain]" (states function)

| Condition | Recommendation |
|---|---|
| Any role-setting found | Replace with direct purpose statements |
| None found | PASS |

Effort: Quick Win (reword affected lines)
Reference: Topics/13-opus-specifics.md, Generation Standards Prompt Engineering

### F4: Overemphasis Scan

Count occurrences of high-emphasis words across all rule files and CLAUDE.md:
CRITICAL, MUST, ALWAYS, NEVER, IMPORTANT, REQUIRED, MANDATORY, ESSENTIAL

Exclude occurrences inside code blocks and file headers.

| Condition | Recommendation |
|---|---|
| > 15 total | Reduce emphasis; Opus 4.6/4.7 follow moderate instructions reliably |
| 10-15 total | Review each usage -- keep only where truly critical |
| < 10 total | PASS |

Effort: Quick Win (tone down individual words)
Reference: Topics/13-opus-specifics.md (Opus does not need aggressive emphasis;
4.7 in particular interprets instructions literally and may overcomply with
CAPS emphasis)

### F5: settings.json Deny Rule Coverage

Read settings.json. Check that deny rules cover:
- Destructive bash commands: rm -rf, sudo, format, del /f
- Sensitive file reads: .env, credentials, secrets, private keys
- Force push: git push --force, git push -f
- Branch deletion: git branch -D, git branch --delete --force

| Condition | Recommendation |
|---|---|
| Missing 2+ categories | Add deny rules for missing categories |
| Missing 1 category | Add the missing deny rule |
| All covered | PASS |

Effort: Quick Win (add entries to deny array)
Reference: Topics/11-permissions.md, Generation Standards item 6

### F6: Agent Teams Enablement

Check settings.json for `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: "1"` in the env block. Check the orchestrator rule for an execution mode decision matrix (sequential / parallel / teams).

| Condition | Recommendation |
|---|---|
| No env block or no Agent Teams flag | Add env block with Agent Teams enablement |
| Flag present but no decision matrix | Add decision matrix to orchestrator rule |
| Both present | PASS |

Note: On Windows, document that split-pane mode does not work; use in-process mode.

Effort: Quick Win (add env setting) or Medium (add decision matrix section)
Reference: Topics/04-teams.md, Generation Standards Execution Mode

### F7: Autocompact Configuration

Check settings.json or CLAUDE.md for autocompact threshold configuration.

| Condition | Recommendation |
|---|---|
| No autocompact mention | Recommend setting autocompact threshold (suggest 85%) |
| Threshold < 80% | Warn: low threshold wastes context |
| Threshold >= 80% | PASS |

Effort: Quick Win (add to settings.json or CLAUDE.md)
Reference: Topics/05-memory.md

---

## Part 2 -- Agent and Skill Audit (6 checks)

### A1: Model Selection Review

Read all agent files. Check the `model` field in frontmatter.

| Pattern | Recommendation |
|---|---|
| All agents use opus | Recommend Sonnet for implementer/explorer agents (5x cost savings) |
| No model specified on any agent | Add explicit model selection with rationale |
| Mix of opus/sonnet appropriate to role | PASS |

Opus is for: orchestrator, planner, complex debugger, reviewer. (Opus 4.7 current)
Sonnet is for: implementer, validator, explorer, formatter.
Pairing Sonnet implementation with Opus review creates cross-model cognitive diversity.

Effort: Quick Win (change model field in frontmatter)
Reference: Topics/02-agents.md, Generation Standards Model Selection Policy

### A1b: Opus 4.7 Migration Readiness

Environments pinned to Opus 4.6 (via model aliases, frontmatter `model:`, or
ANTHROPIC_DEFAULT_OPUS_MODEL env var) can migrate to 4.7. Scan for 4.7-incompatible
patterns in settings, agent bodies, skill bodies, and any embedded API snippets:

| Signal | Recommendation |
|---|---|
| `temperature`, `top_p`, `top_k` set to non-default values | REMOVE (API 400 on 4.7); tune via `effort` |
| `thinking: {type: "enabled", budget_tokens: N}` | Replace with `thinking: {type: "adaptive"}` + `effort` |
| `MAX_THINKING_TOKENS` env var used to tune Opus | Remove; switch to `effort` level or `/effort` command |
| 4.6-era scaffolding like "double-check before returning", "think carefully first" | Try removing and compare; often unnecessary on 4.7 |
| Emphatic language (CRITICAL, MUST, ALWAYS) stacked | 4.7 reads literally; tone down |
| `max_tokens` hardcoded at 4k/8k in agentic API examples | Raise to 64k+ for 4.7 agentic runs |
| CLAUDE.md/settings recommendations for `effort: medium` as default | Update to `effort: xhigh` for coding/agentic; `effort: high` for general |

Effort: Medium (multiple files typically affected)
Reference: Topics/13-opus-specifics.md (full 4.7 guidance),
platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7

### A2: maxTurns Presence

Read all agent files. Check for `maxTurns` in frontmatter.

| Condition | Recommendation |
|---|---|
| Any agent missing maxTurns | Add maxTurns (prevents runaway execution) |
| All agents have maxTurns | PASS |

Suggested values: explorers 15-25, implementers 40-60, reviewers 20-30.

Effort: Quick Win (add one frontmatter field per agent)
Reference: Topics/02-agents.md, Generation Standards Agent Rules

### A3: disallowedTools for Reviewers

Read all agent files. Identify agents whose name or description indicates review, validation, or analysis. Check for `disallowedTools` in frontmatter.

| Condition | Recommendation |
|---|---|
| Reviewer/validator without disallowedTools | Add disallowedTools: [Edit, Write] for read-only agents |
| All reviewers have appropriate restrictions | PASS |

Effort: Quick Win (add one frontmatter field)
Reference: Topics/02-agents.md, Generation Standards Agent Rules

### A4: Anti-Oversubagenting

Read the orchestrator rule or CLAUDE.md. Check for instructions that prevent excessive agent delegation (e.g., "handle simple questions directly", "delegate only for complex multi-step tasks").

| Condition | Recommendation |
|---|---|
| No anti-oversubagenting guidance | Add routing guidance for simple vs complex requests |
| Present | PASS |

Effort: Quick Win (add a sentence to orchestrator rule)
Reference: Topics/08-routing.md

### A5: Skill Description Quality

Read all SKILL.md files. For each, check:
1. Written in third person ("Captures state..." not "I capture state...")
2. Contains 3 or more trigger phrases
3. Contains negative triggers where name is ambiguous
4. Under 1024 characters
5. Format: [What] + [When/triggers] + [Capabilities]

| Condition | Recommendation |
|---|---|
| Any skill fails 2+ criteria | Rewrite skill description |
| Any skill fails 1 criterion | Adjust the specific issue |
| All skills pass | PASS |

Effort: Quick Win (edit description strings)
Reference: Topics/03-skills.md, Quality Gates Skill Description

### A6: Skill Progressive Disclosure

Read all SKILL.md files. Count lines for each.

| Condition | Recommendation |
|---|---|
| Any SKILL.md > 200 lines without scripts/ or references/ | Split into SKILL.md + scripts/ + references/ |
| Any SKILL.md > 500 lines | Must split (hard limit) |
| All appropriately structured | PASS |

Effort: Medium (create subdirectories, move content)
Reference: Topics/03-skills.md, Generation Standards Skill Rules

---

## Part 3 -- Memory and State Audit (6 checks)

### M1: Wiki Staleness Tracking

Check for staleness detection mechanisms:
- `Docs/_working/state/WIKI_WATERMARK.json` exists
- Wiki pages in Docs/ have `Last Updated` fields
- Any hook or skill that checks wiki freshness

| Condition | Recommendation |
|---|---|
| No staleness tracking at all | Add WIKI_WATERMARK.json and Last Updated fields |
| Partial (only dates, no watermark) | Add watermark for automated detection |
| Full tracking | PASS |

Effort: Medium (create watermark file, add dates to wiki pages)
Reference: Topics/05-memory.md, Generation Standards item 18

### M2: Wiki File Size Discipline

Read `Docs/index.md` and measure line count. Glob for all `.md` files under `Docs/` (excluding `_working/` and `Environment/`). Measure each.

| Condition | Recommendation |
|---|---|
| index.md > 100 lines | Split index into sub-indexes per area |
| Any content file > 300 lines | Split into sub-pages |
| All within limits | PASS |

Effort: Medium (restructure wiki files)
Reference: Topics/05-memory.md

### M3: Working Memory VCS Exclusion

Check that `Docs/_working/` is excluded from version control:
- Git: grep for `Docs/_working/` or `_working/` in `.gitignore`
- Perforce: grep for `Docs/_working/` in `.p4ignore`
- If no VCS ignore file exists, check GETTING_STARTED.md for documentation

| Condition | Recommendation |
|---|---|
| Not excluded from VCS | Add exclusion pattern to VCS ignore file |
| Excluded | PASS |

Effort: Quick Win (add one line to .gitignore or .p4ignore)
Reference: Topics/05-memory.md (Section 5.9), Generation Standards Required VCS Exclusion

### M4: State File Growth Bounds

Check for state file size management:
- Read state-save skill: does it cap SESSION_CONTEXT.md at ~100 lines?
- Read state-save skill: does it archive or prune old state files?
- Check `Docs/_working/retro/`: are entries bounded (e.g., auto-archive after 50)?

| Condition | Recommendation |
|---|---|
| No growth bounds anywhere | Add pruning logic to state-save, cap retro entries |
| Partial bounds (some files managed, others not) | Extend bounds to all state files |
| All managed | PASS |

Effort: Medium (edit state-save skill, add pruning logic)
Reference: Topics/05-memory.md, Generation Standards item 17

### M5: Memory Tier Appropriateness

If GENESIS.md exists, check the team size and project complexity.
Read the wiki structure and compare against the tier.

| Project Scale | Expected Tier |
|---|---|
| Solo, simple project | Lite (flat Docs/, 3-5 wiki pages) |
| Solo/small team, moderate project | Standard (Areas/, Decisions/, 5-15 pages) |
| Large team or enterprise | Enterprise (full hierarchy, Roles/, 15+ pages) |

| Condition | Recommendation |
|---|---|
| Tier is overkill for project scale | Simplify: remove unused wiki sections |
| Tier is too simple for scale | Expand: add missing wiki areas |
| Appropriate | PASS |

Effort: Medium (restructure wiki) or Large (full tier migration)
Reference: Topics/05-memory.md

### M6: State-Save / State-Load Existence and Symmetry

Check that both skills exist. If both exist, verify symmetry:
- state-save writes to SESSION_SNAPSHOT.json and SESSION_CONTEXT.md
- state-load reads the same files
- state-load includes drift detection

| Condition | Recommendation |
|---|---|
| One or both missing | Create the missing skill(s) |
| Both exist but asymmetric | Fix asymmetry (align file paths and fields) |
| Both exist and symmetric | PASS |

Effort: Medium (create skill) or Quick Win (fix asymmetry)
Reference: Topics/05-memory.md, Generation Standards items 7-8

---

## Part 4 -- Hook and Automation Audit (4 checks)

### H1: Stop Hook Self-Review

Check if a Stop hook is configured that performs self-review of modified files before accepting work. This is especially valuable for code-producing projects.

Check settings.json hooks or `.claude/hooks.json` for a Stop hook.

| Condition | Recommendation |
|---|---|
| Code project + no Stop hook | Recommend agent-based Stop hook for self-review |
| Non-code project | Not applicable (PASS) |
| Stop hook present | PASS |

Effort: Medium (create hook configuration + review agent)
Reference: Topics/16-hook-system.md, Generation Standards item 12c

### H2: PreCompact Auto-Save Hook

Check for a PreCompact hook that saves session state before context compaction.

Check settings.json hooks for a PreCompact event, or check GETTING_STARTED.md for documentation of manual PreCompact handling.

| Condition | Recommendation |
|---|---|
| No PreCompact hook and no documentation | Add PreCompact auto-save hook or document manual process |
| Documented but not automated | PASS (with note) |
| Hook configured | PASS |

Effort: Quick Win (add hook to settings.json) or Medium (create auto-save script)
Reference: Topics/16-hook-system.md, Generation Standards item 12b

### H3: Binary File Protection

Check if the environment handles binary or large files that should not be read:
- .claudeignore patterns for binary extensions (.exe, .dll, .pdb, .uasset, etc.)
- Settings deny rules for binary file operations

| Condition | Recommendation |
|---|---|
| Project has binaries + no protection | Add binary extensions to .claudeignore |
| No binaries in project | PASS |
| Protection present | PASS |

Effort: Quick Win (add patterns to .claudeignore)
Reference: Topics/11-permissions.md

### H4: Self-Learning Execution Trigger

If a self-learning rule exists (retro logging), check that there is a trigger
mechanism that acts on accumulated observations:
- SessionStart hook or /state-load check that counts retro entries
- Recommendation to run /update after N entries accumulate
- Any automated pattern that processes retro logs

| Condition | Recommendation |
|---|---|
| Self-learning rule exists but no trigger | Add execution trigger (hook or state-load check) |
| No self-learning rule | Not applicable (suggest adding if project is ongoing) |
| Trigger present | PASS |

Effort: Medium (add hook or modify state-load)
Reference: Topics/07-self-learning.md, Generation Standards item 16

### H5: Compliance Enforcement Hooks

If the environment handles sensitive/regulated data (check GENESIS.md, sensitive-data
rule, or CLAUDE.md for mentions of PII, HIPAA, SOX, GDPR, financial data, patient data,
legal privilege):

Check for deterministic enforcement hooks:
- PreToolUse hook scanning Write/Edit content for PII patterns
- pii-patterns.conf with domain-appropriate regex patterns
- UserPromptSubmit hook for input screening (optional but recommended)
- PostToolUse audit trail hook for compliance logging

| Condition | Recommendation |
|---|---|
| Sensitive data handled + advisory rule only (no hooks) | Add PreToolUse PII gate hook + pattern config |
| Hooks present but patterns are generic (not domain-specific) | Customize patterns for the specific domain |
| Hooks present but only audit (PostToolUse), no blocking (PreToolUse) | Add PreToolUse blocking hook |
| No sensitive data in project | Not applicable (PASS) |
| Full enforcement stack present | PASS |

Effort: Medium (create hook scripts + pattern config + settings.json entries)
Reference: Topics/16-hook-system.md (Section 16.9), Generation Standards item 25

---

## Part 5 -- Advanced Pattern Audit (5 checks)

### P1: Routing Table Completeness and Domain-Specificity

Read the orchestrator rule. Extract routing table entries.

Check completeness:
- At least 10 entries covering 8+ distinct intent categories
- Every entry has a primary route and fallback
- Entries cover: simple tasks, complex tasks, investigation, creation, review, error handling, state management, meta/help

Check domain-specificity:
- At least 3 entries use domain-specific vocabulary (not generic "code question")
- Compare against GENESIS.md or CLAUDE.md for domain terms

| Condition | Recommendation |
|---|---|
| < 10 entries or < 8 categories | Add missing routing entries |
| Entries are generic | Replace with domain-specific language |
| Missing fallbacks | Add fallback chains |
| Complete and domain-specific | PASS |

Effort: Medium (rewrite routing table)
Reference: Topics/08-routing.md, Generation Standards Routing Table Rules

### P2: Execution Mode Coverage

Check the orchestrator rule for a decision matrix covering:
1. Sequential subagents (serial pipeline)
2. Parallel subagents (independent Task tool calls)
3. Agent Teams (experimental, multi-stream)

| Condition | Recommendation |
|---|---|
| Only sequential mentioned | Add parallel and teams options with decision criteria |
| No execution mode guidance | Add full decision matrix |
| All three covered | PASS |

Effort: Quick Win (add decision matrix section to orchestrator rule)
Reference: Topics/04-teams.md, Generation Standards Execution Mode

### P3: Codebase Mapping for Large Projects

Estimate project size: glob for source files (*.cpp, *.h, *.cs, *.py, *.ts, *.js, etc.) in the target directory. If GENESIS.md mentions codebase size, use that.

| Condition | Recommendation |
|---|---|
| 50+ source files and no /map-codebase skill | Recommend adding codebase mapping |
| < 50 source files | Not applicable |
| /map-codebase present | PASS |

Effort: Large (create skill + wiki scaffold)
Reference: Topics/05-memory.md, Generation Standards Optional Skills

### P4: Multi-Role Support

If GENESIS.md indicates a team with different roles (dev, design, QA, etc.) or if the environment serves multiple people with different needs:

| Condition | Recommendation |
|---|---|
| Team with diverse roles + no Docs/Roles/ | Add role templates (CLAUDE.local.md per role) |
| Solo or uniform team | Not applicable |
| Docs/Roles/ present | PASS |

Effort: Large (create role templates, add routing entries)
Reference: Topics/05-memory.md (Section 5.8), Generation Standards item 23

### P5: Document Integration

If GENESIS.md or the user interview mentions working with external documents (PDFs, design specs, API references):

| Condition | Recommendation |
|---|---|
| External docs mentioned + no parsing setup | Add document processing recommendations to GETTING_STARTED.md |
| No external docs | Not applicable |
| Parsing documented | PASS |

Effort: Quick Win (add section to GETTING_STARTED.md) or Medium (add processing skill)
Reference: Topics/21-rag-strategies.md (RAG + document integration), Generation Standards item 19

### P6: Environment Shape

Read the `Shape` field from UPGRADE_CONTEXT.md. Cross-reference with interview answers for signals about multiple projects being worked on from this setup.

| Condition | Recommendation |
|---|---|
| Shape: SINGLE + user mentions multiple distinct projects or "I wish Claude would forget about X while I'm on Y" | Convert to multi-area hub. Move existing `.claude/`, CLAUDE.md, Docs/ under `<area-slug>/`; generate parent shell. Reversible. |
| Shape: HUB + exactly one remaining area | Collapse hub to single area. Move `<only-area>/*` up; delete HUB_GENESIS.md, HUB_ARCHITECTURE.md, parent `.claude/`. Reversible. |
| Shape: HUB_LIKE_UNDECLARED (sibling environments, no HUB_GENESIS.md) | Declare hub structure. Generate HUB_GENESIS.md and parent shell based on deduplication analysis. |
| Shape: HUB + cumulative CLAUDE.md budget exceeded | Tighten parent CLAUDE.md or move shared content into a loaded-on-demand rule |
| Shape: HUB + areas rarely touched together | Consider splitting into independent single environments in different directories |
| Shape matches user's workflow cleanly | PASS |

Effort: Large for conversion (Convert to hub / Declare hub); Medium for collapse; Quick Win for budget tightening.
Reference: architecture-guide.md Hub Architecture section; CLAUDE.md /upgrade-environment pipeline shape-conversion branch.

---

## Part 6 -- User Pain Point Mapping

During the user interview, the orchestrator collects pain points. Map each
pain point to the relevant checks for prioritization.

| User Pain Point | Primary Checks | Secondary Checks |
|---|---|---|
| "Context runs out too fast" | F7 (autocompact), M4 (growth bounds) | F1 (CLAUDE.md size), M2 (wiki size), A6 (skill size) |
| "Wrong assistant handles my request" | P1 (routing), A5 (skill descriptions) | A4 (anti-oversubagenting) |
| "Keeps asking for permission" | F5 (deny rules, may need more allow rules) | Check settings.json allow patterns |
| "Doesn't remember across sessions" | M6 (state-save/load), M1 (wiki staleness) | H2 (PreCompact), M4 (state pruning) |
| "Environment feels bloated" | F1 (CLAUDE.md size), M2 (wiki size), M5 (tier) | A6 (skill size), F4 (overemphasis) |
| "Doesn't catch its own mistakes" | H1 (Stop hook self-review) | Self-learning checks (H4) |
| "Wiki is always outdated" | M1 (staleness tracking) | P3 (codebase mapping) |
| "Takes too long on simple tasks" | A4 (anti-oversubagenting), P1 (routing) | A1 (model selection -- Opus for simple tasks is slow) |
| "Makes the same mistake repeatedly" | H4 (self-learning trigger) | M6 (state persistence) |
| "Files get corrupted or overwritten" | H3 (binary protection), F5 (deny rules) | H1 (Stop hook review) |
| "Worried about sensitive data leaking" | H5 (compliance hooks), sensitive-data rule | F5 (deny rules), PostToolUse audit |
| "Need to prove compliance / audit trail" | H5 (compliance hooks), PostToolUse audit | M6 (state persistence for audit) |

When a pain point matches multiple checks, prioritize the primary checks in
the recommendation report. Elevate matched recommendations by one tier if they
address a stated user pain point (e.g., a Medium change that addresses a pain
point should be highlighted as high-priority Medium).

---

## Recommendation Prioritization

After running all checks, prioritize recommendations:

1. **Critical gaps**: Checks that FAIL AND address a user pain point
2. **High-priority**: Checks that FAIL OR address a user pain point
3. **Standard**: Checks that reveal gaps but no user pain point
4. **Low-priority**: Minor improvements with small impact

Within each priority level, order by effort (Quick Wins first).

For each recommendation, include:
- A unique ID ([Q1], [M1], [L1] etc.)
- Gap description (what is wrong)
- Best practice reference (topic file)
- Effort tier and estimated scope
- Specific files affected
- Detailed description of what to change

---

## Conflict Detection

Some recommendations may conflict. Flag these explicitly:

- Adding more rules (completeness) vs keeping files small (F1, M2)
- Adding more agents (capability) vs anti-oversubagenting (A4)
- Enterprise memory tier (completeness) vs Lite tier (simplicity, M5)
- Automated hooks (H1-H4) vs keeping settings.json simple

Present conflicts as choices for the user, not as both-recommended.

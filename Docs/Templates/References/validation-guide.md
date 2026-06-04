# Validation Guide

**VERSION: 2 (2026-05-31)** -- single source of truth for the environment
validation checklist. `.codex/rules/03-quality-gates.md` (the always-loaded
rule) and `Docs/AgentPlaybooks/EnvironmentValidation.md` (functional/smoke/edge
tests) both reference this file by name and do not re-list checks. When you add,
remove, or renumber a check, do it here and bump the version below.

Changelog:
- v2 (2026-05-31): designated single source of truth. Added the precise check-
  count statement; added checks 6b (required core rules present), 16b (manifest-
  vs-files boundary crossing), 20b (GENESIS vocabulary in AGENTS.md). Added tier
  labels (Blocking / Critical / Advisory / Conditional).
- v1: original 55-check guide.

Reference document for the environment-validator agent, loaded in Step 2 of its
procedure. Contains the complete validation checklist, report format, and
grading criteria.

---

## Check scope and count

The checklist is **22 core checks** (numbered 1-22, always run; plus the always-
run sub-checks 6b, 16b, 20b and the conditional sub-check 21b) + **27 conditional
checks** (23-49, run only when the trigger condition is met) + **6 hub checks**
(50-55, run only for multi-area hubs). Earlier docs that said "22-point
checklist" referred to the core set; "50" counted core+conditional; both describe
this same guide at different scopes. Cite the scope, not a bare number.

Tier legend (severity when a check is violated):
- **Blocking** -- structural breakage; the environment will not work. FAIL gates release.
- **Critical** -- logic/consistency defect; the environment works but misbehaves.
- **Advisory** -- quality/UX improvement; WARN, does not gate release.
- **Conditional** -- only applies when its GENESIS/ARCHITECTURE trigger is present.

## Complete Validation Checklist

Run every check. Record PASS, WARN, or FAIL for each with details for non-PASS.

### Structural Checks (1-6b) -- BLOCKING

**1. AGENTS.md file references exist**: Read AGENTS.md, extract every file path
reference (rules, agents, skills, docs). Verify each exists on disk.
FAIL if any referenced file is missing.

**2. Agent TOML validity**: Every `.codex/agents/*.toml` must parse as TOML and
include `name` (matches filename stem), `description`, `developer_instructions`,
`model`, `model_reasoning_effort`, and `sandbox_mode`. FAIL if required fields
are missing or TOML is invalid.

**2b. Agent sandbox scope**: Analysis-only agents must use
`sandbox_mode = "read-only"`. Agents that write files must use
`sandbox_mode = "workspace-write"` and rely on `.codex/config.toml` permissions
for sensitive path restrictions. FAIL if an agent claims to be read-only while
using a write-capable sandbox.

**3. Skill frontmatter validity**: Every `.agents/skills/*/SKILL.md` must have
`name` and `description`. Check description quality: states WHAT + WHEN, includes
3+ trigger phrases, and includes negative triggers if name is ambiguous. FAIL if
description is too vague or missing required trigger guidance.

**4. No README.md in skill folders**: Glob for `.agents/skills/*/README.md`.
Any match is FAIL.

**5. .codex/config.toml validity**: Must be valid TOML with an explicit model,
`model_reasoning_effort`, sandbox/approval policy, and at least one deny rule.
FAIL if invalid TOML or no deny rules.

**6. .codex/config.toml permission coverage**: Cross-reference agent sandbox modes,
skills, hooks, and expected MCP/server operations against .codex/config.toml
permissions. Deny rules must cover destructive commands and sensitive file reads.
WARN if required operations are not represented in the permission policy.

**6b. Required core rules present**: The generated environment must contain a
routing/orchestrator rule plus an autonomy rule, a context-management rule, an
error-handling rule, and a self-learning rule (the required core components from
`02-generation-standards.md`). Match by purpose, not filename. FAIL if the
routing/orchestrator rule is missing; WARN per missing autonomy/context/error/
self-learning rule. (Closes the gap where standards required these but no check
verified their presence.)

### Routing and Logic Checks (7-13) -- CRITICAL

**7. Routing table completeness**: Orchestrator rule must have 10+ routing entries
covering 8+ distinct intent categories. Each entry needs a primary route and
fallback. At least 3 entries must be domain-specific. FAIL if below minimums.

**8. Domain-specific routing**: Routing entries must use domain vocabulary from
GENESIS.md, not generic placeholders. Bad: "complex task -> planner". Good:
"database migration -> planner (schema + model updates)". WARN if majority generic.

**9. Wiki index.md**: `Docs/index.md` must exist with Status field
(NEW_ENVIRONMENT or ACTIVE), table of contents, valid references. Structure
must match tier from ARCHITECTURE.md. FAIL if missing or no status field.

**10. State-save taxonomy coverage**: State-save SKILL.md must cover all 6
categories: tool state, task state, artifact state, decision state, blocked
state, drift risk. WARN if any missing.

**11. State-save/state-load symmetry**: Everything state-save writes, state-load
must read. File paths must match (SESSION_SNAPSHOT.json, SESSION_CONTEXT.md).
State-load must include drift detection. WARN if gaps exist.

**12. No contradictory rules**: Scan all rule files for contradictions (autonomy
vs asking, conflicting routing, conflicting thresholds). WARN if potential
contradiction found.

**13. No orphan components**: Every agent must be referenced in routing table or
AGENTS.md. Every skill referenced in AGENTS.md or a rule. Every rule referenced
in AGENTS.md. WARN if 1 unreferenced, FAIL if 2+.

### Size and Quality Checks (14-17) -- BLOCKING (size limits) / CRITICAL (quality)

**14. File size limits**: AGENTS.md < 250 lines (FAIL). Rule files < 120 lines
(WARN). Agent files < 80 lines (WARN). SKILL.md < 500 lines / 5,000 words (FAIL
on words, WARN on lines).

**15. Cross-reference resolution**: Every internal file path reference in any
generated file must resolve to an existing file. FAIL if broken references.

**16. No duplicate content**: Flag if the same instruction block (5+ similar
lines) appears in multiple files. WARN if significant duplication found.

**16b. Manifest-vs-files boundary crossing**: Cross-validate the ARCHITECTURE.md
Component Manifest against what was actually written. Every component the
manifest lists (each rule, agent, skill, hook) must exist on disk, and every
`.codex/` component on disk must appear in the manifest. This is a connection
check, not an existence check: it catches a generator that wrote a file the
architecture never planned, or planned a file it never wrote. FAIL on any
mismatch. (For hubs, scope per area + parent shell.)

**17. No role-setting prompts**: Search all generated files for "Act as a...",
"You are a [role] who...", "Pretend to be...", "Your role is...". FAIL if found.
Acceptable: "You help users with [task]", "This environment manages [domain]".

### Completeness Checks (18-22b) -- ADVISORY (except 18, 20b = CRITICAL)

**18. GETTING_STARTED.md complete**: Must exist with: what the environment does,
how to start, available commands, suggested first tasks (2+). FAIL if missing.

**19. VCS ignore guidance present**: `.gitignore`, `.p4ignore`, or generated
GETTING_STARTED.md guidance must exclude `Docs/_working/` and project-specific
large/generated artifacts. WARN if missing or minimal.

**20. Intent-behind-rules in AGENTS.md**: Sample 5+ constraints. 80%+ must
include WHY (because..., parenthetical explanation). WARN if 50-79%. FAIL < 50%.

**20b. GENESIS vocabulary in AGENTS.md (no jargon drift)**: The domain
vocabulary the user gave in GENESIS.md (key nouns, tools, workflow terms) must
actually appear in the generated AGENTS.md and routing table. A generated
environment whose AGENTS.md reads generically -- as if it could belong to any
project -- failed to absorb the intake. Sample the 5-8 most distinctive GENESIS
terms; CRITICAL if fewer than half appear anywhere in AGENTS.md or the routing
rule.

**21. Orchestrator context discipline**: Orchestrator rule must include a
whitelist of files the orchestrator may Read directly, delegation mandate for
source files, and disk-based subagent handoff pattern. FAIL if missing.

**21b. Plugin recommendations match architecture**: If ARCHITECTURE.md lists
plugins in Recommended Plugins section, GETTING_STARTED.md must have an
"Optional Plugins" section with marketplace add command and install commands.
Must NOT auto-install. WARN if section missing when plugins recommended.

**22. Skill triggering tests**: For each skill, construct and evaluate:
- 3 obvious triggers (should match description)
- 2 paraphrased triggers (different words, same intent)
- 2 non-triggers (should NOT match)
WARN if description too broad (non-triggers fire) or too narrow (paraphrases miss).

---

## Conditional Checks (23-38)

Run these only when the relevant condition is met per GENESIS.md/ARCHITECTURE.md:

**23. PreCompact hook**: .codex/config.toml must configure PreCompact auto-save hook
(or document in GETTING_STARTED.md).

**24. local config profile**: Must be generated when ARCHITECTURE.md specifies
machine-specific paths.

**25. Docs/_working/ VCS exclusion**: Must be in .gitignore, .p4ignore, or
documented.

**26. Self-learning execution trigger**: The self-learning rule is a required core
component, so this effectively always applies. .codex/config.toml must configure a
self-learning trigger hook (InstructionsLoaded preferred, or SessionStart) that
counts `Docs/_working/retro/` entries and recommends `/update` at threshold. FAIL
if a self-learning rule exists with no such trigger (logging-only loops never run).

**27. State file pruning**: /state-save must include pruning logic when state
management is included.

**28. Wiki staleness watermark**: Initialized when /map-codebase is included.

**29. Stop hook self-review**: Configured when GENESIS.md indicates code-producing
project.

**30. Document parsing tool**: Documented in GETTING_STARTED.md when GENESIS.md
indicates external docs.

**31. Multi-role templates**: Generated in Docs/Roles/ when GENESIS.md indicates
team with diverse roles.

**32. Beads setup**: In GETTING_STARTED.md when GENESIS.md indicates complex
multi-session project with interdependent subtasks and intermediate+ user.

**33. Compliance enforcement hooks**: PreToolUse PII gate + pii-patterns.conf
when GENESIS.md indicates sensitive data AND deterministic enforcement.

**34. PII pattern config**: Contains domain-appropriate patterns (not just
generic defaults) when compliance hooks generated.

**35. Token optimization guidance**: Present in GETTING_STARTED.md when GENESIS.md
indicates cost-conscious or balanced efficiency priority.

**36. Optional plugins section**: Present in GETTING_STARTED.md when
ARCHITECTURE.md lists matching official plugins.

**37. Skill eval recommendation**: Present in GETTING_STARTED.md when 3+ custom
skills and intermediate+ user.

**38. Memory plugin recommendation**: Present in GETTING_STARTED.md as optional
when ARCHITECTURE.md lists a memory plugin.

**39. Status line documented**: When GENESIS.md indicates complex project or large
codebase, GETTING_STARTED.md must include status line setup instructions showing
context health. WARN if missing.

**40. InstructionsLoaded hook configured**: When self-learning rule is included,
.codex/config.toml must configure an InstructionsLoaded hook (preferred over SessionStart)
that checks retro/ entry count and recommends /update after 5+ entries. WARN if
using SessionStart instead of InstructionsLoaded. FAIL if no trigger mechanism exists.

**41. MCP Tool Search threshold documented**: When ARCHITECTURE.md includes 3+
MCP servers, GETTING_STARTED.md must document the ENABLE_TOOL_SEARCH setting with
recommended threshold. WARN if missing.

**42. Service tier guidance documented in GETTING_STARTED.md**: When GENESIS.md indicates
cost-conscious or balanced efficiency priority, GETTING_STARTED.md must document
available Codex service-tier trade-offs without auto-enabling premium or latency-focused
tiers in shared config. WARN if missing.

**43. MCP server packages verified**: Every MCP server in generated .mcp.json or
.codex/config.toml must correspond to a verified server from tool-registry.md "Verified
MCP Servers" section. FAIL if any MCP server references an unverified or non-existent
package. Cross-check each server's command/args against the registry entry.

**44. Hook matcher format**: All hook matchers in .codex/config.toml must be strings
(e.g., "Edit", "Write|Edit", "Bash"), not objects. Events without tool-specific
matching (PreCompact, InstructionsLoaded, SessionStart, Stop, SessionEnd) must
omit the matcher field entirely. FAIL if any matcher is an object or if a
non-tool event has a matcher.

**45. Diagnostic discipline section**: When GENESIS.md indicates the user will
be debugging, troubleshooting, or diagnosing issues (software dev, game dev,
DevOps, IT ops, data engineering), the error-handling rule must include a
diagnostic discipline section with: multi-hypothesis start, pivot trigger after
2 failed attempts, and explicit assumption stating. WARN if missing for
applicable domains.

**46. Environment complexity decisions respected**: Every external dependency in
the generated environment (MCP servers, plugins, third-party tool installs) must
correspond to an "Include" entry in ARCHITECTURE.md's Environment Complexity
decision table. FAIL if any generated external dependency was not in the table
or was marked "Skip". WARN if the decision table is missing entirely when
external dependencies are present.

**47. GPT-5.5 API compatibility**: When GENESIS.md targets GPT-5.5 (or does not
specify a pinned older model), generated .codex/config.toml, skill bodies, agent
bodies, and embedded code snippets must NOT set `temperature`, `top_p`, `top_k`,
or `thinking.budget_tokens`. These parameters return 400 on GPT-5.5. FAIL if
any such parameter appears in generated API-call content.

**48. Effort level guidance**: When the generated environment targets GPT-5.5,
GETTING_STARTED.md must mention `effort` tuning. Must include at least one of:
`model_reasoning_effort = "xhigh"` recommendation for complex coding/agentic
work, or `model_reasoning_effort` on Codex subagent TOML files. WARN if absent.

**49. Output budget headroom**: When the generated environment targets GPT-5.5,
any embedded output limits in example API snippets should be large enough for
the task class and should not copy tiny placeholder values into agentic loops.
WARN if low output limits appear in example agentic-loop snippets without an
explanation.

### Hub Mode Checks (50-55)

Run these only when the target contains `Docs/Environment/HUB_GENESIS.md`.

**50. Hub registry matches disk**: Read the work-area registry from
HUB_GENESIS.md. Every listed area-slug must have a corresponding
`<target>/<area-slug>/Docs/Environment/GENESIS.md`,
`<target>/<area-slug>/AGENTS.md`, and `<target>/<area-slug>/.codex/`.
FAIL if any registry entry has no matching subfolder, or if a subfolder
exists with `.codex/` but is not listed in the registry.

**51. Cumulative AGENTS.md budget**: Measure parent AGENTS.md line count plus
each per-area AGENTS.md line count. The largest (parent + any one child) must
be under 250 lines. Parent AGENTS.md alone should be under 80 lines.
FAIL if cumulative > 250 for any area. WARN if parent > 80.

**52. Override declarations for name collisions**: For every component name
that appears both at the parent and in any area (same rule filename, same agent
name, same skill folder), the per-area version must declare
`overrides: <parent-component-name>` in frontmatter. FAIL if a collision exists
without the override declaration. This catches unintentional shadowing.

**53. Cross-area routing discipline**: Per-area routing tables must not contain
direct file paths to sibling areas (e.g., `../other-area/.agents/skills/foo/`).
Cross-area references must go through the parent routing table, which directs
the user to switch focus. FAIL if any area references another area's internal
file structure.

**54. Parent permission subset**: Parent .codex/config.toml permission profile must
not grant broader filesystem or network scope than the union of areas needs. No
parent-only access that no area uses -- that access belongs in the specific area
that needs it. WARN if parent grants unused scope; delete or move it.

**55. HUB_ARCHITECTURE matches HUB_GENESIS**: The shared-component manifest in
HUB_ARCHITECTURE.md must match what is actually generated at the parent. Every
shared rule/skill/agent listed must exist at `<target>/.codex/`, and every
`<target>/.codex/` component (except the work-area registry artifacts) must
appear in the manifest. FAIL on mismatches.

---

## Verdict Logic

- **PASS**: All checks are PASS (no WARN, no FAIL)
- **WARN**: At least one WARN but no FAIL
- **FAIL**: At least one FAIL

---

## Report Format

Write to `<target>/Docs/Environment/VALIDATION_REPORT.md`:

```markdown
# Environment Validation Report

Generated: YYYY-MM-DD
Target: <target_path>
Verdict: PASS | WARN | FAIL

## Summary
[2-3 sentence overview]

## Results

### Check 1: AGENTS.md File References
Status: PASS | WARN | FAIL
[Details if non-PASS]

[... all checks ...]

## Skill Triggering Tests

### Skill: <name>
Obvious triggers: [3 phrases] -- [assessment]
Paraphrased triggers: [2 phrases] -- [assessment]
Non-triggers: [2 phrases] -- [assessment]
Assessment: PASS | WARN

[... all skills ...]

## Critical Issues (if FAIL)
[Numbered list]

## Warnings (if WARN)
[Numbered list]

## Recommendations
[Optional suggestions]
```

---

## Output to Orchestrator

Return:
- Overall verdict: PASS, WARN, or FAIL
- Count of checks by status (e.g., "18 PASS, 3 WARN, 1 FAIL")
- List of any FAIL issues (one line each)
- List of any WARN issues (one line each)
- Path to the full validation report

---

## Fix Workflow

The validator is read-only and does not fix issues. When critical failures exist:

1. Orchestrator reads the validation report
2. For each FAIL, orchestrator delegates a targeted fix to component-generator
3. After all fixes, orchestrator re-invokes the validator
4. Maximum 2 fix-and-revalidate cycles

The orchestrator must NOT fix issues directly -- delegate to component-generator
with the specific failure context from the report.

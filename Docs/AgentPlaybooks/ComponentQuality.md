# Component Quality Standards

Quality criteria per component type. Loaded by the component-generator
during each generation pass and by the environment-validator for quality checks.

Every generated component must meet the standards below. The component-generator
should self-check against these criteria before writing each file. The validator
checks them after generation.

---

## CLAUDE.md Quality Criteria

### Size Limit
- Target: 150-200 lines
- Hard maximum: 250 lines

### Required Sections (in order)

1. Purpose and constraints (NOT role-setting)
2. First-run onboarding (detect NEW_ENVIRONMENT marker)
3. Non-negotiable constraints
4. Autonomy rules (reference to rule file)
5. Quick command reference
6. Orchestrator contract (lean context, delegate, artifact-first)
7. Canonical behavior examples (2-3 few-shot examples)
8. Compaction hints (domain-specific preservation list)
9. Verification patterns (domain-specific commands)
10. Self-improvement note

### Include/Exclude Rubric

**INCLUDE in CLAUDE.md** (things Claude cannot guess or infer):
- Commands the user wants available and their exact trigger words
- Style rules that differ from Claude's defaults (e.g., "never use emoji",
  "always write in passive voice for this legal project")
- Testing instructions specific to this project
- Architectural decisions that affect how Claude should work
- Dev environment quirks (non-standard paths, custom tools, platform constraints)
- Common gotchas that have caused problems before
- Hard safety constraints (what to never do)
- Domain vocabulary that has specific meaning in this project
- The intent (WHY) behind every constraint

**EXCLUDE from CLAUDE.md** (wastes tokens, adds noise):
- Anything Claude can infer from reading the code or files
- Standard conventions for the language/framework (Claude already knows these)
- Detailed API documentation (link to it instead)
- Frequently-changing information (put in memory files instead)
- Redundant restatements of the same rule
- General coding best practices (Claude already follows these)
- Lengthy examples that belong in reference files
- Information that belongs in a rule or agent file (CLAUDE.md references them)

### Intent-Behind-Rules Enforcement

Every constraint in CLAUDE.md must explain WHY, not just WHAT.

Bad:
```
- Never modify files in the /config directory.
```

Good:
```
- Never modify files in the /config directory -- these are shared
  configuration managed by the platform team, and local changes will be
  overwritten on next deploy.
```

Check: For each constraint, ask "would Claude understand why this matters?"
If the answer is "only if Claude already knows our project," the intent
is missing.

### Few-Shot Example Requirements

Include 2-3 canonical behavior examples that show how the assistant should
handle common situations in this specific domain. These are more effective
than rule lists for establishing behavioral norms.

Each example must:
- Be realistic for the project domain
- Show a user request and the expected assistant behavior
- Demonstrate a specific pattern (e.g., investigate-before-answering,
  delegation, asking vs. acting)
- Be concise (5-10 lines per example, not full conversations)

Format:
```
## Canonical Behavior Examples

### Example: [Situation Name]
User: "[realistic user request]"
Expected: [What the assistant should do, in 2-4 bullet points.
Include which agent to delegate to, what to check first, etc.]
```

### Anti-Patterns to Avoid

- Role-setting prompts ("Act as a senior engineer who...")
- Repeating the same instruction in different words
- Vague constraints without actionable guidance ("be careful with databases")
- Over-specifying obvious behavior ("read files before editing them")
- Giant routing tables (put in orchestrator rule instead)
- Detailed agent/skill descriptions (they have their own files)

---

## Rule File Quality Criteria

### Size Limit
- Target: 60-100 lines
- Hard maximum: 120 lines

### Structure Requirements

- Clear title (# heading)
- Brief purpose statement (1-2 sentences)
- Organized with ## subheadings
- Actionable items, not philosophy
- Tables for structured data (routing tables, permission lists)

### Content Standards

- Each rule must be specific enough to act on
- Each rule must include WHY (same intent-behind-rules requirement as CLAUDE.md)
- Avoid overlap with other rule files (check for duplication)
- Link to other rules rather than restating their content
- Use domain-specific vocabulary from GENESIS.md

### Per-Rule-Type Standards

**Orchestrator rule (00-orchestrator.md)**:
- Must contain a routing table with domain-specific entries
- Every routing entry must have: intent | complexity | route | fallback
- Must define delegation requirements (objective, output format, tool guidance, boundaries)
- Must reference complexity scaling (simple/standard/complex)
- Must specify proactive vs. conservative default action

**Autonomy rule (01-autonomy.md)**:
- Must classify actions by reversibility and impact
- Must include the overengineering prevention instruction (Opus 4.6)
- Must list specific examples for "act" vs. "ask" in this domain
- Must not contradict the orchestrator's routing decisions

**Context management rule (02-context-management.md)**:
- Must specify trigger thresholds (turn count, delegation count, file reads)
- Must describe the two-stage approach (proactive summarize + auto-save)
- Must include domain-specific compaction preservation hints
- Must reference /state-save skill for the auto-save action

**Self-learning rule (03-self-learning.md)**:
- Must list friction categories with examples
- Must include cold-start seed entries from the starter profile
- Must specify bootstrapping thresholds (lower in first 30 days)
- Must reference /update skill for acting on patterns
- Must include correction detection heuristics

**Error handling rule (04-error-handling.md)**:
- Must cover: agent failure, missing file, tool unavailable, state corruption,
  VCS not configured, permission denied
- Each error type must have a specific recovery action
- Must not instruct retrying more than once

**Memory management rule (05-memory-management.md)**:
- Must state INDEX.md is the only file loaded by default
- Must describe just-in-time retrieval pattern
- Must include staleness criteria (Last Updated / Last Verified)
- Must reference the tier chosen in ARCHITECTURE.md

---

## Agent Definition Quality Criteria

### Size Limit
- Target: 40-60 lines
- Hard maximum: 80 lines

### Frontmatter Requirements

All fields are enforced:
```yaml
---
name: agent-name          # Required. Matches filename stem.
description: ...          # Required. Includes WHEN to delegate.
model: sonnet             # Required. opus | sonnet | haiku
tools: [Read, Write, ...]# Required. List of tools.
maxTurns: 30              # Required. Integer 10-100.
---
```

Optional but recommended:
```yaml
disallowedTools: []       # Tools this agent must not use
permissionMode: default   # default | bypassPermissions
```

### Description Standards

The description field determines WHEN the orchestrator delegates to this agent.
It must:
- State WHEN to delegate (not just WHAT the agent does)
- Use domain vocabulary ("when a database query fails" not "when there is an error")
- Be specific enough that the orchestrator can make a routing decision

Bad: "Helps with code implementation."
Good: "Implement code changes for planned features and bugfixes. Delegate when
a task has a clear plan and specific files to modify."

### Instruction Body Standards

After the frontmatter, the agent instructions must include:

1. **Objective**: What this agent accomplishes (1-2 sentences)
2. **Output format**: What the agent writes to disk and returns
3. **Tool guidance**: Which tools to use and how (especially important for
   agents with constrained tool access)
4. **Task boundaries**: What is in scope and out of scope
5. **Investigate-before-answering**: "Never speculate about files you have
   not read. Read the relevant files first, then answer."
6. **Artifact requirement**: "Write your output to [specific path].
   Return a brief summary to the orchestrator."

### Model Selection Justification

Each agent's model should match its work type:
- Opus: Complex reasoning, architectural decisions, multi-step planning
- Sonnet: Following clear procedures, code implementation, structured review
- Haiku: Quick lookups, file exploration, simple queries

If an agent's model does not match these guidelines, the validator flags a WARN
(not FAIL -- the architect may have domain-specific reasons).

---

## Skill (SKILL.md) Quality Criteria

### Size Limits
- Target: 100-300 lines
- Soft maximum: 500 lines
- Hard maximum: 5,000 words

### Frontmatter Requirements

```yaml
---
name: skill-name
description: [What]. [When/triggers 3+]. [Negative triggers if ambiguous].
context: fork
allowed-tools: [Read, Write, Bash]
metadata:
  author: Claude Harness Generator
  version: 1.0.0
  generated: YYYY-MM-DD
---
```

### Skill Description Checklist

The description field is critical for skill triggering. Check each item:

- [ ] States WHAT the skill does (first sentence)
- [ ] Contains 3+ trigger phrases users might say
- [ ] Trigger phrases include the slash command name (e.g., "/state-save")
- [ ] Trigger phrases include natural language variants
- [ ] Written in third person ("Saves the current state..." not "Save the current state...")
- [ ] Under 1024 characters total
- [ ] Over 80 characters total
- [ ] Contains negative triggers if the skill name is ambiguous
      (e.g., "Do NOT use for saving individual files" for state-save)
- [ ] Does not overlap significantly with other skill descriptions

### Content Structure

Critical instructions at the TOP of SKILL.md (not buried after background).

Recommended order:
1. `## Critical` or `## Important` (if any critical instructions exist)
2. `## Overview` (what this skill does, 2-3 sentences)
3. `## Steps` (numbered procedure)
4. `## Output` (what files are created/modified)
5. `## Error Handling` (what to do when things go wrong)
6. References to scripts/ and references/ subdirectories as needed

### Composability Requirement

Each skill must check its own preconditions and not assume another skill
ran first. For example:
- /state-load must handle the case where /state-save was never run
- /health-check must handle a brand-new environment with no history
- /update must handle an environment with no retro entries

Check: Does the skill handle the "empty state" case? If not, add handling.

### Progressive Disclosure

For skills with substantial reference material:
- Core instructions in SKILL.md (under 500 lines)
- Deterministic scripts in scripts/ (validation, capture, formatting)
- Detailed reference docs in references/ (loaded on demand, one level deep)

The skill should reference these subdirectories explicitly:
"For detailed troubleshooting, see references/troubleshooting.md"

### Script Requirements (scripts/ subdirectory)

If the skill includes scripts:
- Scripts must be deterministic (no LLM interpretation needed)
- Scripts must produce structured output (JSON preferred)
- Scripts must handle errors gracefully (exit codes, error messages)
- Scripts must work cross-platform (or document platform requirements)
- Script filenames must describe their function (capture-vcs-state.sh, validate.py)

---

## Memory Scaffold Quality Criteria

### INDEX.md Requirements

- Must be the ONLY memory file loaded by default
- Must contain `Status: NEW_ENVIRONMENT` marker for first-run detection
- Must contain a table of contents linking to all other memory files
- Must include Last Updated timestamp
- Each entry must have a 1-line description
- Must match the tier from ARCHITECTURE.md:
  - Lite: INDEX.md + PROJECT.md (2 files)
  - Standard: INDEX.md + Overview.md + Areas/ + Decisions/ + Sessions/
  - Enterprise: Standard + sub-indexes in Areas/ + Teams/

### Memory File Standards

- Each file starts with 2-3 line summary
- Uses "Last Updated" and "Last Verified" timestamps
- Cross-links use relative paths
- Human-readable (doubles as project documentation)
- No binary content, no base64, no encoded data

### Anti-Overengineering Check

Compare the memory tier against the project scale from GENESIS.md:

- Solo developer, simple project: Lite tier only (INDEX + PROJECT)
- Small team, medium complexity: Standard tier
- Large team, complex domain: Enterprise tier

If the memory tier is more complex than the project justifies, flag as WARN.
"Memory tier [Enterprise] may be over-engineered for project scale [solo developer].
Consider Lite tier."

---

## State Management Quality Criteria

### SESSION_SNAPSHOT.json

- Must be valid JSON
- Must contain keys for all 6 taxonomy categories
- Must include a timestamp
- Must include environment version
- Values should be concise (paths, not file contents)

### SESSION_CONTEXT.md

- Must be human-readable narrative
- Must summarize the session state in plain language
- Must be understandable without reading the JSON
- Target: 20-50 lines

### Symmetry Check

- /state-save writes SESSION_SNAPSHOT.json and SESSION_CONTEXT.md
- /state-load reads both files
- Same category names used in both
- Same file paths referenced in both

---

## settings.json Quality Criteria

### Structure

```json
{
  "permissions": {
    "allow": [...],
    "deny": [...]
  }
}
```

### Permission Coverage

Must include at minimum:
- `Read(./**)` -- allow reading all project files
- `Write(./Docs/**)` and `Edit(./Docs/**)` -- allow memory/docs operations
- `Write(./.claude/**)` and `Edit(./.claude/**)` -- allow self-modification
- `Write(./CLAUDE.md)` and `Edit(./CLAUDE.md)` -- allow CLAUDE.md updates
- Domain-specific permissions (Bash commands for build, test, VCS)

### Deny Rule Requirements

Must include at minimum:
- At least one dangerous Bash command denial (rm -rf, sudo, etc.)
- At least one sensitive file read denial (.env, secrets, credentials)

Should include:
- Denials specific to the project's ecosystem
- Denials for destructive VCS operations (force push, hard reset)

### Ecosystem-Specific Additions

Based on GENESIS.md technical environment:

| Ecosystem | Additional Allow | Additional Deny |
|-----------|-----------------|-----------------|
| Node.js | `Bash(npm *)`, `Bash(npx *)` | `Bash(npm publish *)` |
| Python | `Bash(python *)`, `Bash(pip *)` | `Bash(pip install --user *)` (if not desired) |
| Git | `Bash(git *)` | `Bash(git push --force *)`, `Bash(git reset --hard *)` |
| Perforce | `Bash(p4 *)` | `Bash(p4 submit *)`, `Bash(p4 obliterate *)` |
| Docker | `Bash(docker *)` | `Bash(docker rm -f *)` |
| Database | `Bash(psql *)`, `Bash(mysql *)` | `Bash(* DROP DATABASE *)` |

### Sandbox Configuration

If relevant to the project, include sandbox settings:
- `CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE` tuning recommendation
- Hook configurations for quality gates (PostToolUse for lint/test)

---

## File Size Enforcement Table

Quick reference for all generated component size limits:

| Component | Target Lines | Hard Max Lines | Hard Max Words |
|-----------|-------------|----------------|----------------|
| CLAUDE.md | 150-200 | 250 | -- |
| Rule file | 60-100 | 120 | -- |
| Agent definition | 40-60 | 80 | -- |
| SKILL.md | 100-300 | 500 | 5,000 |
| Wiki index.md (Docs/index.md) | 20-50 | 100 | -- |
| GETTING_STARTED.md | 30-60 | 100 | -- |
| settings.json | -- | -- | -- (valid JSON) |

Total rule files: 5-8 (flag if outside this range).
Total agent definitions: minimum 1, typical 3-7 (flag if >10).

---

## Investigate-Before-Answering Requirement

Every generated agent must include this pattern in its instructions:

```
Never speculate about files you have not read. When asked about code,
configuration, or project structure, read the relevant files first,
then provide your answer based on what you found.
```

This prevents agents from hallucinating file contents or project structure.
The exact wording can be adapted to the domain, but the principle must be
present.

For non-code domains, adapt:
```
Never speculate about documents you have not read. When asked about
existing content, read the relevant files first, then respond based
on what you found.
```

---

## Anti-Overengineering Checks

The component-generator must apply these checks after each generation pass:

### Agent Count Check

| Project Scale | Expected Agents | Flag If |
|--------------|----------------|---------|
| Solo, simple | 1-3 | > 3 agents |
| Small team, medium | 3-5 | > 6 agents |
| Large team, complex | 5-7 | > 8 agents |

"Only generate agents that the intake answers justify. A smaller set of
well-defined agents is better than many agents with overlapping responsibilities."

### Rule Count Check

Expected: 5-8 rule files for any project.
Flag if: > 8 rules (some should probably be merged).
Flag if: < 5 rules (core rules may be missing).

### Skill Count Check

Minimum: 4 core skills (/state-save, /state-load, /update, /health-check).
Additional skills must each be justified by a specific workflow from GENESIS.md.

Flag if: > 8 total skills for a simple project.
Flag if: Skills overlap significantly in purpose.

### Complexity Match

Compare generated environment complexity against GENESIS.md project description.
Flag warnings for:
- Enterprise memory tier on a solo project
- Team coordination rule on a solo project
- Performance analysis agent on a non-performance-critical project
- Build skill when no build system exists
- Review agent when no code review workflow was described

### Content Density Check

For each file, check that content is substantive, not padded:
- No filler paragraphs that repeat the file's title
- No generic advice that applies to any project
- No placeholder sections ("TODO: fill this in")
- No excessive formatting (triple-nested bullets, deeply nested headers)

If a file is under 50% of its target size, that is acceptable and preferred
over padding it with generic content.

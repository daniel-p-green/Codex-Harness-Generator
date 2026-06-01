# Template: Update Skill (/update)

<!-- TEMPLATE ANNOTATION
  This template defines the /update skill that reviews friction logs and proposes
  environment improvements. It is split into two phases: Analysis (always runs)
  and Implementation (requires user approval per proposal).

  QUALITY CRITERIA:
  - Skill description includes 3+ trigger phrases
  - SKILL.md body under 500 lines
  - Analysis phase clearly separated from implementation
  - Evaluation-driven methodology
  - Proposal format with evidence, change, classification
  - Guardrails (max 1 structural change, self-modifiable vs human-only)
  - Backup before edit
  - EVOLUTION.md logging

  WHY THIS EXISTS:
  Generated environments have routing errors, missing permissions, wrong thresholds,
  and workflow gaps. The /update skill uses evidence from the friction log to identify
  patterns, propose targeted fixes, and apply them after user approval. This is the
  primary mechanism for environment improvement over time.

  The analysis/implementation split prevents accidental self-modification. Claude
  analyzes first, presents proposals, and only implements after explicit approval.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application

  File structure:
  .claude/skills/update/
    SKILL.md              (this file -- core instructions)
    references/
      proposal-format.md    (detailed proposal template)
============================================================ -->

## SKILL.md

```yaml
---
name: update
description: Review friction logs and propose environment improvements. Use when the user says "update environment", "improve the setup", "review friction", "check for improvements", "what can be better", or "/update". Do NOT use for updating code, dependencies, or project files.
context: fork
allowed-tools: [Read, Write, Edit, Glob, Grep]
metadata:
  author: Claude Harness Generator
  version: 1.0.0
---
```

## Critical

- Phase 1 (Analysis) always runs. Phase 2 (Implementation) requires explicit user approval per proposal.
- Maximum ONE structural change per invocation (new rule file, new agent, routing table rewrite).
- ALWAYS back up files before modifying them (copy to `Docs/_working/retro/Backups/`).
- NEVER modify: `Docs/Environment/GENESIS.md` (immutable intake record).
- Log ALL changes to `Docs/Environment/EVOLUTION.md`.

## Phase 1: Analysis

<!-- ANALYSIS PHASE
  WHY: Analysis produces proposals without changing anything. The user can
  review proposals, approve some, reject others. This prevents accidental
  self-modification from a misidentified pattern.
-->

### Step 1: Read the evidence

1. Read `Docs/_working/retro/INDEX.md` for theme overview
2. Read the most recent `Docs/_working/retro/YYYY-MM.md` monthly log
3. Read `Docs/Environment/EVOLUTION.md` for history of past changes
4. Count entries by friction category

### Step 2: Identify patterns

Use the evaluation-driven methodology:

1. **Identify gap**: Find friction categories with 2+ entries (or 1 entry matching a pre-seeded pattern)
2. **Group related entries**: Cluster entries that describe the same underlying problem
3. **Rank by frequency and impact**: More entries = higher priority. User corrections (CORRECTION) outweigh routine friction (FRICTION).

Priority ordering:
1. ROUTING_CORRECTION (routing table is wrong -- high impact, easy fix)
2. CORRECTION (user taught Claude a rule -- should be codified)
3. PATTERN (confirmed recurring friction)
4. SKILL_UNDERTRIGGER / SKILL_OVERTRIGGER (skill descriptions need tuning)
5. FRICTION (individual friction events, lower priority)

### Step 3: Draft proposals

For each identified pattern, create a proposal:

```markdown
## Proposal: [Short title]

**Evidence**: [N] entries in [category]. Examples:
- [date] [entry 1]
- [date] [entry 2]

**Root cause**: [Why this friction occurs]

**Proposed change**: [Specific file + specific edit]

**Classification**: small | medium | large
- Small: rule tweak, routing adjustment, threshold change, description update
- Medium: new rule file, new agent, new skill reference
- Large: structural change (new skill, architecture modification)

**Self-modifiable**: yes | no (requires human editing)

**Risk**: [What could go wrong if this change is applied]
```

### Step 4: Verify before proposing

<!-- PREMATURE VICTORY PREVENTION
  WHY: Proposals that "should fix it" but do not actually help are worse than
  no change at all. Verify that the proposed change addresses the evidence.
-->

Before presenting each proposal:
- Does this change directly address the friction entries cited?
- Could this change introduce new friction or contradict existing rules?
- Is there a simpler change that achieves the same result?
- Has this already been tried (check EVOLUTION.md)?

### Step 5: Present to user

Write proposals to `Docs/_working/retro/Proposals/YYYY-MM-DD_update.md`.
Present a summary in plain language:

```
Found [N] improvement opportunities:

1. [Title] (small, self-modifiable)
   [One-sentence description of change]

2. [Title] (medium, requires human editing)
   [One-sentence description of change]

Approve individual proposals by number, or "approve all" for small changes.
```

## Phase 2: Implementation

<!-- IMPLEMENTATION PHASE
  WHY: Only runs after explicit user approval. Each approved proposal is
  implemented one at a time with backups and logging.
-->

For each approved proposal:

### Small changes (implement directly)

1. Back up the target file to `Docs/_working/retro/Backups/[filename].[timestamp]`
2. Apply the change
3. Verify: read the modified file, confirm it is consistent and does not contradict other rules
4. Log the change in `Docs/Environment/EVOLUTION.md`

### Medium changes (implement with review)

1. Back up all affected files
2. Create the new file(s) or modify existing ones
3. Update cross-references (routing table, CLAUDE.md if needed)
4. Verify consistency across all modified files
5. Log in EVOLUTION.md

### Large changes (require plan approval)

1. Present a detailed implementation plan
2. Wait for second approval
3. Implement step by step with backups at each step
4. Verify after each step
5. Log in EVOLUTION.md

## Guardrails

<!-- GUARDRAILS
  WHY: Self-modification is powerful but dangerous. These guardrails prevent
  the update skill from making changes that break the environment or violate
  user trust.
-->

### Self-modifiable (after user approval)
- Rule files (`.claude/rules/*.md`)
- Routing table entries
- Context management thresholds
- Self-learning thresholds and seed patterns
- Skill descriptions (trigger phrases, negative triggers)
- Memory structure (INDEX.md, area files)
- Retro logs and proposals

### Requires human editing (present change, do not apply)
- `settings.json` permissions (allow/deny lists)
- CLAUDE.md hard constraints (non-negotiable rules)
- Agent model assignments (sonnet/opus/haiku)
- Agent maxTurns values
- Hook configurations
- `.claudeignore` patterns

### Never modified
- `Docs/Environment/GENESIS.md` (original intake record -- immutable)

## EVOLUTION.md format

```markdown
# Environment Evolution Log

## YYYY-MM-DD: [Change title]
- **Trigger**: [Friction category + entry count]
- **Change**: [What was modified]
- **Files**: [List of changed files]
- **Backup**: [Path to backup]
- **Result**: [Observed impact, if known]
```

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Proposals may include: new routing entries, permission additions, convention rules
  - Build/test integration: verify changes do not break build

  KNOWLEDGE WORK:
  - Proposals focus on: output style, citation format, research workflow
  - Simpler guardrails (fewer technical constraints)
  - Present proposals in plain language (avoid technical jargon)

  GAME DEVELOPMENT:
  - Proposals may include: playtest checklist updates, build config changes
  - Additional never-modify: binary asset handling rules
  - VCS-specific guardrails (Perforce submit rules)

  CONSERVATIVE DOMAINS:
  - Tighter guardrails: ALL changes require human approval (no "small = direct")
  - Additional never-modify: safety constraints, compliance rules, disclaimer requirements
  - Extra verification step: "Does this change affect safety-critical behavior?"
-->

<!-- ANTI-PATTERNS

  1. ANALYSIS AND IMPLEMENTATION IN ONE STEP
     Problem: Claude reads friction, immediately modifies rules without asking.
     Fix: Split into two phases. Analysis always runs. Implementation requires approval.

  2. NO BACKUP BEFORE EDIT
     Problem: Bad change applied, no way to revert.
     Fix: Always back up to Docs/_working/retro/Backups/ before modifying any file.

  3. MULTIPLE STRUCTURAL CHANGES AT ONCE
     Problem: Three new rules + routing rewrite + new agent. Hard to tell what helped.
     Fix: Max one structural change per invocation.

  4. MODIFYING GENESIS.MD
     Problem: Original intake record overwritten with current preferences.
     Fix: GENESIS.md is immutable. It records what was asked, not what evolved.

  5. PROPOSING WITHOUT EVIDENCE
     Problem: "I think we should add a new agent for X" without friction data.
     Fix: Every proposal must cite specific friction entries.

  6. NO EVOLUTION LOG
     Problem: Changes accumulate without record. Cannot trace what changed or why.
     Fix: Log every change in EVOLUTION.md with trigger, change, and backup path.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Skill description includes 3+ trigger phrases
  [ ] Negative trigger present ("Do NOT use for updating code or dependencies")
  [ ] SKILL.md body under 500 lines
  [ ] Critical instructions at top
  [ ] Phase 1 (Analysis) clearly separated from Phase 2 (Implementation)
  [ ] Evaluation-driven methodology referenced
  [ ] Proposal format with evidence, change, classification, risk
  [ ] Guardrails: self-modifiable vs human-only vs never-modify lists
  [ ] Max 1 structural change per invocation
  [ ] Backup before edit requirement
  [ ] EVOLUTION.md logging format specified
  [ ] GENESIS.md marked as never-modify
  [ ] Priority ordering for friction categories
  [ ] Premature victory prevention (verify before proposing)
  [ ] Progressive disclosure (references/proposal-format.md)
  [ ] No README.md in skill folder
  [ ] ASCII-only
-->

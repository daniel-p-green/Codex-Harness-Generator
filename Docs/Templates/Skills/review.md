# Review Skill (Template)

<!-- ANNOTATION: The review skill performs a quick review of current changes.
     Unlike the reviewer agent (which is delegated to by the orchestrator
     for deep reviews), this skill is user-invocable for quick checks.
     It is read-only and produces a CRITICAL/WARNING/SUGGESTION report. -->

<!-- QUALITY: Must show progressive disclosure structure. Must include
     proper description with trigger phrases. Must use the review rubric.
     Must be diff-based. SKILL.md under 500 lines. -->

## Progressive Disclosure Structure

```
review/
  SKILL.md                    # Core instructions (< 500 lines)
  scripts/
    collect-changes.sh        # Gather changed files (VCS-specific)
  references/
    review-criteria.md        # Detailed review criteria by domain (optional)
```

## Example: Review Skill (`.agents/skills/review/SKILL.md`)

````markdown
---
name: review
description: >
  Quick review of current changes. Use when the user says "review my changes",
  "review this", "check my code", "/review", or "what do you think of these
  changes". Reviews only modified files, not the entire codebase. Do NOT use
  for reviewing external PRs or commits -- that requires the full reviewer
  agent.
context: fork
tool access policy:
  - Read
  - Glob
  - Grep
  - Bash
metadata:
  version: 1.0.0
---

<!-- ANNOTATION: Frontmatter design decisions:
     - context: fork (isolated context to avoid polluting main conversation)
     - Bash allowed for running VCS diff commands
     - workspace writes are not allowed (review is read-only)
     - description: 5 trigger phrases, 1 negative trigger -->

## Critical: Review is Read-Only

<!-- ANNOTATION: This is the most important constraint. The review skill
     identifies issues but does not fix them. Fixing is a separate step
     that goes through the normal implementation pipeline. -->

This skill identifies issues in your changes. It does NOT modify files.
If issues are found, they will be reported for you to decide how to fix.

## Review Process

1. **Identify changes**
   Run the appropriate command to find modified files:
   ```bash
   # For Git:
   git diff --name-only HEAD
   git diff --staged --name-only

   # For Perforce:
   p4 opened -s
   ```

   <!-- VARIATION: Adapt the diff command to the project's VCS.
        If no VCS, ask the user which files to review. -->

2. **Read each changed file**
   - Read the full file (not just the diff) to understand context
   - Focus on the changed sections but check their interaction with
     surrounding code

3. **Apply the review rubric**
   For each file, check against the rubric below and categorize findings

4. **Produce the report**
   Output findings in priority order (CRITICAL first)

## Review Rubric

### CRITICAL (must fix before proceeding)
- Logic errors that produce incorrect results
- Crashes, unhandled exceptions, or panics
- Security issues (injection, auth bypass, exposed secrets)
- Data loss or corruption risks
- Resource leaks

### WARNING (should address)
- Missing error handling for likely failures
- Performance concerns in hot paths
- Unclear or misleading names
- Missing validation on external input
- Potential race conditions

### SUGGESTION (consider for quality)
- Style consistency
- Documentation opportunities
- Simplification possibilities
- Test coverage gaps

<!-- VARIATION: For knowledge work (document review):
     CRITICAL: factual errors, unsupported claims, contradictions
     WARNING: weak citations, unclear reasoning, missing context
     SUGGESTION: tone, structure, formatting -->

## Output Format

```markdown
## Review Summary

**Files reviewed**: <count>
**Assessment**: APPROVE / NEEDS_CHANGES / BLOCK

### CRITICAL
- [file:line] Issue. Impact. Suggested fix.

### WARNING
- [file:line] Issue. Risk.

### SUGGESTION
- [file:line] Suggestion.

### Overall
<1-2 sentence summary of the changes and their quality>
```

If reviewing more than 10 files, focus on the 5 highest-risk files
and note which files were skimmed.
````

## Example Script: `scripts/collect-changes.sh`

<!-- ANNOTATION: This script abstracts VCS-specific logic so the
     SKILL.md instructions can be VCS-agnostic. The component-generator
     should generate a VCS-appropriate version of this script. -->

```bash
#!/bin/bash
# Collect list of changed files for review
# Outputs one file path per line

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Git project
    echo "=== Staged changes ==="
    git diff --staged --name-only
    echo "=== Unstaged changes ==="
    git diff --name-only
    echo "=== Untracked files ==="
    git ls-files --others --exclude-standard
elif p4 info >/dev/null 2>&1; then
    # Perforce project
    echo "=== Opened files ==="
    p4 opened -s 2>/dev/null | sed 's/#.*//' | sed 's|//[^/]*/||'
else
    echo "No VCS detected. Please specify files to review."
    exit 1
fi
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] SKILL.md under 500 lines
     - [ ] Description includes 3+ trigger phrases
     - [ ] Description includes negative trigger
     - [ ] context: fork specified
     - [ ] Review is explicitly read-only (no workspace writes)
     - [ ] CRITICAL/WARNING/SUGGESTION rubric present
     - [ ] Domain-appropriate examples in each rubric tier
     - [ ] Output format includes assessment (APPROVE/NEEDS_CHANGES/BLOCK)
     - [ ] Diff-based approach (reviews changes, not entire codebase)
     - [ ] scripts/ directory used for VCS abstraction
     - [ ] No README.md inside the skill folder
-->

<!-- ANTI-PATTERN: Do not merge the review skill with the build skill.
     They serve different purposes: build checks if code compiles,
     review checks if code is correct and well-written. A user might
     want to review without building, or build without reviewing. -->

<!-- ANTI-PATTERN: Do not include the full review criteria in SKILL.md
     if it exceeds 100 lines. Put detailed criteria in
     references/review-criteria.md and keep SKILL.md focused on the
     process and rubric summary. -->

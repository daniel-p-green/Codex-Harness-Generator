# Review Workflow Rule (Template)

<!-- ANNOTATION: Generate this rule when the project benefits from code
     or document review. Almost all software projects should include this.
     Knowledge work projects may include a lighter version focused on
     document review rather than code review. -->

<!-- QUALITY: Must include CRITICAL/WARNING/SUGGESTION rubric.
     Must define diff-based review process. Must include self-review
     guidance. Under 120 lines. -->

## Example: Review Workflow Rule (`.claude/rules/review-workflow.md`)

```markdown
# Review workflow

Review changes before they are finalized. Prioritize findings by risk.

## Review rubric

<!-- ANNOTATION: The three-tier rubric ensures reviewers focus on what
     matters. Without this, reviews tend to be either too nitpicky
     (all style) or miss critical issues. -->

### CRITICAL (must fix before proceeding)
- Crashes, data loss, security vulnerabilities
- Incorrect business logic or broken functionality
- Resource leaks (memory, file handles, connections)
- Race conditions or data corruption risks

<!-- VARIATION: For game dev, add:
     - GC/UPROPERTY hazards (dangling references)
     - Authority/replication correctness
     - Unintended gameplay outcomes -->

<!-- VARIATION: For knowledge work (document review), replace with:
     - Factual errors or unsupported claims
     - Missing citations for key assertions
     - Contradictions with established findings -->

### WARNING (should fix, may defer with justification)
- Performance issues in hot paths
- Missing error handling for likely failure cases
- Unclear naming or confusing control flow
- Missing null checks or boundary validation

### SUGGESTION (nice to have, low risk)
- Style and formatting improvements
- Documentation improvements
- Testability enhancements
- Future-proofing opportunities

## How to review

<!-- ANNOTATION: This section defines the review process. The key
     insight is to review diffs, not entire files -- this keeps the
     review focused on what changed. -->

When asked to review changes:
1. Identify what changed (diff, file list, or changelist)
2. Read each changed file in the context of the change
3. Categorize every finding as CRITICAL, WARNING, or SUGGESTION
4. Present findings in priority order (CRITICAL first)
5. For large diffs: identify the 3-5 highest-risk files and focus there

### Review output format
```
## Review: <short description>

### CRITICAL
- [file:line] Issue description. Why it matters. Suggested fix.

### WARNING
- [file:line] Issue description. Risk. Suggested fix.

### SUGGESTION
- [file:line] Suggestion. Benefit.

### Summary
- X critical, Y warnings, Z suggestions
- Overall assessment: APPROVE / NEEDS_CHANGES / BLOCK
```

<!-- ANTI-PATTERN: Do not write "LGTM" without actually reviewing.
     Do not focus only on style when there are logic issues.
     Do not review files that were not changed (unless checking
     integration points). -->

## Self-review before submit

<!-- ANNOTATION: Self-review catches obvious issues before involving
     another person or agent. This is especially valuable when Claude
     is both the implementer and the reviewer (different agent instances). -->

Before declaring implementation complete:
1. Re-read all changed files
2. Check for:
   - TODO or FIXME comments left behind
   - Debug logging that should be removed
   - Commented-out code
   - Hardcoded values that should be configurable
3. Verify the changes match the original request
4. Run automated checks (lint, type check, tests) if available
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] Three-tier rubric (CRITICAL/WARNING/SUGGESTION) present
     - [ ] Each tier has domain-appropriate examples
     - [ ] Review output format specified
     - [ ] Self-review checklist included
     - [ ] Priority ordering (critical first) specified
     - [ ] Under 120 lines
-->

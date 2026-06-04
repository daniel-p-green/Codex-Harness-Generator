# Build Skill (Template)

<!-- ANNOTATION: The build skill demonstrates the feedback loop pattern:
     build -> parse errors -> fix -> rebuild. It is one of the most
     common skills in software development environments. Uses progressive
     disclosure with scripts/ for build execution and error parsing. -->

<!-- QUALITY: Must show progressive disclosure structure (SKILL.md + scripts/).
     Must include proper description with trigger phrases. Must demonstrate
     the feedback loop pattern. Must show error categorization. SKILL.md
     under 500 lines. -->

## Progressive Disclosure Structure

```
build/
  SKILL.md                    # Core instructions (< 500 lines)
  scripts/
    run-build.sh              # Build execution script
    parse-errors.sh           # Error extraction script (optional)
  references/
    error-reference.md        # Common error patterns and fixes (optional)
```

<!-- ANNOTATION: The scripts/ directory is key. Scripts execute without
     loading their source into context -- only their output is consumed.
     This saves significant tokens compared to generating build commands
     and parsing logic from scratch each time. -->

## Example: Build Skill (`.agents/skills/build/SKILL.md`)

````markdown
---
name: build
description: >
  Build the project and report results. Use when the user says "build",
  "compile", "run the build", "check if it compiles", or "/build". Also
  use after implementing code changes to verify they compile. Do NOT use
  for running tests (use the test command directly) or for deploying.
context: fork
tool access policy:
  - Read
  - Bash
  - Glob
  - Grep
metadata:
  version: 1.0.0
---

<!-- ANNOTATION: Frontmatter design decisions:
     - context: fork (runs in isolated subagent context)
     - uses shell commands to run build/test and `rg` plus targeted reads for
       investigating errors. Workspace writes are not included because the build
       skill should not fix errors -- it reports them.
     - description: includes 5 trigger phrases and 2 negative triggers
     VARIATION: For projects where the build skill should auto-fix
     simple errors (like missing imports), add Write and Edit to
     tool access policy and include fix instructions. -->

## Critical: Build Command

<!-- ANNOTATION: Critical instructions go at the TOP of SKILL.md,
     per OpenAI's skill authoring best practices. The build
     command is the most important piece of information. -->

Run this command to build:
```bash
./scripts/run-build.sh
```

If the script is not available, use:
```bash
npm run build
```

<!-- VARIATION: Adapt the build command to the project:
     - C++/UE: UnrealBuildTool invocation
     - Rust: cargo build
     - Go: go build ./...
     - TypeScript: npm run build / tsc
     - Python: pip install -e . (or no build step)
     - Java: mvn compile / gradle build -->

## Build-Fix-Rebuild Loop

<!-- ANNOTATION: This is the canonical feedback loop pattern from
     OpenAI's skill authoring guide. The key insight is to make
     validation scripts verbose with specific error messages so
     Codex can fix issues without human intervention. -->

1. Run the build command
2. If the build succeeds: report SUCCESS and stop
3. If the build fails:
   a. Read the FULL error output
   b. Identify the ROOT cause (first error, not cascading errors)
   c. Categorize the error (see below)
   d. Report the error with category and suggested fix
   e. Do NOT attempt to fix the error (report it to the orchestrator)

<!-- VARIATION: For projects where the build skill should attempt fixes:
     Replace step 3e with:
     e. If syntax/type error: fix the code and rebuild (max 3 retries)
     f. If dependency/config/infra error: report to user -->

## Error Categories

<!-- ANNOTATION: Categorizing errors helps the orchestrator decide
     whether to auto-fix (delegate to implementer) or report to
     the user (infrastructure issues). -->

| Category | Examples | Action |
|----------|----------|--------|
| Syntax error | Missing semicolon, unclosed bracket | Fixable by implementer |
| Type error | Wrong argument type, missing return | Fixable by implementer |
| Missing import | Unresolved symbol, module not found | Fixable by implementer |
| Missing dependency | Package not installed | Report to user |
| Configuration error | Wrong paths, missing env vars | Report to user |
| Infrastructure error | Disk full, permissions, network | Report to user |

## Output Format

```markdown
## Build Result: SUCCESS / FAILED

### Command
<exact command run>

### Output
<relevant build output -- truncate to last 50 lines if very long>

### Errors (if FAILED)
- Category: <error category>
- File: <path>
- Line: <line number>
- Error: <error message>
- Suggested fix: <what to change>

### Duration
<build time>
```
````

## Example Script: `scripts/run-build.sh`

<!-- ANNOTATION: The build script wraps the actual build command with
     timing and exit code handling. It can also set up environment
     variables or run pre-build checks. -->

```bash
#!/bin/bash
# Build script for the project
# Exits with 0 on success, non-zero on failure

set -e

echo "=== Build started at $(date) ==="

# Pre-build checks (optional)
# npm run lint 2>&1 || echo "Lint warnings (non-blocking)"

# Main build
npm run build 2>&1

EXIT_CODE=$?

echo "=== Build finished at $(date) with exit code $EXIT_CODE ==="
exit $EXIT_CODE
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] SKILL.md under 500 lines
     - [ ] Description includes 3+ trigger phrases
     - [ ] Description includes negative triggers
     - [ ] context: fork specified
     - [ ] Build command is project-specific (not placeholder)
     - [ ] Feedback loop pattern documented (build -> parse -> report)
     - [ ] Error categorization table present
     - [ ] Output format specified
     - [ ] scripts/ directory used for build execution
     - [ ] No README.md inside the skill folder
-->

<!-- ANTI-PATTERN: Do not put the actual build command only in the script
     and not in SKILL.md. If the script is missing or fails to execute,
     Codex needs to know the build command from SKILL.md directly. -->

<!-- ANTI-PATTERN: Do not include the full error reference in SKILL.md.
     Put it in references/error-reference.md and load on demand. This
     keeps SKILL.md focused and under the 500-line target. -->

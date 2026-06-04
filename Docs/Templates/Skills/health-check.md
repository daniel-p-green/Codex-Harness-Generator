# Health Check Skill (Template)

<!-- ANNOTATION: The health check skill validates the environment's
     structural and semantic integrity. It uses a two-layer approach:
     a deterministic script for structural checks (fast, reliable) and
     LLM-based analysis for semantic checks (deeper but slower). This
     is a core skill generated for every environment. -->

<!-- QUALITY: Must show two-layer approach (script + LLM). Must include
     deterministic validation script reference. Must output PASS/WARN/FAIL
     per check. Must use progressive disclosure structure. SKILL.md
     under 500 lines. -->

## Progressive Disclosure Structure

```
health-check/
  SKILL.md                    # Core instructions (< 500 lines)
  scripts/
    validate.sh               # Deterministic structural checks (or .py)
  references/
    troubleshooting.md        # How to fix common health issues (optional)
```

<!-- ANNOTATION: The scripts/ directory is critical for this skill.
     Deterministic validation via scripts is more reliable than LLM-based
     file existence checking. "Code is deterministic; language
     interpretation isn't" (OpenAI skills guide). -->

## Example: Health Check Skill (`.agents/skills/health-check/SKILL.md`)

````markdown
---
name: health-check
description: >
  Check the health and integrity of this Codex environment. Use when
  the user says "health check", "check environment", "validate setup",
  "is everything working", or "/health-check". Also useful after updates
  or when something seems broken. Do NOT use for checking application
  code health -- this checks the AI environment only.
context: fork
tool access policy:
  - Read
  - Glob
  - Grep
  - Bash
metadata:
  version: 1.0.0
---

## Critical: Two-Layer Validation

<!-- ANNOTATION: The two-layer approach is a key design pattern.
     Layer 1 (script) catches structural issues deterministically.
     Layer 2 (LLM) catches semantic issues that require understanding.
     Always run Layer 1 first -- it is fast and reliable. -->

This health check runs in two phases:
1. **Structural validation** (deterministic script)
2. **Semantic validation** (LLM-based analysis)

## Phase 1: Structural Validation

Run the validation script:
```bash
bash .agents/skills/health-check/scripts/validate.sh
```

<!-- VARIATION: For Windows-primary projects, use validate.py instead
     of validate.sh. Python scripts are more portable. -->

The script checks:
- All files referenced in AGENTS.md exist
- .codex/config.toml is valid TOML
- Skill folders use kebab-case naming
- Each skill directory contains SKILL.md
- Agent TOML files have required fields (name, description, developer_instructions, model, model_reasoning_effort, sandbox_mode)
- Wiki index.md (Docs/index.md) exists

Script outputs JSON:
```json
{
  "checks": [
    {"name": "agents-md-refs", "status": "PASS", "details": ""},
    {"name": "codex-config-toml", "status": "FAIL", "details": "Invalid TOML at line 15"}
  ],
  "summary": {"pass": 5, "warn": 1, "fail": 1}
}
```

If the script is not available, perform these checks manually using
Read, Glob, and Grep tools.

## Phase 2: Semantic Validation

After Phase 1 completes, perform these LLM-based checks:

1. **INDEX consistency**: Read Docs/index.md and verify it
   matches the actual directory contents
2. **Staleness**: Check "Last Updated" dates in key documents.
   Flag anything older than 30 days as WARN
3. **Routing completeness**: Read the routing rule and verify every
   common intent has a route with a fallback
4. **Rule contradictions**: Scan rule files for instructions that
   contradict each other
5. **State symmetry**: Verify /state-save and /state-load cover
   the same categories
6. **Retro patterns**: If Docs/_working/retro/ exists, check for recurring
   FRICTION entries that suggest unresolved issues

<!-- VARIATION: Add domain-specific semantic checks:
     - Software dev: verify build command matches project files
     - Knowledge work: verify document templates exist
     - Game dev: verify binary asset protection rules -->

## Output Format

```markdown
## Environment Health Report

Date: YYYY-MM-DD

### Structural Checks (Script)
| Check | Status | Details |
|-------|--------|---------|
| AGENTS.md references | PASS/WARN/FAIL | ... |
| .codex/config.toml valid | PASS/WARN/FAIL | ... |
| Skill folder naming | PASS/WARN/FAIL | ... |
| Agent frontmatter | PASS/WARN/FAIL | ... |
| Wiki index exists | PASS/WARN/FAIL | ... |

### Semantic Checks (LLM)
| Check | Status | Details |
|-------|--------|---------|
| INDEX consistency | PASS/WARN/FAIL | ... |
| Document staleness | PASS/WARN/FAIL | ... |
| Routing completeness | PASS/WARN/FAIL | ... |
| Rule contradictions | PASS/WARN/FAIL | ... |
| State symmetry | PASS/WARN/FAIL | ... |

### Summary
- Total: X pass, Y warn, Z fail
- Overall: HEALTHY / NEEDS_ATTENTION / DEGRADED
```

### Status definitions
- **PASS**: Check passed, no issues
- **WARN**: Minor issue, environment works but could be improved
- **FAIL**: Issue that may cause problems, should be fixed

### Recommended actions
For each WARN or FAIL, include a one-line recommendation for how to fix it.
````

## Example Script: `scripts/validate.sh`

<!-- ANNOTATION: This script performs fast, deterministic structural
     checks. Its output is JSON so the LLM can parse it reliably.
     The script should complete in under 5 seconds. -->

```bash
#!/bin/bash
# Structural validation for Codex environment
# Outputs JSON with check results

PASS=0
WARN=0
FAIL=0
CHECKS="["

add_check() {
    local name="$1" status="$2" details="$3"
    if [ "$CHECKS" != "[" ]; then CHECKS="$CHECKS,"; fi
    CHECKS="$CHECKS{\"name\":\"$name\",\"status\":\"$status\",\"details\":\"$details\"}"
    case "$status" in
        PASS) PASS=$((PASS+1)) ;;
        WARN) WARN=$((WARN+1)) ;;
        FAIL) FAIL=$((FAIL+1)) ;;
    esac
}

# Check 1: AGENTS.md exists
if [ -f "AGENTS.md" ]; then
    add_check "agents-md-exists" "PASS" ""
else
    add_check "agents-md-exists" "FAIL" "AGENTS.md not found in project root"
fi

# Check 2: .codex/config.toml is valid TOML
if [ -f ".codex/config.toml" ]; then
    if python3 -c "import tomllib; tomllib.load(open('.codex/config.toml','rb'))" 2>/dev/null; then
        add_check "codex-config-toml-valid" "PASS" ""
    else
        add_check "codex-config-toml-valid" "FAIL" ".codex/config.toml contains invalid TOML"
    fi
else
    add_check "codex-config-toml-valid" "WARN" "No .codex/config.toml found"
fi

# Check 3: Skill folders use kebab-case
for dir in .agents/skills/*/; do
    if [ -d "$dir" ]; then
        dirname=$(basename "$dir")
        if echo "$dirname" | grep -qE '^[a-z][a-z0-9-]*$'; then
            add_check "skill-naming-$dirname" "PASS" ""
        else
            add_check "skill-naming-$dirname" "FAIL" "Skill folder '$dirname' is not kebab-case"
        fi
    fi
done

# Check 4: Each skill has SKILL.md
for dir in .agents/skills/*/; do
    if [ -d "$dir" ]; then
        dirname=$(basename "$dir")
        if [ -f "${dir}SKILL.md" ]; then
            add_check "skill-md-$dirname" "PASS" ""
        else
            add_check "skill-md-$dirname" "FAIL" "Missing SKILL.md in $dir"
        fi
    fi
done

# Check 5: Wiki index exists
if [ -f "Docs/index.md" ]; then
    add_check "memory-index" "PASS" ""
else
    add_check "memory-index" "WARN" "No Docs/index.md found"
fi

CHECKS="$CHECKS]"

echo "{\"checks\":$CHECKS,\"summary\":{\"pass\":$PASS,\"warn\":$WARN,\"fail\":$FAIL}}"
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] SKILL.md under 500 lines
     - [ ] Description includes 3+ trigger phrases and negative trigger
     - [ ] context: fork specified
     - [ ] Two-layer approach: script (structural) + LLM (semantic)
     - [ ] Validation script exists in scripts/ directory
     - [ ] Script outputs JSON (not free text)
     - [ ] PASS/WARN/FAIL status per check
     - [ ] Output format includes summary table
     - [ ] Overall status (HEALTHY/NEEDS_ATTENTION/DEGRADED)
     - [ ] Recommended actions for WARN and FAIL items
     - [ ] No README.md inside the skill folder
-->

<!-- ANTI-PATTERN: Do not rely solely on LLM-based validation. The
     deterministic script is faster and more reliable for structural
     checks. Use LLM analysis only for semantic checks that require
     understanding context and meaning. -->

<!-- ANTI-PATTERN: Do not make the health check modify files. It is
     a diagnostic tool that reports issues. Fixing issues is a separate
     operation (either manual or via /update). Write is NOT in
     tool access policy for this reason. -->

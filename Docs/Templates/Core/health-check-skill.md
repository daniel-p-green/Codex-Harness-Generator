# Template: Health-Check Skill (/health-check)

<!-- TEMPLATE ANNOTATION
  This template defines the /health-check skill that validates environment
  integrity using a two-layer approach: deterministic script (structural checks)
  and LLM-based analysis (semantic checks).

  QUALITY CRITERIA:
  - Skill description includes 3+ trigger phrases
  - SKILL.md body under 500 lines
  - Two-layer validation (deterministic + semantic)
  - scripts/validate.sh reference for structural checks
  - PASS/WARN/FAIL output format
  - Progressive disclosure structure
  - Specific checks enumerated

  WHY THIS EXISTS:
  Environments degrade over time. Files get deleted, cross-references break,
  rules contradict each other, state files go stale. Without periodic validation,
  these issues accumulate silently until something breaks during actual use.

  The two-layer approach combines the reliability of deterministic scripts
  (checking file existence, JSON validity) with the intelligence of LLM analysis
  (detecting contradictions, stale content, routing gaps).
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application

  File structure:
  .claude/skills/health-check/
    SKILL.md              (this file -- core instructions)
    scripts/
      validate.sh           (deterministic structural validation)
    references/
      check-catalog.md      (full catalog of all checks with details)
============================================================ -->

## SKILL.md

```yaml
---
name: health-check
description: Validate environment integrity and freshness. Use when the user says "health check", "validate environment", "check my setup", "is everything working", "run diagnostics", or "/health-check". Do NOT use for checking code quality or running tests.
context: fork
allowed-tools: [Read, Glob, Grep, Bash]
metadata:
  author: Claude Harness Generator
  version: 1.0.0
---
```

## Critical

- Run the deterministic script FIRST. It catches structural issues quickly and reliably.
- Then run semantic checks for issues the script cannot detect.
- Output a brief health report with PASS/WARN/FAIL per check.
- Do NOT modify any files. Health-check is read-only validation.
- Use progressive disclosure: brief report first, details on request.

## Layer 1: Deterministic validation

<!-- DETERMINISTIC LAYER
  WHY: "Code is deterministic; language interpretation isn't." Structural checks
  (file exists, JSON is valid, frontmatter has required fields) should be done
  by a script, not by LLM reasoning. Scripts are faster, cheaper, and more reliable.
-->

Run `scripts/validate.sh` from the project root. The script checks:

### Structural checks

| Check | What it validates | Severity |
|---|---|---|
| S1: CLAUDE.md exists | `./CLAUDE.md` or `./.claude/CLAUDE.md` present | FAIL |
| S2: Settings valid JSON | `.claude/settings.json` parses without errors | FAIL |
| S3: Skill folders | Each `.claude/skills/*/` has a `SKILL.md` file | FAIL |
| S4: Skill naming | Skill folder names are kebab-case (lowercase + hyphens) | WARN |
| S5: No skill README | No `README.md` inside skill folders | WARN |
| S6: Agent frontmatter | Each `.claude/agents/*.md` has name, description, maxTurns in frontmatter | FAIL |
| S7: Wiki index | `Docs/index.md` exists | FAIL |
| S8: State directory | `Docs/_working/state/` directory exists | WARN |
| S9: Retro directory | `Docs/_working/retro/` directory exists | WARN |
| S10: File size limits | CLAUDE.md < 250 lines, rules < 120 lines, agents < 80 lines | WARN |
| S11: SKILL.md size | Each SKILL.md < 500 lines | WARN |
| S12: Settings deny rules | `settings.json` has non-empty `permissions.deny` array | WARN |

### Script output format

The script outputs JSON:

```json
{
  "timestamp": "2026-02-14T15:30:00Z",
  "checks": [
    {"id": "S1", "name": "CLAUDE.md exists", "status": "PASS", "detail": ""},
    {"id": "S2", "name": "Settings valid JSON", "status": "PASS", "detail": ""},
    {"id": "S10", "name": "File size limits", "status": "WARN", "detail": "CLAUDE.md is 267 lines (limit: 250)"}
  ],
  "summary": {"pass": 10, "warn": 2, "fail": 0}
}
```

## Layer 2: Semantic validation

<!-- SEMANTIC LAYER
  WHY: Some checks require understanding content, not just structure.
  "Do the routing entries cover all intent categories?" requires reading
  the routing table and reasoning about completeness. Scripts cannot do this.
-->

After the script completes, perform these LLM-based checks:

| Check | What it validates | Severity |
|---|---|---|
| L1: Cross-references | All file paths referenced in CLAUDE.md actually exist | FAIL |
| L2: Routing completeness | Routing table covers: bugs, features, exploration, refactor, ambiguous (at minimum) | WARN |
| L3: Routing specificity | Routing entries use domain-specific terms (not generic "bug -> debugger") | WARN |
| L4: Rule consistency | No contradictory rules across rule files (e.g., autonomy says "ask" but routing says "act") | FAIL |
| L5: INDEX freshness | Docs/index.md matches actual directory contents | WARN |
| L6: Stale documents | Documents with "Last Updated" older than 30 days | WARN |
| L7: Retro patterns | Friction entries with 3+ occurrences that have no corresponding proposal | WARN |
| L8: State symmetry | State-save covers all 6 taxonomy categories AND state-load reads all of them | WARN |
| L9: Permission coverage | settings.json allows all tools referenced by agents and skills | WARN |
| L10: Orphan components | Agents or skills referenced in routing but whose files do not exist | FAIL |

## Output format

<!-- OUTPUT FORMAT
  WHY: Progressive disclosure. The brief report shows status at a glance.
  Users who want details can ask. This keeps the main output concise.
-->

### Brief report (always shown)

```
## Health Check Report

Run: 2026-02-14 15:30 UTC
Environment: Acme Dashboard

### Summary
PASS: 18/22 checks passed
WARN: 3 warnings
FAIL: 1 failure

### Failures (action required)
- [FAIL] L10: Orphan component -- .claude/agents/perf-analyst.md referenced in routing but file missing

### Warnings
- [WARN] S10: CLAUDE.md is 267 lines (limit: 250) -- consider trimming
- [WARN] L6: Docs/Areas/auth.md last updated 45 days ago
- [WARN] L7: 4 ROUTING_CORRECTION entries without a proposal

### Recommendation
Fix the FAIL item first (create or remove the orphaned agent reference).
Run /update to address the routing corrections.
```

### Detailed report (on request)

If the user asks for details on any check, provide:
- What was checked
- What was expected
- What was found
- Suggested fix

## scripts/validate.sh

<!-- SCRIPT
  WHY: Deterministic validation runs without consuming LLM tokens.
  This script handles all structural checks that do not require reasoning.
  It outputs JSON that the LLM layer can parse and augment.
-->

```bash
#!/usr/bin/env bash
# Health check: deterministic structural validation
# Usage: bash .claude/skills/health-check/scripts/validate.sh
# Output: JSON to stdout

set -euo pipefail

PASS=0
WARN=0
FAIL=0
CHECKS="["

add_check() {
  local id="$1" name="$2" status="$3" detail="${4:-}"
  [ "$CHECKS" != "[" ] && CHECKS="$CHECKS,"
  CHECKS="$CHECKS{\"id\":\"$id\",\"name\":\"$name\",\"status\":\"$status\",\"detail\":\"$detail\"}"
  case "$status" in
    PASS) PASS=$((PASS+1)) ;;
    WARN) WARN=$((WARN+1)) ;;
    FAIL) FAIL=$((FAIL+1)) ;;
  esac
}

# S1: CLAUDE.md exists
if [ -f "./CLAUDE.md" ] || [ -f "./.claude/CLAUDE.md" ]; then
  add_check "S1" "CLAUDE.md exists" "PASS"
else
  add_check "S1" "CLAUDE.md exists" "FAIL" "No CLAUDE.md found"
fi

# S2: Settings valid JSON
if [ -f ".claude/settings.json" ]; then
  if python3 -c "import json; json.load(open('.claude/settings.json'))" 2>/dev/null; then
    add_check "S2" "Settings valid JSON" "PASS"
  else
    add_check "S2" "Settings valid JSON" "FAIL" "Invalid JSON in settings.json"
  fi
else
  add_check "S2" "Settings valid JSON" "WARN" "No settings.json found"
fi

# S3: Skill folders have SKILL.md
for dir in .claude/skills/*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  if [ -f "${dir}SKILL.md" ]; then
    add_check "S3-$name" "Skill $name has SKILL.md" "PASS"
  else
    add_check "S3-$name" "Skill $name has SKILL.md" "FAIL" "Missing SKILL.md in $dir"
  fi
done

# S4: Skill naming (kebab-case)
for dir in .claude/skills/*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  if echo "$name" | grep -qE '^[a-z][a-z0-9-]*$'; then
    add_check "S4-$name" "Skill $name naming" "PASS"
  else
    add_check "S4-$name" "Skill $name naming" "WARN" "Not kebab-case: $name"
  fi
done

# S5: No README.md in skill folders
for dir in .claude/skills/*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  if [ -f "${dir}README.md" ]; then
    add_check "S5-$name" "No README in $name" "WARN" "README.md found in skill folder"
  fi
done

# S7: Wiki index
if [ -f "Docs/index.md" ]; then
  add_check "S7" "Wiki index exists" "PASS"
else
  add_check "S7" "Wiki index exists" "FAIL" "Docs/index.md missing"
fi

# S10: File size limits
if [ -f "./CLAUDE.md" ]; then
  lines=$(wc -l < "./CLAUDE.md")
  if [ "$lines" -le 250 ]; then
    add_check "S10-claude" "CLAUDE.md size" "PASS" "$lines lines"
  else
    add_check "S10-claude" "CLAUDE.md size" "WARN" "$lines lines (limit: 250)"
  fi
fi

# S12: Settings deny rules
if [ -f ".claude/settings.json" ]; then
  deny_count=$(python3 -c "import json; d=json.load(open('.claude/settings.json')); print(len(d.get('permissions',{}).get('deny',[])))" 2>/dev/null || echo 0)
  if [ "$deny_count" -gt 0 ]; then
    add_check "S12" "Settings deny rules" "PASS" "$deny_count deny rules"
  else
    add_check "S12" "Settings deny rules" "WARN" "No deny rules in settings.json"
  fi
fi

CHECKS="$CHECKS]"

cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": $CHECKS,
  "summary": {"pass": $PASS, "warn": $WARN, "fail": $FAIL}
}
EOF
```

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Script checks for git configuration, test runner availability
  - Semantic checks for build system integration

  KNOWLEDGE WORK:
  - Script checks simplified (fewer structural requirements)
  - Semantic checks focus on: source freshness, citation format, document structure
  - No build/test related checks

  GAME DEVELOPMENT:
  - Script checks for VCS (Perforce) configuration
  - Additional checks: binary asset rules present, playtest gate defined
  - Semantic checks for: replication rules consistency, performance guidelines

  CROSS-PLATFORM:
  - validate.sh may need a Python equivalent (validate.py) for Windows
  - Use #!/usr/bin/env bash and test for bash availability
  - Consider: validate.py as default with bash wrapper
-->

<!-- ANTI-PATTERNS

  1. LLM-ONLY VALIDATION
     Problem: All checks done by LLM reasoning. Slow, expensive, inconsistent.
     Fix: Deterministic script for structural checks. LLM only for semantic analysis.

  2. MODIFYING FILES DURING CHECK
     Problem: Health-check "fixes" issues it finds without asking.
     Fix: "Do NOT modify any files. Health-check is read-only validation."

  3. NO SEVERITY LEVELS
     Problem: All issues reported as "problem." User cannot prioritize.
     Fix: PASS/WARN/FAIL with clear severity definitions.

  4. VERBOSE DEFAULT OUTPUT
     Problem: 22 checks with full details dumped into conversation.
     Fix: Progressive disclosure. Brief summary first, details on request.

  5. MISSING SCRIPT OUTPUT FORMAT
     Problem: Script prints human-readable text. LLM must parse prose.
     Fix: Script outputs JSON. LLM parses structured data.

  6. NO ACTIONABLE RECOMMENDATIONS
     Problem: "3 warnings found." User does not know what to do.
     Fix: Each check includes a suggested fix. Summary includes recommended next action.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Skill description includes 3+ trigger phrases
  [ ] Negative trigger present ("Do NOT use for checking code quality")
  [ ] SKILL.md body under 500 lines
  [ ] Critical instructions at top
  [ ] Two-layer approach (deterministic + semantic)
  [ ] Deterministic checks enumerated with IDs
  [ ] Semantic checks enumerated with IDs
  [ ] scripts/validate.sh with JSON output
  [ ] PASS/WARN/FAIL severity levels defined
  [ ] Brief report format specified
  [ ] Progressive disclosure (brief first, details on request)
  [ ] Read-only (no file modifications)
  [ ] Actionable recommendations in output
  [ ] No README.md in skill folder
  [ ] Script handles missing files gracefully
  [ ] ASCII-only
-->

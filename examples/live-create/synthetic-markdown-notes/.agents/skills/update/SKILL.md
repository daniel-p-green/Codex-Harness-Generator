---
name: update
description: Use when the user says "improve this harness", "update the rules", "learn from these misses", "/update", or when retro notes show repeated friction in synthetic documentation workflows. Do not use for ordinary note drafting or project-plan edits.
---

## Critical

Make the smallest harness change that fixes a repeated pattern. Do not add new assistants, integrations, or rules unless the retro evidence justifies them.

## Steps

1. Read `Docs/_working/retro/` and identify repeated patterns.
2. Read the relevant current harness files before proposing edits.
3. Propose a short change list with expected benefit and risk.
4. Apply only approved or clearly requested changes.
5. Run `/health-check` or equivalent validation after edits.

## Retro Entry Shape

Each pattern should include evidence, impact, proposed fix, and whether the fix belongs in rules, skills, agents, or docs.

## Output

Return changed files, validation result, and any deferred improvements.

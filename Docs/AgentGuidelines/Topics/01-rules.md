# 1. Rules

## 1.1 Structure and Organization

- **Established**: Baseline
- **Source**: claude-code-docs.md, claude-code-best-practices.md | Tier 1
- **Recommendation**: Organize rules as separate `.md` files in `.claude/rules/`. Each file
  covers one concern (orchestrator, autonomy, context-management, self-learning,
  error-handling, memory-management). Use a numbered prefix (00-, 01-, 02-) for loading
  order clarity. All `.md` files in `.claude/rules/` are automatically loaded as project
  memory.
- **Anti-pattern**: Putting all rules into CLAUDE.md. This bloats the file and causes Claude
  to ignore important instructions. Rules files provide modularity without losing visibility.

## 1.2 File Sizing

- **Established**: Baseline
- **Source**: claude-code-best-practices.md, context-engineering.md | Tier 1
- **Recommendation**: Keep individual rule files under 120 lines. CLAUDE.md under 250 lines
  (ideally 150-200). For each line, ask: "Would removing this cause Claude to make mistakes?"
  If not, cut it. Bloated instruction files cause Claude to ignore actual instructions.
- **Anti-pattern**: Comprehensive rules that cover every edge case. Claude already knows
  standard conventions. Only document what differs from defaults, what Claude cannot infer
  from code, and non-obvious gotchas.

## 1.3 Intent-Behind-Rules

- **Established**: 2025-09 (Opus 4.6 release); reinforced on 4.7
- **Source**: opus-4-6-guide.md, context-engineering.md,
  platform.claude.com/docs/en/build-with-claude/prompt-engineering | Tier 1
- **Recommendation**: Every constraint must include WHY, not just WHAT. Opus follows
  rules with stated intent more reliably than bare rules. Even more important on 4.7,
  which reads instructions literally -- without stated intent, 4.7 applies rules narrowly
  to exactly what is stated rather than the broader spirit.
  - Bad: "Always use TypeScript strict mode"
  - Good: "Always use TypeScript strict mode because our CI pipeline rejects non-strict
    files and we have had production bugs from implicit any"
- **Anti-pattern**: Bare lists of rules without rationale. The model may interpret ambiguous
  rules differently than intended when context is missing.

## 1.4 Include/Exclude Rubric

- **Established**: Baseline
- **Source**: claude-code-best-practices.md | Tier 1
- **Recommendation**: Include in CLAUDE.md:
  - Bash commands Claude cannot guess (custom build, test, deploy commands)
  - Code style rules that differ from defaults
  - Testing instructions and preferred test runners
  - Repository etiquette (branch naming, PR conventions)
  - Architectural decisions specific to the project
  - Developer environment quirks (required env vars, ports, paths)
  - Common gotchas or non-obvious behaviors

  Exclude from CLAUDE.md:
  - Anything Claude can figure out by reading code
  - Standard language conventions Claude already knows
  - Detailed API documentation (link instead)
  - Information that changes frequently
  - Long explanations or tutorials
  - File-by-file descriptions of the codebase
  - Self-evident practices like "write clean code"
- **Anti-pattern**: Including standard conventions or things Claude already does correctly.
  Every unnecessary line dilutes the signal of important instructions.

## 1.5 Emphasis Tuning

- **Established**: Baseline
- **Source**: claude-code-best-practices.md | Tier 1
- **Recommendation**: Use "IMPORTANT" or "YOU MUST" for critical rules to improve adherence.
  Use regular text for guidelines and preferences. Reserve capitalized emphasis for rules
  where violations have caused real problems. If Claude keeps ignoring a rule despite
  emphasis, the file is probably too long -- prune other content first.
- **Anti-pattern**: Making everything IMPORTANT. When everything is emphasized, nothing is
  emphasized. The model normalizes the emphasis level and stops distinguishing priorities.

## 1.6 Path-Specific Rules

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: Use YAML frontmatter with `paths` to scope rules to specific file
  patterns. Example: API-specific rules only load when Claude works with API files.
  ```yaml
  ---
  paths:
    - "src/api/**/*.ts"
  ---
  # API Rules (only apply when working with API files)
  ```
  Supports glob patterns and brace expansion (`*.{ts,tsx}`, `{src,lib}/**`).
- **Anti-pattern**: Loading all rules globally when some only apply to specific areas of the
  codebase. This wastes context tokens on irrelevant instructions.

---

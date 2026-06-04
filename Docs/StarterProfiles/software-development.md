# Starter Profile: Software Development

Follows `Docs/StarterProfiles/PROFILE_FORMAT.md` (slim). A starting point the
architect adapts -- it points at templates, it does not inline them.

## Profile Metadata

- **Target audience**: developers building web apps, APIs, CLIs, libraries, services
- **Languages**: Python, Node/TypeScript, Go, Rust, Java, C# (pick per intake)
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: proactive | **VCS**: Git

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| researcher | high-effort | Research APIs/libraries/patterns before implementation | researcher.md |
| planner | high-effort | Break features/refactors into buildable checkpoints | planner.md |
| implementer | medium-effort | Implement one checkpoint at a time, run verification | implementer.md |
| reviewer | high-effort | Review changes for correctness/security/perf (read-only) | reviewer.md |
| explorer | medium-effort | Locate code, map call chains and dependencies | explorer.md |
| debugger | high-effort | Reproduce, hypothesize, fix, verify | debugger.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy, context-management, self-learning, error-handling (with diagnostic
discipline), memory-management, and `vcs-git.md`.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/build`, `/review`;
conditional `/map-codebase` (Pattern F -- when 50+ files or navigation is hard).

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | Bug in API endpoint / route handler | debugger (handler, middleware, request flow) | Include error + stack trace | explorer -> debugger |
| 2 | Test failure / test not passing | debugger (read output, fixtures, expected vs actual) | Include test command output | answer directly (trivial assertion) |
| 3 | New feature (clear scope) | planner -> implementer -> reviewer | One checkpoint at a time; verify between | intake (if scope unclear) |
| 4 | New feature (vague / broad) | clarify -> planner -> implementer -> reviewer | Gather requirements first | researcher (if domain knowledge needed) |
| 5 | Refactor / restructure | planner -> implementer -> reviewer | Plan boundaries; verify no behavior change | explorer (map dependencies first) |
| 6 | Code review / review my changes | reviewer | Read git diff, classify findings | answer directly (single file) |
| 7 | "Where is X" / find the file | explorer | Search by filename, symbol, content | answer directly (obvious) |
| 8 | "How does X work" / architecture | researcher -> explorer | Docs first, then code | answer directly (well-documented) |
| 9 | Performance issue / optimization | explorer (profile, hotspots) -> researcher | Include profiling/timing data | debugger (if actually a bug) |
| 10 | Database / schema migration | planner (migration + model updates) -> implementer | Include ORM/migration tool | researcher (unfamiliar tool) |
| 11 | Dependency update / library upgrade | researcher (changelog, breaking changes) -> planner -> implementer | Check compatibility first | explorer (find usage sites) |
| 12 | CI/CD pipeline issue / build failure | debugger (build logs, config) | Include build log output | explorer -> debugger |
| 13 | Security concern / vulnerability fix | researcher (CVE, best practices) -> implementer -> reviewer | Reviewer checks security | debugger (repro needed) |
| 14 | Documentation / README update | answer directly (draft) | Use project doc conventions | researcher (accuracy check) |
| 15 | Config change / env setup | answer directly or implementer (multi-file) | Check existing config patterns | explorer (find config files) |
| 16 | "Explain this code" | explorer (read and summarize) | Include file path + line range | answer directly (code in message) |

Complexity scaling: Simple (1 agent, direct answers/config/doc) | Standard (2-3
agents: bug fixes, single-file features, reviews) | Complex (3-5 agents serial:
multi-file features, refactors, migrations).

## Ecosystem Permissions

Base + Universal Deny + Git, plus the language ecosystem(s) the intake names --
all in `Docs/Templates/References/ecosystem-permissions.md`. Add `Docs(...)`
output paths the implementer commonly writes (test fixtures, migrations) to avoid
permission prompts. Generate `local config profile` for machine-specific paths.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Context exhaustion on large refactors -- implementer runs
  out of context past ~10 files. Mitigation: max 5 files per checkpoint.
- [PATTERN] (pre-seeded) "Fix" vs "rewrite" routing ambiguity -- when a fix needs a
  new approach (not just correcting a mistake), route to planner first.
- [PATTERN] (pre-seeded) Permission prompts for new file paths -- implementer creates
  files outside pre-approved dirs. Add common output paths to .codex/config.toml.
- [PATTERN] (pre-seeded) Code mismatches project conventions -- explorer should check
  existing import/error-handling style before implementation.
- [PATTERN] (pre-seeded) state-load misses newly added files -- artifact state should
  distinguish "new files" from "modified files".
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) and **Stop hook self-review**
  (recommended for code-producing work) -- see `Docs/Templates/Optional/hooks-template.md`.
- Optional **PostToolUse** test-on-edit for fast suites (exit code 2 feeds
  failures back). Keep a re-entry guard on Stop hooks.

## Cost / Model Notes

high-effort GPT-5.5 for planner/debugger/reviewer/researcher; medium-effort GPT-5.5 for implementer/explorer.
Defaults: balanced (high-effort GPT-5.5 on reasoning roles, medium-effort GPT-5.5 on execution; compaction 95%;
AGENTS.md ~200 lines). Cost-conscious override: all medium-effort GPT-5.5, compaction 85%,
AGENTS.md ~150, full RTK in GETTING_STARTED. Subagents ~4x, teams ~15x vs direct.

## Customization Points

Language/framework (drives ecosystem permissions + verify commands); solo vs team
(team -> multi-role + team template); test/CI gates; existing codebase scale
(-> /map-codebase, semantic-search MCP); sensitive data (-> data rules/hooks).

## Team-architecture pattern

Producer-Reviewer (implement -> review) within a Pipeline (plan -> implement ->
review). Subagents are the default; consider Agent Teams only for a feature that
cleanly splits across non-overlapping areas (backend / frontend / tests) -- prefer
`codex with worktrees` (~4x) over teams (~15x) for parallel file work.

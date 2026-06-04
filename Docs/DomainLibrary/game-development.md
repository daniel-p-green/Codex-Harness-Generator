# Bundled Domain: Game Development

Builds on the **software-development** base profile and specializes it for engine
work (Unreal C++, Unity C#, Godot GDScript/C#).

Follows `Docs/StarterProfiles/PROFILE_FORMAT.md` (slim). A starting point the
architect adapts -- it points at templates, it does not inline them. Patterns
here are validated against a production Unreal Engine 5 C++ project (manual
playtest gates, Perforce, multi-agent orchestration).

## Profile Metadata

- **Target audience**: developers on Unreal (C++), Unity (C#), Godot (GDScript/C#), or custom engines
- **Engines/languages**: pick per intake -- drives build commands, asset patterns, ecosystem permissions
- **Complexity**: Extended | **Memory tier**: Standard (dual-wiki option below) | **Action default**: proactive (except playtest gates) | **VCS**: Git default, Perforce variant

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| researcher | high-effort | Research engine APIs, gameplay/networking/rendering patterns; check wiki before web | researcher.md |
| planner | high-effort | Break features/refactors into independently compilable checkpoints (PT-XX) | planner.md |
| implementer | medium-effort | Implement ONE checkpoint; preserve reflection macros; never touch binary assets | implementer.md |
| reviewer | high-effort | Review changes (read-only); rubric crashes > GC > replication > perf > style | reviewer.md |
| explorer | medium-effort | Locate code, map class hierarchy/call flow/replication boundaries | explorer.md |
| debugger | high-effort | Reproduce, hypothesize, fix crashes/gameplay/replication bugs, verify | debugger.md |
| performance-analyst | medium-effort | Analyze profiling data, find hotspots (tick, traces, draw calls, GC) | performance-analyst.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (binary-asset protection), context-management (preserve replication
intent + build status), self-learning (game categories), error-handling (with
diagnostic discipline + crash-log interpretation), memory-management,
`build-system.md`, `testing-gates.md` (playtest gate), and `vcs-git.md` or
`vcs-perforce.md`.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/build`, `/review`;
conditional `/map-codebase` (Pattern F -- large engine codebases).

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | Gameplay bug (wrong behavior, incorrect state) | debugger (ability system, component state, event flow) | Include repro + expected vs actual | explorer -> debugger |
| 2 | Crash / callstack / access violation | debugger (callstack, UPROPERTY/GC, null pointers) | Include full callstack and log snippet | explorer -> debugger |
| 3 | Replication / multiplayer bug | debugger (authority, role, net relevancy, RPC params) | Specify client/server/both and player count | researcher (replication docs) -> debugger |
| 4 | Build failure / compile error | debugger (parse build log, includes, fix errors) | Include full build output | explorer (if error names unknown file) -> debugger |
| 5 | New gameplay feature (clear scope) | planner -> implementer -> reviewer -> /build | One checkpoint at a time; playtest gate after each | researcher (if engine API unfamiliar) |
| 6 | New gameplay feature (vague / broad) | clarify -> planner -> implementer -> reviewer -> /build | Gather replication needs, input bindings, asset deps | researcher (if design pattern needed) |
| 7 | Refactor / restructure game system | planner -> implementer -> reviewer -> /build | Plan boundaries; verify no gameplay behavior change | explorer (map dependencies first) |
| 8 | Performance issue / FPS drop / hitching | performance-analyst (hotspots) -> planner -> implementer | Include profiling data or when perf degrades | explorer (if unclear which system) |
| 9 | "Where is X" / "Find the class for Y" | explorer | Search filename, symbol, class hierarchy | answer directly (obvious from structure) |
| 10 | "How does X work" / engine system question | researcher -> explorer (if code facts needed) | Engine docs first, then source | answer directly (well-documented) |
| 11 | Asset issue (missing reference, broken Blueprint) | explorer (asset dependencies, references) | Binary assets not editable -- describe editor fix | answer directly (simple re-path) |
| 12 | Blueprint / editor change needed | answer directly (exact editor steps) -> STOP | Cannot edit .uasset/.umap/.prefab; user does it in editor | explorer (if unclear which Blueprint) |
| 13 | Animation / montage issue | explorer (montage setup, notify timings) -> debugger | Include montage name, section, observed behavior | researcher (if anim system unfamiliar) |
| 14 | UI / widget bug | debugger (widget hierarchy, binding, visibility) | Specify HUD, menu, or overlay | explorer -> debugger |
| 15 | AI / behavior tree issue | debugger (BT nodes, blackboard, decorators) | Include BT asset name, expected vs actual | explorer (map BT structure) -> debugger |
| 16 | Code review / review my changes | reviewer (game review rubric) | Read VCS diff, classify findings | answer directly (single file) |
| 17 | Networking / RPC question | researcher (replication model, RPC types, net serialization) | Specify engine and network model | answer directly (basic RPC syntax) |
| 18 | Plugin / module architecture | explorer (module structure, deps, public API) | Include plugin name and what is needed | researcher (if module-system docs needed) |
| 19 | Input system / controls | explorer (input bindings, action mappings) -> implementer | Specify keyboard, gamepad, touch, or all | researcher (if Enhanced Input / new system) |
| 20 | Ability system / GAS issue (Unreal) | debugger (ability spec, effect, cue, attribute set) | Include ability class, conditions, observed behavior | researcher (GAS docs) -> debugger |

Complexity scaling: Simple (1 agent, <5 calls -- code questions, simple fixes,
editor-step descriptions) | Standard (2-3 agents -- bug fixes, single-system
features, reviews) | Complex (5-7 agents serial -- multi-system features,
replication-aware changes, optimization passes).

## Ecosystem Permissions

Base + Universal Deny + Git or Perforce -- see
`Docs/Templates/References/ecosystem-permissions.md`. Engine-specific source
paths and asset denies are domain-unique, so add them here:

- **Allow (engine source)**: Unreal -> `write access(./Source/**)`,
  `write access(./Plugins/**/Source/**)`, `write access(./Config/**)`. Unity ->
  `write access(./Assets/**/*.cs)`, `write access(./Packages/**/*.cs)`,
  `write access(./ProjectSettings/**)`. Godot -> `write access(./**/*.{gd,tscn,tres})`,
  `write access(./project.godot)`.
- **Deny (binary assets, both Edit and Write)**: `**/*.{uasset,umap,prefab,asset,scene}`.
  Hard rule -- these are never text-editable.
- **Perforce** (variant): allow `p4 edit/add/reopen/revert/change/reconcile/opened/
  fstat/describe/changes/diff/sync/info/where *`; deny `p4 submit/obliterate/archive *`
  (never submit autonomously). Perforce projects cannot use worktrees.

`VCS ignore rules`: binary assets, media (png/jpg/tga/exr/psd/wav/mp3/ogg/mp4), build
output (Binaries/, Intermediate/, DerivedDataCache/, Library/, Temp/, obj/), and
Engine/ (too large to index). Generate `local config profile` for machine-specific
engine and build-tool paths; gitignore it.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Context exhaustion on large refactors -- implementer runs
  out of context touching many header/source pairs. Mitigation: max 3-4 pairs per
  checkpoint; use area maps to avoid re-scanning.
- [PATTERN] (pre-seeded) Build errors after correct-looking changes -- missing
  #include for new types, GENERATED_BODY() issues, forward decl insufficient for
  full type, reflection macro typos. Mitigation: implementer verifies includes
  before reporting done.
- [PATTERN] (pre-seeded) Gameplay vs replication bug routing ambiguity -- "X does
  not work in multiplayer" could be either. Mitigation: check single-player repro
  first; reproduces -> gameplay debugger; only in MP -> replication debugger.
- [PATTERN] (pre-seeded) Binary asset edits attempted -- implementer tries to edit
  .uasset/.umap when a Blueprint change is needed. Mitigation: PreToolUse hook
  blocks binary edits; write exact editor steps and stop.
- [PATTERN] (pre-seeded) Playtest steps too vague -- gate says "test the feature"
  with no specifics. Mitigation: every gate has numbered steps, expected result
  per step, and what to capture on failure.
```

## Hook Suggestions

Templates in `Docs/Templates/Optional/hooks-template.md`:

- **PreToolUse binary-asset block** (recommended, domain-unique) -- matcher
  `Write|Edit`; reject paths matching `\.(uasset|umap|prefab|asset|scene|fbx|png|
  jpg|wav|mp3|ogg|tga|exr|psd)$` with exit code 2 and "write editor steps instead".
- **PreCompact auto-save** (recommended) -- persist checkpoint, modified files,
  build status before compaction.
- **Stop hook self-review** (recommended) -- agent reviews modified source for
  missing UPROPERTY macros, replication bugs, GAS anti-patterns; exit 2 to
  self-correct. Keep a re-entry guard.
- **Status line** (recommended) -- `CODEX_STATUSLINE` for context health;
  document WSL requirement for Windows in GETTING_STARTED.
- **PostToolUse build reminder** (optional) -- nudge `/build` after edits.

## Cost / Model Notes

high-effort GPT-5.5 for planner/debugger/reviewer/researcher; medium-effort GPT-5.5 for implementer/explorer/
performance-analyst. Workflows are naturally serial (plan -> implement -> build ->
playtest) so subagents (~4x) are the default. Defaults: balanced (GPT-5.5 on
reasoning roles, compaction 95%, AGENTS.md ~200 lines). Cost-conscious override:
all medium-effort GPT-5.5 (GPT-5.5 only for orchestrator routing), consider folding
performance-analyst into debugger, compaction 85%, AGENTS.md ~150, aggressive
`VCS ignore rules`, full RTK in GETTING_STARTED (filters 1000+-line UBT output).
Engine builds are slow -- `/build` should track build times and suggest partial
builds. Area maps save tokens vs repeated full scans. Monitor with `/cost`.

## Customization Points

Engine choice (Unreal/Unity/Godot/custom -- drives build command, asset patterns,
permissions); VCS (Git vs Perforce variant); dual-wiki (`Design/` + `Dev/`) when
the project has both gameplay-design and code dimensions; `/map-codebase` adoption
for large engine codebases; cost tier (balanced vs cost-conscious); GAS/Enhanced
Input vs other Unreal subsystems.

## Special patterns

- **Manual playtest gate** (the key distinction from generic software-development
  work): game code is not validated by automated tests alone. After each compilable checkpoint,
  `/build`; on SUCCESS emit a pause message (what changed, files touched, numbered
  test steps, expected result per step, what to capture on failure) and STOP until
  the user reports PASS/FAIL/PARTIAL. The orchestrator never skips this gate.
  Enforced by the `testing-gates.md` rule.
- **Codebase mapping** (Pattern F): area maps (`Docs/Areas/`) + symbol pages
  (`Docs/Symbols/`) + `/map-codebase`; orchestrator preflight checks map freshness
  before debug/feature/refactor/perf tasks.

## Team-architecture pattern

Producer-Reviewer (implement -> review) inside a Pipeline (plan -> implement ->
build -> playtest). Subagents are the default. Consider Agent Teams only for
parallel exploration (independent debug hypotheses) or large multi-system features
with non-overlapping file ownership (gameplay / networking / ui). Prefer
`codex with worktrees` (~4x) over teams (~15x) for Git projects; Perforce cannot use
worktrees, and split-pane mode does not work on Windows (use in-process mode).
For large codebases set `CODEX_AUTOCOMPACT_PCT_OVERRIDE: "85"`.

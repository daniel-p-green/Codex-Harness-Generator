# Generation standards

Every generated environment must meet these standards. The component-generator
and environment-validator both enforce them.

## Required core components (every environment)

1. **CLAUDE.md** -- orchestrator contract, first-run onboarding, intent behind
   constraints, 2-3 behavior examples, compaction hints, verification commands
2. **Routing rule** (00-orchestrator.md) -- domain-specific entries, fallbacks,
   complexity scaling (simple/standard/complex)
2b. **Context discipline** in routing rule -- Read whitelist, delegation mandate,
   disk-based subagent handoff
3. **Autonomy rule** -- reversibility classification, anti-overengineering
4. **Context management rule** -- adaptive thresholds, compaction hints
5. **Self-learning rule** -- cold-start seed entries from starter profile
6. **Error handling rule** -- graceful degradation per failure mode
7. **/state-save skill** -- 6 categories (tool/task/artifact/decision/blocked/
   drift-risk), JSON output
8. **/state-load skill** -- session startup protocol, drift detection
9. **/update skill** -- analysis-only phase, implementation after approval
10. **/health-check skill** -- deterministic validation script
11. **Memory structure** -- tiered: Lite/Standard/Enterprise per intake
12. **settings.json** -- permissions, deny rules, Agent Teams env var. Generate
    `settings.local.json` when machine-specific paths exist (with a commented
    placeholder, never an empty allow array). `fastModePerSessionOptIn` (when
    cost-conscious) is a TOP-LEVEL boolean key (`true`), NOT a string under `env`.
12b. **PreCompact auto-save hook**
12c. **Stop hook self-review** (recommended for software/game dev)
12d. **Self-learning trigger hook** -- an InstructionsLoaded (preferred) or
    SessionStart hook that counts `Docs/_working/retro/` entries and recommends
    `/update` at threshold. REQUIRED whenever the self-learning rule (#5) is
    present, i.e. every environment -- the rule is logging-only without it.
    Template: Optional/hooks-template.md "InstructionsLoaded: Self-learning trigger".
13. **.claudeignore** -- appropriate patterns
13b. **.gitignore** (or `.p4ignore`) -- must exclude `Docs/_working/`; its own manifest row
14. **Docs/GETTING_STARTED.md** -- plain-language onboarding
15. **Docs/Environment/** metadata (VERSION.md, GENESIS.md, ARCHITECTURE.md)

## Conditional components (17-29)

Generated ONLY when intake justifies (full specs in
`generation-standards-reference.md`): state pruning (17), wiki watermark (18),
doc parsing (19), multi-model routing (20), semantic-search MCP (21),
session-segmented memory (22), multi-role (23), Beads (24), compliance hooks (25),
token optimization (26), plugins (27), skill eval (28), memory plugin (29).
(Item 16, the self-learning trigger, is a required core component -- see 12d.)

## Quality limits

| Component | Limit | Why |
|---|---|---|
| CLAUDE.md | < 250 lines | Loaded every conversation |
| Rule files | < 120 lines each, 5-8 total | Always-loaded; bloat degrades perf |
| Agent definitions | < 80 lines | Focused, not encyclopedic |
| SKILL.md files | < 500 lines (5,000 words) | Skills fork context |
| All files | ASCII-only | Cross-platform encoding safety |

## CLAUDE.md content rules

INCLUDE: commands Claude cannot guess, non-default style rules, test
instructions, architecture decisions, dev quirks, gotchas.
EXCLUDE: code-inferable info, standard conventions, detailed API docs, volatile info.

## Prompt engineering (Opus 4.8/4.7; 4.6 compatible)

No role-setting; state purpose once with intent (WHY). Prefer 2-3 few-shot examples
over long rule lists; add compaction hints. Write instructions LITERALLY (4.7/4.8 do
not generalize -- be explicit about scope; re-baseline 4.6 "double-check" scaffolding).
Never emit `temperature`/`top_p`/`top_k` (API 400); tune via `effort` (recommend
`xhigh` for coding/agentic). Full detail: Topics 13 + 14.

## Model selection

Opus 4.8 (`claude-opus-4-8`, Claude Code default) for orchestration, architecture,
generation, review, complex debugging; Sonnet 4.6 for implementation, validation,
exploration (~1.2% behind on coding at ~5x lower cost); Haiku for simple lookups.
Cross-model review (Opus + Sonnet) catches different blind spots. Pin model IDs for
third-party deploys (`ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU}_MODEL`). Detail: Topic 13.

## Agent generation rules

- maxTurns required in frontmatter (prevents runaway execution)
- Description states WHEN to delegate, not just WHAT
- disallowedTools lists bare tool NAMES only (e.g. `[Write, Edit]`). Path-scoped
  restrictions (e.g. protect `./Brand/**`) go in settings.json `permissions.deny`,
  NEVER in disallowedTools -- a glob there is unrecognized and fails open silently.
- "Never speculate about files you have not read" in all agent prompts
- Reference content at TOP, instructions at BOTTOM
- Investigate-before-answering pattern for diagnostic agents

## Skill generation rules

- Progressive disclosure: `SKILL.md` + `scripts/` + `references/`
- No README.md in skill folders (SKILL.md is the entry point)
- Descriptions: [What] + [When/3+ triggers] + [Negative triggers if ambiguous]
- Critical instructions at TOP with ## Critical or ## Important
- Side-effect skills: `disable-model-invocation: true` in hooks
- Each skill checks state independently; MCP tools use fully qualified names

## Multi-pass generation

| Pass | Components | Loads |
|---|---|---|
| 1 Foundation | CLAUDE.md, rules, settings, .claudeignore, hooks | ARCHITECTURE, GENESIS, templates |
| 2 Agents | All agent definitions | ARCHITECTURE (agent specs) |
| 3 Skills | All skill definitions | ARCHITECTURE (skill specs) |
| 4 Infrastructure | Wiki, working memory, self-learning | ARCHITECTURE (memory specs) |
| 5 Documentation | GETTING_STARTED, VERSION, cross-refs | All generated files |

Track progress in `<target>/Docs/Environment/GENERATION_PROGRESS.md`.

Hook portability: Bash hooks need a Unix shell (WSL/Git Bash on Windows); for
Windows-primary environments prefer PowerShell or `"type": "prompt"`/`"agent"` hooks.

## Anti-overengineering

Generate only what intake justifies (no VCS rules without VCS, no team coordination
for solo devs, Lite memory for simple projects). Fewer well-crafted files beat many.

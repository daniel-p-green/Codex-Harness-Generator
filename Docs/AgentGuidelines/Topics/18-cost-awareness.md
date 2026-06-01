# 18. Cost Model and Token Optimization

This topic covers cost economics (model tiers, architecture multipliers,
effort levels, budgeting, caching, fast mode) and token-reduction strategy
(third-party tools, built-in features, .claudeignore, startup budget,
subagent/MCP overhead, and efficiency tiers for generated environments).

## Table of contents

- 18.1 Token Economics (architecture cost multipliers)
- 18.2 Effort Levels
- 18.3 /cost Tracking
- 18.4 --max-budget-usd
- 18.5 Prompt Caching Configuration
- 18.6 Fast Mode
- 18.7 Third-Party Token Reduction Tools (RTK, Context Mode, Token Optimizer)
- 18.8 Built-in Optimization Features
- 18.9 .claudeignore as Highest-ROI Optimization
- 18.10 CLAUDE.md Startup Token Budget
- 18.11 Subagent and MCP Overhead
- 18.12 Efficiency Tiers for Generated Environments

## 18.1 Token Economics (architecture cost multipliers) [ALL]

- **Established**: 2025-09; updated 2026-04-20 for Opus 4.7
- **Source**: multi-agent-research-system.md, agent-teams.md,
  platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | Tier 1
- **Recommendation**: Understand cost multipliers for architecture decisions:

  | Architecture | Cost Multiplier | When Justified |
  |-------------|----------------|----------------|
  | Single chat | 1x | Simple tasks, conversations |
  | Single subagent | ~4x | Focused investigation, isolated context |
  | Multi-subagent (3-5) | ~12-20x | Complex research, multi-area exploration |
  | Agent Team (3 teammates) | ~45x | Parallel non-overlapping implementation |
  | Agent Team (5 teammates) | ~75x | Large cross-layer features |

  Token usage explains 80% of performance variance. More tokens generally mean better
  results, but with diminishing returns. Budget accordingly.

  Opus 4.7 tokenizer change [4.7+]: Expect 1.0x-1.35x more tokens for the same text
  compared to 4.6 (up to ~35% more, varies by content type). Re-estimate budgets for
  pipelines migrating from 4.6 to 4.7. Pricing per token is unchanged ($5/M input,
  $25/M output). Opus 4.8 shares the 4.7 tokenizer, so the same headroom applies.

  4.7 default behavior reduces some subagent costs [4.7+]: fewer tool calls and fewer
  subagents spawned by default. Multi-subagent multipliers above are upper bounds on 4.7;
  in practice you may see 0.7-0.9x of the listed figure unless you explicitly prompt for
  more parallelism.
- **Anti-pattern**:
  - Choosing architecture without considering cost.
  - Migrating a pipeline from 4.6 to 4.7 without re-estimating token budgets.
  - Assuming `temperature=0` saves tokens on 4.7 -- sampling params are removed there.

## 18.2 Effort Levels [ALL] (UPDATED for Opus 4.7)

- **Established**: 2025-09; updated 2026-04-20 for Opus 4.7
- **Source**: platform.claude.com/docs/en/build-with-claude/effort,
  code.claude.com/docs/en/changelog | Tier 1
- **Recommendation**: Configure effort levels per task type. See topic 13.5 for full 4.7
  effort guidance. Summary:
  - `low`: Simple fixes, documentation, boilerplate, bounded subagents. Fast, minimal thinking.
  - `medium`: Standard development, cost-sensitive workflows.
  - `high` (API default): Complex reasoning, architecture, security review.
  - `xhigh` [4.7+] (Claude Code default on 4.7): RECOMMENDED starting point for coding
    and agentic work. Expect meaningfully higher token usage than `high`.
  - `max` (4.6, 4.7, Mythos): Reserve for frontier problems. Can cause overthinking.

  Set via:
  - API: `output_config.effort` (preferred, GA on Opus 4.7/4.6, Sonnet 4.6, Opus 4.5)
  - Claude Code session: `/effort` command with interactive slider (v2.1.111)
  - Frontmatter: `effort:` field on agents, skills, slash commands (v2.1.76-v2.1.84)
  - Env: `CLAUDE_CODE_EFFORT_LEVEL`
  - Settings: `effortLevel`
  - Default effort for API-key / Bedrock / Vertex / Foundry / Team / Enterprise users
    changed from `medium` to `high` in v2.1.94.

  Claude Code note: Auto mode (v2.1.111) is available for Max subscribers on Opus 4.7 --
  Claude selects effort per turn.
- **Anti-pattern**:
  - Always using `high` or `max`. Slower and more expensive for tasks that don't benefit
    from deep reasoning.
  - Setting `effort` below `high` on complex 4.7 coding tasks and then prompting around
    the shallow output. Raise effort instead.
  - Forgetting to raise `max_tokens` at `xhigh`/`max` -- 4.7 docs recommend starting at
    64k for agentic runs.

## 18.3 /cost Tracking [ALL]

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: Use `/cost` in interactive sessions to track token usage and API costs.
  Include cost awareness in generated environments:
  - Mention `/cost` in GETTING_STARTED.md
  - Include cost notes in team coordination rules
  - Document cost implications of multi-agent operations

  For headless/automated use, `--output-format json` includes cost data in output metadata.
- **Anti-pattern**: Running expensive multi-agent operations without monitoring costs. Users
  can incur significant API charges without realizing it.

## 18.4 --max-budget-usd [ALL]

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: Use `--max-budget-usd` in headless/print mode to set a hard cost cap:
  `claude -p "prompt" --max-budget-usd 5.00`. This prevents runaway costs in automated
  pipelines.

  Combine with `--max-turns` for additional control: `claude -p "prompt" --max-turns 10
  --max-budget-usd 2.00`.

  Include budget guidance in generated environments that use headless mode for automation.
- **Anti-pattern**: Automated pipelines without budget limits. A misbehaving agent in an
  infinite loop can consume large amounts of API credit.

## 18.5 Prompt Caching Configuration [ALL] (UPDATED April 2026)

- **Established**: 2026-03; updated 2026-04-20
- **Source**: code.claude.com/docs/en/changelog v2.1.86, v2.1.108 | Tier 1
- **Recommendation**: Claude Code uses prompt caching by default. As of v2.1.86, global
  system-prompt caching is enabled when ToolSearch is active, broadening cache hit rates.

  Current (2026-04) status:
  - `ENABLE_PROMPT_CACHING_1H` -- enable 1-hour cache TTL (universal env var)
  - `ENABLE_PROMPT_CACHING_1H_BEDROCK` -- DEPRECATED, use universal form
  - `DISABLE_PROMPT_CACHING*` env vars -- WARNED at startup (v2.1.108). Subscribers fall
    back to 5-minute TTL. Prefer leaving caching enabled.

  Generally leave caching enabled. Disable selectively only when debugging model behavior.

  Cache warmth matters: avoid unnecessary CLAUDE.md/settings churn mid-session -- each
  change invalidates the cache prefix.
- **Anti-pattern**: Continuing to set `DISABLE_PROMPT_CACHING_BEDROCK=1` or other cloud-
  specific disables -- warned at startup and removed in a future release.

## 18.6 Fast Mode [ALL]

- **Established**: 2026-03; updated 2026-05-31 for Opus 4.8
- **Source**: claude-code-docs.md, anthropic.com/news/claude-opus-4-8 | Tier 1
- **Recommendation**: Fast mode uses the current Opus model with faster output
  (approximately 2.5x speed) at a higher per-token cost. Available on Opus 4.6, 4.7, and
  4.8. Toggle interactively with `/fast` or set `"fastMode": true` in settings.json.

  On Opus 4.8, fast mode is ~3x cheaper than it was for previous models ($10/M input,
  $50/M output vs the same standard $5/$25), which materially changes the cost trade-off:
  fast mode is now a more defensible default for speed-sensitive interactive sessions on
  4.8 than it was on 4.7. The `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE` env var is
  deprecated (removed 2026-06-01) -- do not generate it.

  Best practices:
  - Enable at session start, not mid-conversation. Switching mid-session causes
    reprocessing of the existing context at fast-mode pricing.
  - Use `"fastModePerSessionOptIn": true` in settings.json to require per-session
    opt-in. This prevents persistent fast mode from causing unexpected cost increases.
  - Fast mode is most cost-effective for short, focused sessions where speed matters
    more than token cost (quick fixes, exploration, debugging).

  For generated environments:
  - Cost-conscious tier: document as optional in GETTING_STARTED.md, never auto-enable,
    always include `fastModePerSessionOptIn: true`
  - Balanced tier: mention availability in GETTING_STARTED.md with cost trade-off note
  - Quality-first tier: can auto-enable if user prefers speed

- **Anti-pattern**: Leaving `fastMode: true` in shared settings.json without
  `fastModePerSessionOptIn: true`. This silently increases costs for all team members.

## 18.7 Third-Party Token Reduction Tools [ALL]

- **Established**: 2026-03
- **Source**: RTK GitHub, MCP Context Mode, Token Optimizer MCP | Tier 2
- **Recommendation**: Three third-party tools provide significant token reduction:

  1. **RTK (Rust Token Killer)**: CLI proxy that intercepts shell commands via
     PreToolUse hooks and filters/compresses output before it reaches context.
     60-90% reduction on CLI output. Highest ROI for code-producing environments.
     Install: `brew install rtk && rtk init --global`. Integrates via settings.json
     PreToolUse hooks that rewrite commands transparently.
  2. **MCP Context Mode**: Sandboxes tool outputs so only stdout enters conversation
     context; everything else stored in SQLite with full-text search. 98% reduction
     per tool interaction. Best for heavy MCP/tool usage environments.
  3. **Token Optimizer MCP**: MCP server using Brotli compression + persistent SQLite
     caching. 95%+ reduction. Alternative to Context Mode.

  RTK is the highest-ROI recommendation for most environments because it targets
  the most common token waste (verbose CLI output) with minimal setup.

- **Anti-pattern**: Installing all three tools simultaneously. Each addresses
  overlapping concerns. Recommend one primary tool (RTK for most; Context Mode for
  MCP-heavy workflows) and mention others as alternatives.

## 18.8 Built-in Optimization Features [ALL]

- **Established**: 2026-03
- **Source**: claude-code-docs.md, Anthropic blog | Tier 1
- **Recommendation**: Claude Code includes several built-in optimization features:

  1. **MCP Tool Search (lazy loading)**: Loads MCP tool definitions on-demand instead
     of upfront. Activates automatically when tools exceed 10% of context. Reduces
     MCP overhead from ~77k to ~8.7k tokens (85% reduction for 50+ tools).
  2. **Auto-compaction**: Triggers at ~95% context capacity (configurable via
     `CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE` in settings.json env block). Lower
     values (85%) trade session length for more frequent state preservation.
  3. **`/cost` command**: Per-session token breakdown for monitoring (see 18.3).
  4. **`/compact` with focus**: Custom compaction prompts preserve specific context.

  Cross-reference: topic 5 (Memory, Context, and State) for compaction strategy;
  sections 18.1-18.2 for model selection economics and effort budgeting.

- **Anti-pattern**: Setting compaction below 85%. This cuts sessions too short and
  forces frequent state-save/load cycles that themselves consume tokens.

## 18.9 .claudeignore as Highest-ROI Optimization [ALL]

- **Established**: 2026-03
- **Source**: Claude Code docs, community benchmarks | Tier 1
- **Recommendation**: A well-configured .claudeignore provides the highest ROI
  optimization with zero ongoing cost:

  - Excluding `node_modules` alone saves 30k-100k tokens on Node.js projects
  - Well-configured patterns yield ~25% token reduction on file reading operations
  - Combined with other optimizations: 55% consumption reduction, 60% faster responses

  Domain-specific patterns matter more than generic ones:
  - Software: `dist/`, `build/`, `node_modules/`, `coverage/`, lock files
  - Game dev: `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `Content/`,
    `Engine/` (UE5); `Library/`, `Temp/`, `Obj/` (Unity)
  - Data: `*.csv` (large data files), `*.parquet`, `data/raw/`
  - DevOps: `*.tfstate`, `.terraform/`, cloud provider caches

  Cross-reference: topic 1.2 (CLAUDE.md) for startup token budget.

- **Anti-pattern**: Overly aggressive patterns that exclude files Claude needs to
  read (source code, config files, test files). Always verify patterns do not
  exclude generated environment files.

## 18.10 CLAUDE.md Startup Token Budget [ALL]

- **Established**: 2026-03
- **Source**: Community benchmarks, CLAUDE.md token analysis | Tier 2
- **Recommendation**: Every line of CLAUDE.md costs tokens every session. A 2,100-token
  CLAUDE.md consumes 2,100 tokens before conversation starts.

  Targets by efficiency tier:
  - Cost-conscious: 150 lines (~600 tokens)
  - Balanced: 200 lines (~800 tokens)
  - Quality-first: 250 lines (~1,000 tokens, the existing hard max)

  Use subdirectory CLAUDE.md files for specialized rules that only load when
  those files are touched. Rule: if it is not needed for every single interaction,
  it does not belong in the root CLAUDE.md.

  Note [4.7+]: token estimates above are 4.6-era. Under the 4.7/4.8 tokenizer the same
  text costs up to ~1.35x more (see 18.1); allow that headroom when sizing CLAUDE.md and
  any `max_tokens` budgets.

  Cross-reference: topic 1 (Rules) for CLAUDE.md content guidelines.

- **Anti-pattern**: Putting detailed API docs, code examples, or frequently-changing
  information in CLAUDE.md. Link to reference files instead.

## 18.11 Subagent and MCP Overhead [ALL]

- **Established**: 2026-03
- **Source**: Anthropic multi-agent research, community reports | Tier 1
- **Recommendation**: Each subagent spawns a full context window with ~20k tokens
  overhead before work begins. Five MCP servers add ~55k tokens before conversation
  starts (e.g., Jira alone uses ~17k tokens).

  Cost-conscious environments should:
  - Prefer CLI tools (gh, aws, gcloud, kubectl) over MCP servers when available
  - Consolidate agents where roles overlap (e.g., merge explorer into debugger)
  - Reserve subagent delegation for high-volume operations (tests, docs, logs)
  - Estimate 20k minimum overhead per subagent invocation
  - Enable MCP Tool Search (see topic 10 section 10.11, and section 18.8) for environments with 3+
    MCP servers to defer tool definition loading and reduce upfront context overhead

  Cross-reference: section 18.1 for subagent/team cost multipliers.

- **Anti-pattern**: Using subagents for simple tasks that could be answered directly.
  A 3-tool-call direct answer costs ~2k tokens; delegating the same work to a
  subagent costs ~25k tokens.

## 18.12 Efficiency Tiers for Generated Environments [ALL]

- **Established**: 2026-03
- **Source**: Token optimization research synthesis | Tier 2
- **Recommendation**: Generated environments should be calibrated to one of three
  efficiency tiers based on intake:

  | Setting | Cost-Conscious | Balanced | Quality-First |
  |---------|---------------|----------|---------------|
  | Default model | Sonnet for all agents | Sonnet impl, Opus plan/review | Opus available for all |
  | Compaction threshold | 85% | 95% (default) | 95% (default) |
  | .claudeignore | Aggressive (domain + generic) | Standard (domain-specific) | Minimal (only binaries) |
  | CLAUDE.md target | 150 lines | 200 lines | 250 lines |
  | RTK recommendation | Install instructions in GETTING_STARTED.md | Mentioned as option | Not mentioned |
  | Agent consolidation | Merge where roles overlap | Standard roster | Full roster |
  | Subagent delegation | Only for high-volume ops | Standard routing | Generous delegation |

  Default tier is "balanced" if the user expresses no preference. The tier
  influences architecture decisions (model selection, agent count), generation
  (settings.json env block, .claudeignore patterns, CLAUDE.md length), and
  documentation (GETTING_STARTED.md cost monitoring section).

  The fast-mode tier guidance in 18.6 maps onto these same three tiers.

- **Anti-pattern**: Applying cost-conscious settings to quality-first users (degrades
  experience) or quality-first settings to budget-constrained users (causes bill shock).

---

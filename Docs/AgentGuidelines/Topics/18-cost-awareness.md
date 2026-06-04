# 18. Cost Model and Token Optimization

This topic covers GPT-5.5/Codex cost controls: reasoning effort, service tier,
prompt size, subagent overhead, MCP loading, VCS ignore rules, and generated
environment efficiency tiers.

## Table of contents

- 18.1 Token Economics
- 18.2 Reasoning Effort
- 18.3 Session Cost Tracking
- 18.4 Headless Budget Caps
- 18.5 Prompt Caching and Context Churn
- 18.6 Service Tier Selection
- 18.7 Third-Party Token Reduction Tools
- 18.8 Built-in Optimization Features
- 18.9 VCS Ignore Rules as Highest-ROI Optimization
- 18.10 AGENTS.md Startup Token Budget
- 18.11 Subagent and MCP Overhead
- 18.12 Efficiency Tiers for Generated Environments

## 18.1 Token Economics [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/api/docs/guides/reasoning,
  https://developers.openai.com/codex/subagents | Tier 1
- **Recommendation**: Treat architecture as the primary cost lever.

  | Architecture | Cost Profile | When Justified |
  |-------------|--------------|----------------|
  | Direct answer | Lowest | Simple questions, small edits, bounded checks |
  | Single subagent | Higher | Isolated investigation or review with separate context |
  | Multiple subagents | Much higher | Parallel work on clearly independent areas |
  | Agent team | Highest | Large projects with real parallel implementation value |

  Reasoning effort and subagent count compound. Use subagents when isolation,
  parallelism, or specialized review changes the outcome; keep direct work direct.

- **Anti-pattern**: Delegating a small lookup to a subagent because a role exists.
  A focused direct command is usually cheaper, faster, and easier to verify.

## 18.2 Reasoning Effort [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/api/docs/guides/reasoning,
  https://developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**: Configure effort with Codex `model_reasoning_effort` and,
  for API examples, Responses API `reasoning.effort`.

  Current Codex config values are `minimal`, `low`, `medium`, `high`, and
  model-dependent `xhigh`. GPT-5.5 defaults to `medium` reasoning effort in the
  official reasoning guide, which is a good balanced default.

  | Effort | Use for |
  |--------|---------|
  | `low` | simple edits, formatting, short docs, mechanical checks |
  | `medium` | normal development, validation, cost-sensitive work |
  | `high` | architecture, debugging, security review, complex synthesis |
  | `xhigh` | only when the selected model supports it and quality warrants the cost |

  Generated environments should pin `model = "gpt-5.5"` and choose
  `model_reasoning_effort` per agent role rather than using prompt wording as a
  substitute for effort configuration.

- **Anti-pattern**: Adding "think harder" language everywhere. Raise effort for
  the role or task that needs it and keep instructions concise.

## 18.3 Session Cost Tracking [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex | Tier 1
- **Recommendation**: Include lightweight cost awareness in generated
  environments:
  - Mention the Codex cost/status command when the target workflow is long-running.
  - Document cost implications of multi-agent operations.
  - Prefer small validation loops before broad scans or multi-agent review.

  For headless automation, prefer structured command output and explicit stop
  conditions so cost and progress can be audited.

- **Anti-pattern**: Running open-ended automated loops without progress checks,
  stop criteria, or budget guidance.

## 18.4 Headless Budget Caps [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex | Tier 1
- **Recommendation**: When generated environments include headless or scheduled
  Codex runs, document the budget controls supported by the deployed Codex
  surface and pair them with turn limits, narrow scopes, and artifact outputs.

  If a specific CLI flag is unavailable in the installed Codex version, fall back
  to shorter task prompts, smaller file scopes, and explicit "stop and report"
  gates.

- **Anti-pattern**: Treating budget flags as the only safeguard. They are a last
  line of defense, not a substitute for bounded work.

## 18.5 Prompt Caching and Context Churn [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/concepts/customization | Tier 1
- **Recommendation**: Keep stable instructions stable. Prompt caching is most
  useful when AGENTS.md, rules, and high-level context do not churn every turn.

  Generated environments should:
  - Keep root AGENTS.md concise.
  - Move domain detail into docs or subdirectory AGENTS.md files.
  - Avoid rewriting large instruction files during normal operation.
  - Store volatile working notes under `Docs/_working/`, not in startup context.

- **Anti-pattern**: Putting every checklist, example, and research note into the
  root instructions file.

## 18.6 Service Tier Selection [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**: Use Codex `service_tier` only when the environment has a
  clear latency or cost requirement and the user's account supports the tier.
  The config reference lists built-in values such as `flex` and `fast`.

  Generated shared configs should not silently force a premium or latency-focused
  tier. Prefer documenting the tradeoff in GETTING_STARTED.md and letting the user
  choose for the session.

- **Anti-pattern**: Emitting unofficial config keys for speed modes. If the key is
  not in the current Codex config reference, do not generate it.

## 18.7 Third-Party Token Reduction Tools [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: Community tool documentation | Tier 2
- **Recommendation**: Third-party output filters and context compressors can be
  useful for noisy shell output or MCP-heavy environments, but they should be
  optional and domain-justified.

  Generated environments should recommend at most one primary token-reduction
  tool, explain the workflow it improves, and avoid installing extra dependencies
  by default.

- **Anti-pattern**: Adding multiple overlapping token tools before measuring the
  actual source of context growth.

## 18.8 Built-in Optimization Features [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/concepts/customization,
  https://developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**: Prefer built-in Codex controls before extra infrastructure:
  - Subdirectory AGENTS.md files for scoped instructions.
  - Skills for progressively disclosed procedures.
  - MCP/tool search where available for large tool surfaces.
  - Compaction and state-save hooks for long sessions.
  - Direct shell searches before broad model reads.

- **Anti-pattern**: Solving context pressure by adding another always-loaded
  agent, MCP server, or reference file.

## 18.9 VCS Ignore Rules as Highest-ROI Optimization [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: Codex customization guidance and repository practice | Tier 1
- **Recommendation**: Well-scoped ignore rules reduce accidental context load with
  no runtime dependency:
  - Software: `dist/`, `build/`, `node_modules/`, `coverage/`
  - Game dev: engine caches, generated binaries, derived data
  - Data: large raw exports, intermediate parquet/csv files
  - DevOps: state files, cloud cache directories, generated plans

  Ignore generated or bulky artifacts, but do not hide source code, tests,
  schemas, or generated harness files that Codex must inspect.

- **Anti-pattern**: Using broad ignore patterns that make verification impossible.

## 18.10 AGENTS.md Startup Token Budget [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/guides/agents-md | Tier 1
- **Recommendation**: Every root instruction line loads into many sessions.
  Keep root AGENTS.md small and move specialized guidance closer to the files it
  governs.

  Targets by efficiency tier:
  - Cost-conscious: about 150 lines
  - Balanced: about 200 lines
  - Quality-first: about 250 lines

  Use subdirectory AGENTS.md files for specialized rules that should load only
  when Codex works in that area.

- **Anti-pattern**: Putting detailed API docs, long examples, or frequently
  changing status notes in root AGENTS.md.

## 18.11 Subagent and MCP Overhead [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/subagents,
  https://developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**: Each subagent and MCP server adds planning and context
  overhead. Cost-conscious environments should:
  - Prefer CLI tools over MCP servers when CLI output is enough.
  - Consolidate agents where roles overlap.
  - Reserve delegation for work that benefits from isolated context.
  - Use explicit agent descriptions so routing is selective.
  - Lazy-load large procedural guidance through skills.

- **Anti-pattern**: Creating one agent per noun in the domain. Agent boundaries
  should reflect materially different work.

## 18.12 Efficiency Tiers for Generated Environments [ALL]

- **Established**: 2026-06-03 Codex port
- **Source**: Harness generator policy grounded in official Codex controls | Tier 2
- **Recommendation**: Calibrate generated environments to one of three tiers:

  | Setting | Cost-Conscious | Balanced | Quality-First |
  |---------|---------------|----------|---------------|
  | Default effort | `medium` | `medium`, with selected `high` agents | `high` for complex roles |
  | Agent roster | Consolidated | Standard | Full, when justified |
  | VCS ignore rules | Aggressive but verified | Domain-specific | Minimal but safe |
  | AGENTS.md target | ~150 lines | ~200 lines | ~250 lines |
  | Third-party token tools | Optional, documented | Mention only if relevant | Usually omit |
  | Subagent delegation | Rare and explicit | Standard routing | Generous but bounded |

  Default to balanced when the user gives no cost preference. Document deviations
  in `Docs/Environment/ARCHITECTURE.md`.

- **Anti-pattern**: Applying quality-first defaults to budget-sensitive users, or
  cost-conscious defaults to users who value reliability over speed.

---

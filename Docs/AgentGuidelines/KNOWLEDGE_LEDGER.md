# Knowledge Ledger

Audit trail of all research and reference material processed by the Harness Generator.
Maintained by the knowledge-base maintenance workflow. Do not edit manually.

Last cleaned: 2026-03-04
Last /update pass: 2026-05-31 (GPT-5.5 release; Codex v2.1.118-v2.1.158)
Last consolidation: 2026-05-31 (26 -> 18 topics)

## Topic Consolidation Map (2026-05-31)

Seven overlapping topic groups were merged into their lowest-numbered survivor
(all guidance preserved). "BP Sections" numbers below that reference a folded-in
topic should be read via this map:

- 06 (context mgmt), 09 (state mgmt) -> 05 (Memory, Context & State)
- 14 (prompt engineering) -> 13 (GPT-5.5 Model & Prompt Eng)
- 17 (MCP) -> 10 (Integration & MCP)
- 19 (parallel execution) -> 04 (Teams, Parallelism & Patterns)
- 22 (document integration) -> 21 (RAG & Documents)
- 24 (self-validation) -> 15 (Testing, Validation & QA)
- 25 (token optimization) -> 18 (Cost & Tokens)

Surviving topics: 00, 01, 02, 03, 04, 05, 07, 08, 10, 11, 12, 13, 15, 16, 18,
20, 21, 23.

## Active Sources

Sources whose content lives in topic files (Docs/AgentGuidelines/Topics/). Listed here for
traceability after the original file is removed.

| Date Added | Source | Type | Summary | Model Scope | BP Sections | Removed |
|---|---|---|---|---|---|---|
| 2026-02-14 | developers.openai.com/codex | Web/Tier 1 | Complete Codex documentation: settings schema, 14 hook events, skill/agent frontmatter specs, memory hierarchy, permission syntax, environment variables | All Codex | 1-20 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (context engineering) | Web/Tier 1 | Context engineering strategies: smallest set of high-signal tokens, progressive disclosure, structured notes, sub-agent architectures for context rot | All Codex | 6, 5, 14 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (agent skills) | Web/Tier 1 | Skill authoring: 3-level progressive disclosure, trigger phrase requirements, SKILL.md under 500 lines, scripts for deterministic ops | All Codex | 3 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (multi-agent research) | Web/Tier 1 | Multi-agent architecture: GPT-5.5 lead + medium-effort GPT-5.5 workers, 90% improvement over single agent, token usage explains 80% of performance, artifact-first handoff | GPT-5.5 4.5+, medium-effort GPT-5.5 4.5+ | 2, 4, 19 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (agent teams) | Web/Tier 1 | Agent Teams: peer-to-peer messaging, shared task lists, parallel exploration, significant token cost (~15x), default to subagents for serial work | All Codex | 4, 18, 19 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (sandboxing) | Web/Tier 1 | Dual-isolation sandboxing: filesystem + network, 84% reduction in permission prompts, /sandbox command, open-source sandbox-runtime | All Codex | 11 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (platform agent patterns) | Web/Tier 1 | Platform-level patterns: GPT-5.5 overuse of subagents, skip role-setting, adaptive thinking with effort levels | GPT-5.5, GPT-5.5 at lower reasoning effort | 13, 2, 8 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (long-running harnesses) | Web/Tier 1 | Two-part harness: Initializer + Coding Agent, JSON for agent-managed state (less corruption), progress file + git commits for cross-session memory | All Codex | 9, 6 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (common workflows) | Web/Tier 1 | Workflow recipes: explore-plan-implement-commit, Plan Mode for exploration, subagents for isolated investigation, /compact for context management | All Codex | 8, 6, 10 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex/subagents (parallel Codex agents) | Web/Tier 1 | Parallel autonomous agents: file-based task locking, tests as primary QC, design output for agents, agent specialization | All Codex | 19, 15 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (prompt engineering) | Web/Tier 1 | Prompt engineering: few-shot over edge-case lists, XML tags for structure, long docs at top, guided CoT with structured output, temperature 0.1 for agentic | All Codex | 14 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (best practices) | Web/Tier 1 | Best practices: give Codex verification (#1 priority), AGENTS.md must be concise, /clear after 2 failed corrections, subagents for investigation | All Codex | 1, 10, 15 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/api/docs/guides/reasoning | Web/Tier 1 | GPT-5.5 guide: state instructions once, skip role-setting, front-load context, explicit check-in points, adaptive reasoning replaces thinking budgets | GPT-5.5 | 13 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (testing) | Web/Tier 1 | Testing methodology: code-based > LLM-based > human grading, include edge cases always, prioritize volume, use different model for grading | All Codex | 15 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (cookbooks agents) | Web/Tier 1 | Agent patterns: 6 patterns (chain, route, parallel, orchestrator-workers, evaluator-optimizer, autonomous), XML canonical for structured output | All Codex | 8, 14, 2 | 2026-03-04 |
| 2026-02-14 | developers.openai.com/codex (guardrails) | Web/Tier 1 | Safety guardrails: 7-level hallucination reduction, autonomy vs safety balance, degrees of freedom matching, investigate-before-answering | All Codex | 15, 11 | 2026-03-04 |
| 2026-03-04 | Web research + ProjectLeyline analysis | Internal/Tier 2 | RAG strategies, document integration, multi-modal workflows, self-validation loops, production environment analysis of 15 issues | GPT-5.5, GPT-5.5 at lower reasoning effort | 21-24 | 2026-03-04 |
| 2026-04-20 | developers.openai.com/api/docs/guides/reasoning | Web/Tier 1 | GPT-5.5 launch: xhigh effort tier, task budgets beta, high-res images (2576px), new tokenizer (+35% tokens), sampling params removed, budget_tokens removed, adaptive-thinking-only, thinking content omitted by default, fewer subagents/tool calls, literal instruction following, 1M context at standard pricing, cyber safeguards | GPT-5.5 | 13, 14, 18, 02 | live |
| 2026-04-20 | developers.openai.com/codex (Q1-Q2 2026) | Web/Tier 1 | Codex v2.1.73-v2.1.113: new hook events (CwdChanged, FileChanged, TaskCreated, PostCompact, Elicitation, PermissionDenied, StopFailure), new frontmatter (effort, initialPrompt, context: fork/agent, model), new slash commands (/effort, /ultrareview, /powerup, /team-onboarding, /focus, /recap, /less-permission-prompts), permission hardening, MCP elicitation/OAuth/result-size, plugin monitors/userConfig/bin, default effort to high, deprecated DISABLE_PROMPT_CACHING* | All Codex | 16, 03, 02, 11, 17, 20, 18 | live |
| 2026-06-03 | https://developers.openai.com/api/docs/guides/reasoning | Web/Tier 1 | GPT-5.5 reasoning guide: use Responses API `reasoning.effort`, model-dependent effort values, GPT-5.5 default `medium`, tune quality/cost with effort rather than sampling knobs | GPT-5.5 | 13, 18, 02 | live |
| 2026-06-03 | https://developers.openai.com/codex/config-reference | Web/Tier 1 | Codex config reference: TOML config, `model_reasoning_effort`, `service_tier`, permissions profiles, and the rule not to combine `default_permissions` with top-level sandbox settings | All Codex | 10, 11, 18 | live |
| 2026-06-03 | https://developers.openai.com/codex/subagents | Web/Tier 1 | Codex subagents: `.codex/agents/*.toml`, explicit name/description/developer instructions, scoped sandboxing, and role-specific effort settings | All Codex | 02, 04, 08 | live |
| 2026-05-31 | developers.openai.com/codex (v2.1.118-v2.1.158) | Web/Tier 1 | Codex May 2026: GPT-5.5 default model, MessageDisplay hook, PostToolUse updatedToolOutput/continueOnBlock/duration_ms, terminalSequence/sessionTitle/reloadSkills hook outputs, $CODEX_MODEL_REASONING_EFFORT, skill distool access policy + /reload-skills + skillOverrides, plugins auto-load from .agents/skills + plugin init + defaultEnabled, /simplify renamed to /code-review, agent view + dynamic workflows + background sessions, PowerShell -ExecutionPolicy Bypass default | All Codex | 16, 03, 20, 19, 18 | live |

## Removed (Outdated)

Sources removed because their content was outdated or superseded.

| Date Added | Source | Type | Summary | Model Scope | Removed | Reason |
|---|---|---|---|---|---|---|
| (none yet) |

## Archive (Historical)

Development artifacts kept for historical reference only.
Not incorporated into topic files.

| Date | Source | Type | Summary | Removed |
|---|---|---|---|---|
| 2026-02-16 | Internal planning | Archive | PLAN_DRAFT.md -- Initial Creator design draft | 2026-03-04 |
| 2026-02-16 | Internal planning | Archive | PLAN_V2.md -- Second iteration of Creator design | 2026-03-04 |
| 2026-02-16 | Internal planning | Archive | PLAN_V3_FINAL.md -- Third iteration (marked final) | 2026-03-04 |
| 2026-02-16 | Internal planning | Archive | PLAN_V4_UNIFIED.md -- Fourth iteration (unified) | 2026-03-04 |
| 2026-02-16 | Internal planning | Archive | PLAN_AMENDMENTS.md -- Amendments to planning docs | 2026-03-04 |
| 2026-02-16 | Internal planning | Archive | RESEARCH_SYNTHESIS.md -- Synthesis of initial research | 2026-03-04 |
| 2026-02-16 | Internal planning | Archive | SKILLS_GUIDE_TAKEAWAYS.md -- Key takeaways from skills guide | 2026-03-04 |
| 2026-02-16 | Internal planning | Archive | legacy-skills-guide.pdf -- Original skills guide PDF | 2026-03-04 |
| 2026-02-16 | Internal planning | Archive | skills-guide-text.txt -- Extracted text from skills guide | 2026-03-04 |

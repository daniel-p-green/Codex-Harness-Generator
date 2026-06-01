# 13. Opus Model Specifics and Prompt Engineering

**Last Updated**: 2026-05-31 (Opus 4.8 release: 2026-05-28)

Opus 4.8 (`claude-opus-4-8`) is the current flagship, released 2026-05-28.
It is the default model in Claude Code as of v2.1.154. Opus 4.7 remains
supported. Almost all 4.7 guidance below applies unchanged to 4.8 (same
pricing, same removed sampling parameters, same effort model, same tokenizer);
section 13.0 captures the 4.8-specific deltas. Where 4.6 guidance is retained,
it is marked as such.

This topic is the single model-and-prompting reference. Sections 13.0-13.17
cover model-version specifics and deltas (4.8 / 4.7 / 4.6). Sections 13.18-13.22
cover prompt-engineering technique, with each point marked [ALL], [4.7+], or
[4.6 ONLY] so you can tell durable guidance from legacy scaffolding.

## Table of Contents

**Model specifics**
- 13.0 Opus 4.8 Deltas (NEW)
- 13.1 Skip Role-Setting
- 13.2 State Once (No Reminders)
- 13.3 Literal Instruction Following (NEW in 4.7)
- 13.4 Anti-Overengineering
- 13.5 Adaptive Thinking and Effort Levels (UPDATED for 4.7)
- 13.6 Task Budgets (NEW in 4.7, beta)
- 13.7 Removed Sampling Parameters (BREAKING in 4.7)
- 13.8 Thinking Content Omitted by Default (BREAKING in 4.7)
- 13.9 Updated Tokenizer (BREAKING in 4.7)
- 13.10 1M Context Window (Retained, now standard pricing)
- 13.11 Tone and Response Length (CHANGED in 4.7)
- 13.12 Fewer Subagents by Default (CHANGED in 4.7)
- 13.13 High-Resolution Vision (NEW in 4.7)
- 13.14 Memory Tool Improvements (ENHANCED in 4.7)
- 13.15 Real-Time Cybersecurity Safeguards (NEW in 4.7)
- 13.16 Parallel Tool Calling (Retained)
- 13.17 Sensitivity to "Think" Variants (Retained)

**Prompt engineering**
- 13.18 XML Tags Are Canonical [ALL]
- 13.19 Few-Shot Examples [ALL]
- 13.20 Long Documents at Top [ALL]
- 13.21 Temperature / Sampling Parameters [4.6 ONLY]
- 13.22 Structured Chain-of-Thought [ALL]

---

## 13.0 Opus 4.8 Deltas (NEW) [4.7+]

- **Established**: 2026-05-28 (Opus 4.8 release)
- **Source**: anthropic.com/news/claude-opus-4-8, code.claude.com/docs/en/changelog
  (v2.1.154) | Tier 1
- **Model ID**: `claude-opus-4-8`. Default Claude Code model as of v2.1.154.
  Pin via `ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-8` for Bedrock/Vertex/
  Foundry to avoid silent upgrades.
- **Pricing**: Unchanged from 4.7 ($5/M input, $25/M output standard). Fast
  mode is now 3x cheaper than previous models' fast mode and runs at ~2.5x
  speed ($10/M input, $50/M output).
- **Effort levels (renamed surface, same Claude Code mapping)**: 4.8 defaults
  to **Standard (high)** effort, considered the best quality/UX balance. The
  ladder is Standard (default) -> Extra (`xhigh` in Claude Code) -> Max.
  Claude Code still defaults to `xhigh` for agentic/coding work; keep
  recommending `xhigh` in generated GETTING_STARTED.md. No change to the
  no-`temperature`/`top_p`/`top_k` rule (13.7) or adaptive-thinking-only rule
  (13.5) -- both carry over to 4.8 unchanged.
- **Fewer code flaws slip through**: 4.8 is ~4x less likely than 4.7 to let a
  coding flaw pass unflagged. Self-review scaffolding (Stop-hook review,
  "double-check" prompts) is even less necessary than on 4.7 -- prefer letting
  the model self-flag and reserve hooks for deterministic gates.
- **Mid-task system entries (NEW API capability)**: the Messages API now
  accepts `system`-role entries inside the `messages` array, letting you inject
  instructions mid-conversation without breaking the prompt cache or routing
  through a user turn. Relevant for long agentic loops and orchestrators that
  need to update guidance without a cache-busting system-prompt edit.
- **Dynamic workflows (Claude Code, research preview)**: 4.8 + Claude Code can
  plan work and run tens-to-hundreds of parallel background subagents in one
  session with output verification. Enterprise/Team/Max plans only; see topic
  19 (parallel execution). The word "workflow" in a prompt can trigger this;
  generated environments that use "workflow" as domain vocabulary should note
  the `Workflow keyword trigger` setting (16/settings) to suppress it.
- **Anti-pattern**: Treating 4.8 as a breaking change from 4.7. It is not --
  no config that worked on 4.7 breaks on 4.8. The only required change for
  pinned third-party deployments is bumping the model ID.

## 13.1 Skip Role-Setting [ALL]

- **Established**: 2025-09 (Opus 4.6 release), retained for 4.7
- **Source**: opus-4-6-guide.md, anthropic.com/news/claude-opus-4-7 | Tier 1
- **Recommendation**: Do NOT use "Act as an expert" or "You are a senior engineer" prompts.
  State purpose and constraints directly:
  - Bad: "You are an expert Python developer. Act as a senior engineer..."
  - Good: "You help maintain a FastAPI application. Always run pytest after changes."

  This applies to generated CLAUDE.md files, agent definitions, and skill instructions.
- **Anti-pattern**: Role-setting in prompts. It wastes tokens without improving behavior.
  Claude infers expertise from context.

## 13.2 State Once (No Reminders) [ALL]

- **Established**: 2025-09, retained for 4.7
- **Source**: opus-4-6-guide.md, platform.claude.com/docs prompting-best-practices | Tier 1
- **Recommendation**: Claude maintains instruction consistency across extended conversations.
  State each instruction ONCE. Do not repeat rules mid-conversation. Trust that instructions
  persist.

## 13.3 Literal Instruction Following (NEW in 4.7) [4.7+]

- **Established**: 2026-04-16 (Opus 4.7 release)
- **Source**: platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7,
  claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code | Tier 1
- **Recommendation**: Opus 4.7 interprets instructions more literally than 4.6, especially at
  lower effort levels. The model will NOT silently generalize an instruction from one item to
  another, and will NOT infer requests you didn't make.

  Prompt implications:
  - Be explicit about scope. If you want behavior applied "to all X", say so; 4.7 won't
    extrapolate from a single example.
  - Detailed plans win. Structured requests ("generate three options, rank by X, explain in
    one sentence each") produce much better output than vague asks.
  - Re-baseline existing prompts. Scaffolding added to compensate for 4.6 behavior (e.g.,
    "double-check the slide layout before returning", "make sure you consider edge cases") is
    often unnecessary on 4.7 and may degrade results. Try removing it and compare.
- **Anti-pattern**: Assuming 4.7 will fill in context like 4.6 did. Vague prompts that
  "worked well enough" on 4.6 now under-deliver.

## 13.4 Anti-Overengineering [ALL]

- **Established**: 2025-09 (still applies but softened in 4.7)
- **Source**: opus-4-6-guide.md, platform.claude.com | Tier 1
- **Recommendation**: 4.7 is less prone to overengineering than 4.6 out of the box (response
  length calibrates to task complexity; fewer tool calls by default; fewer subagents spawned).
  The anti-overengineering block in generated CLAUDE.md is still recommended but can be
  shorter:
  ```
  Avoid over-engineering. Only make changes directly requested or clearly necessary.
  Do not add features, docstrings, error handling, or abstractions beyond what was asked.
  ```
- **Anti-pattern**: Omitting this guidance entirely. Even 4.7 will occasionally overbuild on
  open-ended asks; the explicit instruction provides a clean signal.

## 13.5 Adaptive Thinking and Effort Levels (UPDATED for 4.7) [4.7+]

- **Established**: 2026-04-16 (4.7 changes)
- **Source**: platform.claude.com/docs/en/build-with-claude/adaptive-thinking,
  platform.claude.com/docs/en/build-with-claude/effort | Tier 1
- **Recommendation**: On 4.7, adaptive thinking is the ONLY thinking-on mode. Manual
  `budget_tokens` is removed (returns 400 on API). Adaptive thinking is off by default; set
  `thinking: {type: "adaptive"}` to enable.

  Effort levels for 4.7 (new `xhigh` tier):

  | Level | Use Case |
  |-------|----------|
  | low | Short, scoped tasks; pair with explicit checklists for multi-part work |
  | medium | Drop-in for average workflow; good results at reduced cost |
  | high | Sweet spot for intelligence-sensitive work (API default) |
  | xhigh | RECOMMENDED STARTING POINT for coding and agentic work |
  | max | Reserve for frontier problems; often overthinks structured-output tasks |

  Claude Code note: Claude Code defaults to `xhigh` for Opus 4.7 on all plans. Auto mode is
  now available for Max subscribers.

  Strict effort enforcement: 4.7 respects effort levels more strictly than 4.6 at low/medium.
  If you see shallow reasoning on complex problems, raise effort -- don't prompt around it.
- **Anti-pattern**:
  - Setting `thinking: {type: "enabled", budget_tokens: N}` on 4.7 (API 400 error)
  - Leaving `effort` unset on API calls when you need coding or agentic depth (defaults to
    `high`, but `xhigh` is the recommended starting point for those workloads)
  - Using `MAX_THINKING_TOKENS` env var to tune 4.7 (ignored)

## 13.6 Task Budgets (NEW in 4.7, beta) [4.7+]

- **Established**: 2026-04-16 (beta header `task-budgets-2026-03-13`)
- **Source**: platform.claude.com/docs/en/build-with-claude/task-budgets | Tier 1
- **Recommendation**: Task budgets are an advisory signal across a full agentic loop. The
  model sees a running countdown and prioritizes to finish within budget. Minimum 20k tokens.
  Distinct from `max_tokens` (hard per-request cap that the model does not see).

  Use task budgets when you want the model to self-moderate (e.g., long agentic explorations
  where you care about cost). Skip them for open-ended quality-first work.
- **Anti-pattern**: Using a restrictive task budget for complex tasks -- the model may finish
  prematurely or refuse. Also: confusing `task_budget` with `max_tokens`.

## 13.7 Removed Sampling Parameters (BREAKING in 4.7) [4.7+]

- **Established**: 2026-04-16
- **Source**: platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | Tier 1
- **Recommendation**: `temperature`, `top_p`, and `top_k` are REMOVED on 4.7 (and 4.8).
  Setting any of them to a non-default value returns 400. Omit them entirely; guide behavior
  through prompting and effort levels.

  Impact on temperature guidance (13.21, "Temperature 0.1 for Agentic Work"): that guidance
  applied to 4.6 and earlier and to Sonnet 4.6. For 4.7/4.8, do NOT set temperature. Use
  `effort: "low"` for consistent/fast agentic subagents instead.
- **Anti-pattern**: Carrying over `temperature=0.1` defaults from 4.6 cookbooks to 4.7/4.8
  requests. Returns 400.

## 13.8 Thinking Content Omitted by Default (BREAKING in 4.7) [4.7+]

- **Established**: 2026-04-16
- **Source**: platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | Tier 1
- **Recommendation**: On 4.7, thinking content is omitted from responses by default. Thinking
  blocks still appear in the stream but `thinking` field is empty. To restore visible
  progress (important for streamed UIs), set:
  ```python
  thinking = {"type": "adaptive", "display": "summarized"}
  ```
  Options: `"omitted"` (default), `"summarized"`.
- **Anti-pattern**: User-facing streaming products leaving display at default -- users see a
  long pause before output starts.

## 13.9 Updated Tokenizer (BREAKING in 4.7) [4.7+]

- **Established**: 2026-04-16
- **Source**: platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | Tier 1
- **Recommendation**: 4.7 uses a new tokenizer (shared by 4.8). Text may use 1.0x-1.35x more
  tokens than on 4.6 (up to ~35% more, varies by content). `/v1/messages/count_tokens` returns
  different counts. Implications:
  - Raise `max_tokens` to give headroom (especially for compaction triggers)
  - Budget CLAUDE.md and rule files with the new tokenizer in mind (still stay under limits
    in topic 01; the ratio is similar enough that current 250/120-line limits hold)
  - Cost estimates based on 4.6 token counts under-predict 4.7 costs by up to 35%
- **Anti-pattern**: Copying `max_tokens` values from 4.6 configs without headroom. Requests
  can truncate output.

## 13.10 1M Context Window (Retained, now standard pricing) [4.7+]

- **Established**: GA on 4.7 at standard API pricing with NO long-context premium
- **Source**: platform.claude.com/docs/en/build-with-claude/context-windows | Tier 1
- **Recommendation**: 1M context is available on 4.7 without the long-context surcharge that
  previously applied above 200k. Max output tokens: 128k.

## 13.11 Tone and Response Length (CHANGED in 4.7) [4.7+]

- **Established**: 2026-04-16
- **Source**: platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | Tier 1
- **Recommendation**: 4.7 is more direct and opinionated, with less validation-forward
  phrasing and fewer emoji than 4.6's warmer style. Response length calibrates to task
  complexity rather than defaulting to fixed verbosity. Agents produce more regular progress
  updates during long traces.

  Prompt implications:
  - Scaffolding like "be concise" is less necessary on 4.7
  - Scaffolding forcing "send interim status messages" is less necessary; 4.7 does this
    naturally
  - If you PREFER warmer tone for user-facing assistants, add explicit tone guidance to
    CLAUDE.md
- **Anti-pattern**: Keeping verbose tone-control scaffolding from 4.6 prompts. Often
  counterproductive on 4.7.

## 13.12 Fewer Subagents by Default (CHANGED in 4.7) [4.7+]

- **Established**: 2026-04-16
- **Source**: platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | Tier 1
- **Recommendation**: 4.7 spawns fewer subagents and makes fewer tool calls by default,
  using reasoning more. Steerable through prompting: if you want more parallelism or more
  aggressive delegation, state it explicitly in CLAUDE.md or the relevant agent prompt.

  Impact on Generator-generated environments: the default orchestrator pattern still holds,
  but generated CLAUDE.md may want to add a line encouraging delegation when the project
  warrants it ("Prefer delegating multi-file searches to a subagent").

## 13.13 High-Resolution Vision (NEW in 4.7) [4.7+]

- **Established**: 2026-04-16
- **Source**: platform.claude.com/docs/en/build-with-claude/vision | Tier 1
- **Recommendation**: 4.7 supports 2576px / 3.75MP images (up from 1568px / 1.15MP). Model
  coordinates are 1:1 with pixels (no scale-factor math). Relevant for computer-use agents,
  screenshot analysis, and multi-modal workflows (see topic 23).

  Cost note: high-res images use more tokens. Downsample before sending when fidelity isn't
  required.

## 13.14 Memory Tool Improvements (ENHANCED in 4.7) [4.7+]

- **Established**: 2026-04-16
- **Source**: platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool | Tier 1
- **Recommendation**: 4.7 is better at writing and using file-system-based memory
  (scratchpads, notes, structured memory stores). Impact on generated environments:
  - Working-memory patterns (Docs/_working/) benefit more on 4.7
  - Agents that maintain notes across turns should improve without prompt changes
  - Consider enabling the managed memory tool for projects with long-horizon tasks

## 13.15 Real-Time Cybersecurity Safeguards (NEW in 4.7) [4.7+]

- **Established**: 2026-04-16
- **Source**: platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | Tier 1
- **Recommendation**: 4.7 includes real-time safeguards that may refuse requests involving
  prohibited or high-risk cybersecurity topics. For legitimate security research, apply to
  the Cyber Verification Program. Relevant for security/DevOps profile users; mention in
  GENESIS.md if the project involves offensive security work.

## 13.16 Parallel Tool Calling (Retained) [ALL]

- **Established**: 2025-09, retained for 4.7
- **Source**: platform-agent-patterns.md | Tier 1
- **Recommendation**: Opus handles parallel tool calling well natively. For explicit
  encouragement:
  ```xml
  <use_parallel_tool_calls>
  For maximum efficiency, whenever you perform multiple independent operations,
  invoke all relevant tools simultaneously rather than sequentially.
  </use_parallel_tool_calls>
  ```
- **Anti-pattern**: Over-prompting. Even with 4.7's "fewer tool calls by default" behavior,
  it still parallelizes well when appropriate.

## 13.17 Sensitivity to "Think" Variants (Retained) [ALL]

- **Established**: 2025-09, retained for 4.7
- **Source**: platform-agent-patterns.md | Tier 1
- **Recommendation**: When thinking is off, words like "think hard" are interpreted as
  regular prompt instructions, NOT as thinking-token allocators. Use "consider", "evaluate",
  "analyze", "assess" instead. Thinking depth is controlled via effort level or adaptive
  thinking configuration.

---

# Prompt Engineering

The following sections cover prompt-engineering technique that applies across
the Harness Generator's generated CLAUDE.md, agent, and skill files. Most of this is
model-agnostic [ALL]; the temperature guidance (13.21) is [4.6 ONLY] legacy --
see 13.7 for the current rule.

## 13.18 XML Tags Are Canonical [ALL]

- **Established**: Baseline
- **Source**: prompt-engineering.md, claude-cookbooks-agents.md | Tier 1
- **Recommendation**: Use XML tags for all structured content in prompts and expected outputs:
  - Routing: `<reasoning>`, `<selection>`
  - Evaluation: `<evaluation>PASS|NEEDS_IMPROVEMENT|FAIL</evaluation>`, `<feedback>`
  - Analysis: `<analysis>`, `<tasks><task><type>`, `<description>`
  - Thinking: `<thinking>`, `<answer>` or `<response>`

  Be consistent with tag names throughout prompts. Refer to tag names explicitly when
  instructing: "Using the contract in <contract> tags, analyze..."

  No canonical "best" tag names exist -- use names that match the content semantics.
- **Anti-pattern**: Inconsistent tag names, mixing XML with JSON for structured output, or
  not referring to tags when instructing Claude about them.

## 13.19 Few-Shot Examples [ALL]

- **Established**: Baseline
- **Source**: prompt-engineering.md, context-engineering.md | Tier 1
- **Recommendation**: Include 3-5 diverse, relevant examples instead of exhaustive rule
  lists. Examples are "the pictures worth a thousand words" for LLMs. Requirements:
  - Relevant: mirror actual use case
  - Diverse: cover edge cases, vary enough to avoid unintended pattern pickup
  - Clear: wrapped in `<example>` tags (nested in `<examples>` if multiple)

  Generated CLAUDE.md files should include 2-3 canonical behavior examples showing expected
  agent behavior for the domain.
- **Anti-pattern**: "Stuffing a laundry list of edge cases" instead of providing diverse
  canonical examples. Edge case lists create fragility; examples generalize better.

## 13.20 Long Documents at Top [ALL]

- **Established**: Baseline
- **Source**: prompt-engineering.md | Tier 1
- **Recommendation**: Put longform data (20K+ tokens) at the TOP of the prompt, above
  query/instructions. Put the query at the END. This improves response quality by up to 30%.

  For agent prompts with reference material: put the reference content at the top,
  instructions at the bottom. This is counterintuitive but validated by Anthropic testing.
  (This is the same "reference content at TOP, instructions at BOTTOM" rule the agent
  generation standards enforce.)

  Structure multiple documents with XML tags:
  ```xml
  <documents>
    <document index="1">
      <source>filename.pdf</source>
      <document_content>{{CONTENT}}</document_content>
    </document>
  </documents>
  ```
- **Anti-pattern**: Putting instructions first and reference material last. The model performs
  better when it has processed the reference material before encountering the instructions.

## 13.21 Temperature / Sampling Parameters [4.6 ONLY]

- **Established**: Baseline (4.6 and earlier); SUPERSEDED for Opus 4.7+
- **Updated**: 2026-04-20
- **Source**: claude-cookbooks-agents.md (legacy),
  platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7 | Tier 1
- **Recommendation**:
  - **Opus 4.7 / 4.8 [4.7+]**: Do NOT set `temperature`, `top_p`, or `top_k`. Non-default
    values return 400. Omit these parameters entirely. Use `effort: "low"` for fast,
    scope-bounded agentic subagents; `high`/`xhigh` when quality matters. See sections 13.5
    and 13.7 (the authoritative copy of the removed-parameter rule).
  - **Opus 4.6, Sonnet 4.6, earlier models [4.6 ONLY]**: The legacy guidance still applies.
    Use `temperature=0.1` for deterministic agentic work (routing, code gen, structured
    output). Higher temperatures only for creative tasks.
- **Anti-pattern**:
  - Setting `temperature` on 4.7/4.8 requests (400 error)
  - Using default `1.0` temperature for agentic work on pre-4.7 models
  - Assuming `temperature=0` guarantees identical outputs -- it never did

## 13.22 Structured Chain-of-Thought [ALL]

- **Established**: Baseline
- **Source**: prompt-engineering.md | Tier 1
- **Recommendation**: Use structured CoT with XML tags to separate reasoning from output:
  ```
  Think before you answer in <thinking> tags. First, consider what approach
  would be most effective. Then, analyze the specific requirements. Finally,
  provide your answer in <answer> tags.
  ```

  Three complexity levels:
  - Basic: "Think step-by-step" (least guided)
  - Guided: Outline specific thinking steps (moderate)
  - Structured: XML tags separating reasoning from answer (best quality)

  Critical: Always have Claude OUTPUT its thinking. Without outputting the thought process,
  no thinking occurs.

  Note for 4.7+: structured CoT (asking the model to write reasoning into `<thinking>` tags)
  is a prompt-level technique and is distinct from the adaptive-thinking API mode (13.5). On
  4.7/4.8 the words "think hard" do not allocate thinking tokens (13.17); control depth via
  effort or adaptive thinking, and use structured CoT tags when you want the reasoning surfaced
  in the visible response.
- **Anti-pattern**: Using CoT for simple tasks where it adds latency without improving
  quality. Also: telling Claude to think without providing a place to output its thinking.

---

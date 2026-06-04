# Codex Port Evaluation

This document defines the minimum passing contract for the Codex Harness Generator
port. A generated harness is considered Codex-ready only when it is structurally
aligned with current OpenAI Codex customization primitives and no longer depends
on the pre-port legacy runtime.

## Official Source Baseline

The port is grounded in these OpenAI sources:

- https://developers.openai.com/codex/concepts/customization
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/config-reference
- https://developers.openai.com/codex/subagents
- https://developers.openai.com/api/docs/guides/reasoning

## Required Runtime Surface

- Root project instructions live in `AGENTS.md`.
- Project-level configuration lives in `.codex/config.toml`.
- Custom Codex subagents live in `.codex/agents/*.toml`.
- Custom skills live in `.agents/skills/*/SKILL.md`.
- Generated docs and templates refer to OpenAI, Codex, GPT-5.5 (`gpt-5.5`),
  `model_reasoning_effort`, MCP, subagents, skills, and AGENTS.md using Codex
  terminology.

## Red/Green Cases

`scripts/eval_codex_port.py` enforces these cases. `tests/test_eval_codex_port.py`
builds temporary green and red repositories to prove the evaluator fails for the
intended reasons.

- **Red: legacy runtime names remain.** Any generated-facing Markdown, TOML,
  YAML, JSON, or text artifact that still mentions pre-port runtime names,
  legacy model-family names, legacy config names, or legacy agent/skill schema
  fields fails.
- **Red: required Codex runtime files missing.** The port fails if `AGENTS.md`,
  `.codex/config.toml`, the five generator subagent TOML files, the four core
  skills, or the renamed Codex templates are absent.
- **Red: legacy runtime files remain.** The port fails if any pre-port runtime
  path or old template filename still exists.
- **Red: source grounding missing.** The port fails if the repo does not cite
  the official OpenAI docs listed above.
- **Red: malformed Codex TOML.** The port fails if `.codex/config.toml`, any
  `.codex/agents/*.toml` file, or generated agent-template TOML block does not
  parse.
- **Red: inactive permission profile.** The port fails if `default_permissions`
  is missing, nested under another TOML table, points at a missing profile, or is
  combined with top-level `sandbox_mode`.
- **Green: Codex contract present.** The port passes only when the required
  runtime files, required concepts, and official source citations are all
  present while the forbidden legacy surface is absent.

Current red fixtures cover:

- legacy root instruction file still present;
- legacy tool-name prose still present;
- missing required Codex path;
- top-level permission-profile conflict;
- nested `default_permissions`;
- missing custom-agent schema fields;
- invalid embedded custom-agent TOML;
- missing official source citations.

## Manual Review Gates

Passing the script is necessary, not sufficient. Before release, manually inspect:

- `README.md` and `Docs/USER_GUIDE.md` for accurate first-run instructions.
- `AGENTS.md` for concise project instructions without stale platform terms.
- `.codex/config.toml` for valid TOML and intended model/permission settings.
- `.codex/agents/*.toml` for valid Codex subagent schemas.
- `.agents/skills/*/SKILL.md` for Codex skill frontmatter and triggering text.
- `Docs/Templates/Core/*` and `Docs/Templates/References/*` for generated-output
  consistency.

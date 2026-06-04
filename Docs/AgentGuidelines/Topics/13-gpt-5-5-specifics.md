# 13. GPT-5.5 and Codex Prompting

**Last Updated**: 2026-06-03

This topic is the model and prompting reference for Codex-generated harnesses.
It is grounded in the OpenAI Codex customization, config, subagent, AGENTS.md,
and reasoning-model docs.

## 13.1 Model Baseline

- **Source**: https://developers.openai.com/api/docs/guides/reasoning,
  https://developers.openai.com/codex/config-reference
- **Recommendation**: Use `gpt-5.5` as the default model for generated Codex
  harnesses unless the user explicitly asks for a different OpenAI model.
- **Generated config**: Set `model = "gpt-5.5"` and
  `model_reasoning_effort = "medium"` in `.codex/config.toml`.
- **Subagents**: Use `model = "gpt-5.5"` in `.codex/agents/*.toml`; vary
  `model_reasoning_effort` by task complexity instead of inventing model-family
  aliases.
- **Anti-pattern**: Mixing provider-specific model nicknames into generated
  Codex files. Generated harnesses should use OpenAI model IDs and Codex config
  keys.

## 13.2 Reasoning Effort

- **Source**: https://developers.openai.com/api/docs/guides/reasoning,
  https://developers.openai.com/codex/subagents
- **Recommendation**: Tune depth with `model_reasoning_effort`.

| Effort | Use |
|---|---|
| `low` | Fast lookup, file mapping, simple classification |
| `medium` | Default project work, implementation from clear plans, validation checklists |
| `high` | Architecture, debugging, review, high-stakes analysis |
| `xhigh` | Hard multi-step reasoning, ambiguous migrations, cross-system design |

- Keep the project default at `medium` unless the harness is explicitly
  quality-first or high-stakes.
- Raise effort for specific subagents instead of raising every run globally.
- Document why any `xhigh` default is justified.

## 13.3 Prompt Shape

- **Source**: https://developers.openai.com/codex/guides/agents-md,
  https://developers.openai.com/codex/concepts/customization
- **Recommendation**: Generated instructions should be short, literal, and
  verifiable.

Use this shape:

1. Purpose: what the assistant or subagent is for.
2. Scope: what it may and may not touch.
3. Decision rules: how to choose between common paths.
4. Verification: how success is checked.
5. Output: what artifact or response format to produce.

Avoid:

- Role-setting filler such as "act as an expert."
- Repeating the same rule in several files.
- Broad "always" language when a narrower trigger is enough.
- Long policy text in `AGENTS.md` that belongs in rules, skills, or references.

## 13.4 Codex Config Examples

For the project config:

```toml
model = "gpt-5.5"
model_reasoning_effort = "medium"
approval_policy = "on-request"
default_permissions = "project-default"
```

For a read-only custom subagent:

```toml
name = "explorer"
description = "Read-only codebase mapper for locating files, symbols, and ownership before edits."
model = "gpt-5.5"
model_reasoning_effort = "low"
sandbox_mode = "read-only"
developer_instructions = """
Map the relevant files and cite paths.
Do not edit files.
Return concise findings with evidence.
"""
```

For a complex reviewer:

```toml
name = "reviewer"
description = "Reviews changes for correctness, regressions, missing tests, and security risk."
model = "gpt-5.5"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Lead with findings.
Prioritize behavior, security, and test gaps over style.
Ground every issue in files, commands, or reproducible evidence.
"""
```

## 13.5 API And Generated-Code Compatibility

- **Source**: https://developers.openai.com/api/docs/guides/reasoning
- **Recommendation**: In generated OpenAI API examples, prefer the Responses API
  and its reasoning controls for reasoning models.
- Do not put API sampling parameters into Codex config files.
- Do not hardcode unsupported third-party model aliases or provider-specific
  environment variables.
- If a generated harness includes application-code examples, label them as API
  examples and keep them separate from Codex CLI/app config.

## 13.6 Evaluation Hooks

Generated harnesses should include tests or evals for model-sensitive behavior:

- Skill trigger near-misses: the right skill activates, adjacent skills stay idle.
- Subagent routing: simple tasks stay in the main session; complex or isolated
  work delegates.
- Verification discipline: implementation agents run or report the relevant
  checks before saying done.
- Safety boundaries: read-only agents do not write; write-capable agents stay
  inside the requested scope.

## 13.7 Upgrade Rules

When upgrading an older harness:

- Replace legacy model-family labels with OpenAI model IDs and reasoning effort.
- Replace Markdown/YAML agent definitions with `.codex/agents/*.toml`.
- Replace old config-file assumptions with `.codex/config.toml`.
- Re-run `scripts/eval_codex_port.py` after every migration pass.
- Manually inspect generated examples; mechanical replacement is not enough.

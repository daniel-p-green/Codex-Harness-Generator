# Semantic Alignment

Generated: 2026-06-04T04:50:59Z
Status: PASS

This live maintainer check compares core Codex concepts in local guidance
against the official OpenAI documentation pages this generator relies on.
It is a drift signal, not a substitute for human source review.

| Concept | Status | Source | Missing official terms | Missing local terms |
|---|---|---|---|---|
| AGENTS.md instruction loading | PASS | https://developers.openai.com/codex/guides/agents-md |  |  |
| Config permission schema | PASS | https://developers.openai.com/codex/permissions |  |  |
| Subagent schema | PASS | https://developers.openai.com/codex/subagents |  |  |
| Skill schema | PASS | https://developers.openai.com/codex/skills |  |  |
| Config model controls | PASS | https://developers.openai.com/codex/config-reference |  |  |

## Scope

- Checks only official `developers.openai.com` pages.
- Checks a small set of concepts the generator depends on: AGENTS.md,
  config permissions, subagents, skills, and model/control settings.
- A pass means the named concepts still appear in both official docs and
  local guidance; it does not prove exact semantic equivalence.

# Source Freshness

Generated: 2026-06-04T10:47:09Z
Status: PASS

This report verifies that official OpenAI documentation URLs cited by
the generator are currently reachable. It does not prove the local
guidance semantically matches every current doc detail.

| Source | Status | HTTP | Final URL |
|---|---|---:|---|
| https://developers.openai.com/codex/concepts/customization | PASS | 200 | https://developers.openai.com/codex/concepts/customization |
| https://developers.openai.com/codex/guides/agents-md | PASS | 200 | https://developers.openai.com/codex/guides/agents-md |
| https://developers.openai.com/codex/config-reference | PASS | 200 | https://developers.openai.com/codex/config-reference |
| https://developers.openai.com/codex/subagents | PASS | 200 | https://developers.openai.com/codex/subagents |
| https://developers.openai.com/codex/permissions | PASS | 200 | https://developers.openai.com/codex/permissions |
| https://developers.openai.com/codex/skills | PASS | 200 | https://developers.openai.com/codex/skills |
| https://developers.openai.com/api/docs/guides/reasoning | PASS | 200 | https://developers.openai.com/api/docs/guides/reasoning |

## Scope

- Checks only official `developers.openai.com` sources.
- Treat failures as a docs-drift investigation trigger, not automatic
  evidence that local guidance is wrong.
- Pair with semantic review before changing generator behavior.

---
name: health-check
description: Use when the user says "check this harness", "verify setup", "run health check", "/health-check", or before sharing the synthetic documentation workspace as a public example. Do not use as a content review for a specific memo; use reviewer for that.
---

## Critical

Health-check validates structure and references. It does not prove every future task will be correct.

## Checks

1. Confirm `AGENTS.md`, `.codex/config.toml`, `.codex/rules/`, `.codex/agents/`, `.agents/skills/`, and `Docs/index.md` exist.
2. Parse TOML files in `.codex/config.toml` and `.codex/agents/*.toml`.
3. Confirm every configured agent file exists.
4. Confirm every configured skill path contains `SKILL.md`.
5. Confirm `Docs/_working/` is ignored by `.gitignore`.
6. Scan for obvious unsafe example content: secrets, credentials, private keys, or real-looking private data.
7. Confirm `Docs/Environment/MANIFEST.md` entries resolve.

## Output

Return PASS, WARN, or FAIL with file paths and the smallest suggested fix.

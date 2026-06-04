# Appendix: Quick Reference Tables

## File Size Limits

| Component | Target | Hard Max |
|-----------|--------|----------|
| AGENTS.md | 150-200 lines | 250 lines |
| Individual rule file | <120 lines | 120 lines |
| Total rule files | 5-8 files | - |
| Agent definition | <80 lines | 80 lines |
| SKILL.md | <500 lines | 5,000 words |
| Skill description | <1024 chars | 1024 chars |

## Settings File Precedence (highest to lowest)

1. Managed settings (system-level)
2. CLI arguments
3. `.codex/local config profile` (local project, not shared)
4. `.codex/config.toml` (shared project)
5. `~/.codex/config.toml` (user global)

## Memory Hierarchy (precedence, highest first)

1. Managed policy AGENTS.md
2. Project AGENTS.md / .codex/AGENTS.md
3. Project rules (.codex/rules/*.md)
4. User memory (~/.codex/AGENTS.md)
5. Project local memory (AGENTS.override.md)
6. Auto memory (~/.codex/projects/<project>/memory/)

## Hook Timeouts

| Handler Type | Default Timeout |
|-------------|----------------|
| command | 600 seconds |
| prompt | 30 seconds |
| agent | 60 seconds |

---

*Last Updated: 2026-03-05*
*Sources: 16 Tier 1 (OpenAI official) research documents, 2 Tier 2 production environments (production game project, production compliance project), Mar 2026 web research (plugins, model config, checkpoints, RAG strategies, multi-modal workflows, document parsing, self-validation patterns)*

# Template: .codex/config.toml

<!-- TEMPLATE ANNOTATION
  This template defines generated `.codex/config.toml` files for Codex.

  QUALITY CRITERIA:
  - Valid TOML, parseable with `tomllib`.
  - Official Codex schema reference included.
  - `model = "gpt-5.5"` and `model_reasoning_effort` are explicit.
  - Permission profiles use the Codex TOML shape from the config reference.
  - `default_permissions` is not combined with top-level `sandbox_mode`.
  - Sensitive files and destructive operations are guarded by config and
    AGENTS.md instructions.
  - Network allowlists are domain-specific and minimal.

  WHY THIS EXISTS:
  `.codex/config.toml` controls the shared runtime defaults for generated Codex
  environments. Bad config either blocks ordinary work or silently widens the
  safety boundary. The generator must emit a small, valid base config first and
  add domain-specific surface area only when the intake justifies it.

  Sources:
  - https://developers.openai.com/codex/config-reference
  - https://developers.openai.com/codex/concepts/customization
-->

## Base configuration

Generate this base for every environment, adapting the permission profile name
and network domains to the target project.

```toml
#:schema https://developers.openai.com/codex/config-schema.json

model = "gpt-5.5"
model_reasoning_effort = "medium"
model_verbosity = "medium"
approval_policy = "on-request"
default_permissions = "generated-environment"

[features]
multi_agent = true
memories = true
apps = true

[permissions.generated-environment]
description = "Workspace write access for the generated Codex environment, with sensitive paths and network access constrained."
extends = ":workspace"

[permissions.generated-environment.filesystem]
glob_scan_max_depth = 4

[permissions.generated-environment.filesystem.":workspace_roots"]
"." = "write"
"**/.env" = "deny"
"**/.env.*" = "deny"
"**/secrets/**" = "deny"
"**/*secret*" = "deny"
"**/*token*" = "deny"
"**/*credential*" = "deny"
"**/*.pem" = "deny"
"**/*.key" = "deny"

[permissions.generated-environment.network]
enabled = true
mode = "limited"

[permissions.generated-environment.network.domains]
"developers.openai.com" = "allow"
"docs.github.com" = "allow"
```

## Model and effort policy

Use one model family across the generated runtime unless the user explicitly asks
for a different OpenAI model.

```toml
model = "gpt-5.5"
model_reasoning_effort = "medium"
model_verbosity = "medium"
```

Effort guidelines:
- `medium`: default for balanced environments, validation, bounded generation.
- `high`: architecture, review, security analysis, difficult debugging.
- `low`: small documentation or lookup-focused agents when speed matters.
- `xhigh`: only if the current model and account support it and the task warrants
  the cost.

Do not add sampling parameters such as `temperature`, `top_p`, or `top_k` to
generated Codex config. Use reasoning effort instead.

## Permission profile rules

Use named permission profiles for shared project policy. Do not combine
`default_permissions` with top-level `sandbox_mode`; the config reference treats
those as separate patterns.

Recommended profile structure:

```toml
default_permissions = "project-default"

[permissions.project-default]
description = "Shared project permissions."
extends = ":workspace"

[permissions.project-default.filesystem.":workspace_roots"]
"." = "write"
"**/.env" = "deny"
"**/.env.*" = "deny"
"**/secrets/**" = "deny"

[permissions.project-default.network]
enabled = true
mode = "limited"

[permissions.project-default.network.domains]
"developers.openai.com" = "allow"
```

Filesystem guidance:
- Default to workspace write for normal generated environments.
- Deny secrets, local credentials, private keys, and raw production exports.
- For conservative domains, narrow write access to `Docs/**`, `_workspace/**`,
  `.codex/**`, and `AGENTS.md`.
- Do not hide files that validation must inspect.

Network guidance:
- Keep `mode = "limited"` unless the user explicitly needs broader network.
- Add official documentation, package registries, or service APIs only when the
  intake identifies them.
- Never hardcode tokens, database URLs, or account-specific secrets in config.

## Shell and command policy

Codex command approval is controlled by `approval_policy`, sandboxing, and the
available tool surface. Keep generated command guidance in AGENTS.md and
GETTING_STARTED.md:
- list the project's build, test, lint, and format commands;
- identify commands that are safe to run for verification;
- require explicit user approval for destructive operations such as force-pushes,
  database mutations, credential rotation, disk formatting, or package publishing.

Do not emit unsupported command allow/deny arrays. If a command policy is not in
the current Codex config reference, express it as instruction and validation
guidance instead of inventing TOML keys.

## Environment variables

Use `[env]` sparingly for stable Codex or tool settings that should apply to every
session.

```toml
[env]
CODEX_AUTOCOMPACT_PCT_OVERRIDE = "85"
ENABLE_TOOL_SEARCH = "auto:5"
```

Guidance:
- Omit autocompact overrides for most projects.
- Use earlier compaction only for very large repositories or long-running sessions.
- Use Tool Search settings only when the environment has enough MCP/tool surface
  to benefit.

## Service tier

The Codex config reference supports `service_tier` values such as `flex` and
`fast`. Do not force a premium or latency-focused tier in shared config without an
explicit user preference.

```toml
# service_tier = "flex"
```

Document the tradeoff in GETTING_STARTED.md when relevant and let users opt in.

## Subagent registry

Register generated Codex subagents with TOML files under `.codex/agents/`.

```toml
[agents]
max_threads = 6
max_depth = 1
job_max_runtime_seconds = 1800

[agents.reviewer]
description = "Reviews changes for correctness and risk."
config_file = "agents/reviewer.toml"
```

Every agent file must include:

```toml
name = "reviewer"
description = "Reviews changes for correctness and risk."
model = "gpt-5.5"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Review changed files and report prioritized findings.
"""
```

## Skills

Register generated skills through `.agents/skills/<name>/SKILL.md` and enable
them from config when the current Codex version supports skill config entries.

```toml
[[skills.config]]
path = "../.agents/skills/validate-environment"
enabled = true
```

Keep each skill's trigger description specific enough for routing and put
deterministic scripts under `scripts/`.

## MCP configuration

Generate MCP configuration only for verified servers selected in ARCHITECTURE.md.
Use environment variables for secrets and document authentication steps in
GETTING_STARTED.md. Keep server instructions concise so tool selection can lazy
load the right tools.

If the current Codex config reference expects MCP servers in a separate file for
the target surface, generate that file and reference it from docs rather than
inventing `.codex/config.toml` keys.

## Hooks

Hooks are deterministic lifecycle automation. Generate hooks only from the
current Codex hook schema and only when the intake justifies them.

Common justified hooks:
- pre-compaction state save for long sessions;
- post-edit verification for projects with fast tests or lint;
- sensitive-file or binary-file guardrails for domains where accidental edits are
  likely.

Do not generate hook schemas copied from another runtime. If the schema is not
verified against the Codex config reference, leave a TODO in ARCHITECTURE.md and
make the validator warn instead of emitting invalid config.

## Local overrides

Machine-specific paths should not live in shared `.codex/config.toml`. Document a
gitignored local profile for engine paths, local CLIs, and per-user service
accounts.

Generated `.gitignore` or VCS ignore guidance should include the local profile
filename chosen by the architecture.

## Complete generated example

```toml
#:schema https://developers.openai.com/codex/config-schema.json

model = "gpt-5.5"
model_reasoning_effort = "medium"
model_verbosity = "medium"
approval_policy = "on-request"
default_permissions = "generated-environment"

[features]
multi_agent = true
memories = true
apps = true

[agents]
max_threads = 6
max_depth = 1
job_max_runtime_seconds = 1800

[agents.environment-validator]
description = "Validates generated Codex environments."
config_file = "agents/environment-validator.toml"

[[skills.config]]
path = "../.agents/skills/validate-environment"
enabled = true

[permissions.generated-environment]
description = "Workspace write access with sensitive paths and network access constrained."
extends = ":workspace"

[permissions.generated-environment.filesystem]
glob_scan_max_depth = 4

[permissions.generated-environment.filesystem.":workspace_roots"]
"." = "write"
"**/.env" = "deny"
"**/.env.*" = "deny"
"**/secrets/**" = "deny"
"**/*secret*" = "deny"
"**/*token*" = "deny"
"**/*credential*" = "deny"
"**/*.pem" = "deny"
"**/*.key" = "deny"

[permissions.generated-environment.network]
enabled = true
mode = "limited"

[permissions.generated-environment.network.domains]
"developers.openai.com" = "allow"
"docs.github.com" = "allow"
"pypi.org" = "allow"
"registry.npmjs.org" = "allow"
```

## Validation checklist

- [ ] File parses as TOML.
- [ ] Schema reference is present.
- [ ] `model = "gpt-5.5"` is present unless the user selected another model.
- [ ] `model_reasoning_effort` is present.
- [ ] If `default_permissions` is present, no top-level `sandbox_mode` is present.
- [ ] Permission profile denies sensitive files and private keys.
- [ ] Recursive deny globs have `glob_scan_max_depth` for portable pre-expansion.
- [ ] Network domains are limited to what the architecture justified.
- [ ] Agent registry points to `.codex/agents/*.toml` files that exist.
- [ ] Skill paths point to `.agents/skills/*/SKILL.md` folders that exist.
- [ ] No unsupported command allow/deny arrays are emitted.
- [ ] No hardcoded secrets, tokens, database URLs, or machine-local absolute paths.
- [ ] ASCII-only.

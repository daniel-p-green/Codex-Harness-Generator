# 11. Permissions

Codex permissions combine approval policy, sandboxing, filesystem scope, network
scope, and user-facing command guidance. Generated environments must use the
official `.codex/config.toml` shape and avoid inventing unsupported permission
arrays.

## 11.1 Codex Config Surface

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**: Use TOML permission profiles for shared runtime policy:

  ```toml
  [permissions.generated-environment]
  description = "Workspace write access with sensitive paths constrained."
  extends = ":workspace"

  [permissions.generated-environment.filesystem.":workspace_roots"]
  "." = "write"
  "**/.env" = "deny"
  "**/.env.*" = "deny"
  "**/secrets/**" = "deny"
  "**/*secret*" = "deny"
  "**/*credential*" = "deny"

  [permissions.generated-environment.network]
  enabled = true
  mode = "limited"

  [permissions.generated-environment.network.domains]
  "developers.openai.com" = "allow"

  default_permissions = "generated-environment"
  ```

  Do not combine `default_permissions` with top-level `sandbox_mode` or other
  top-level sandbox workspace settings.

- **Anti-pattern**: Generating JSON permission arrays or command-pattern rules
  that are not part of the current Codex config reference.

## 11.2 Filesystem Scope

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**: Pick the narrowest scope that still lets the environment
  work:
  - Normal code projects: workspace write, with sensitive paths denied.
  - Conservative document projects: write only to `Docs/**`, `_workspace/**`,
    `Outbox/**`, `.codex/**`, and `AGENTS.md`.
  - Data projects: raw data read-only; derived outputs writable.
  - Public-demo projects: write only to sanitized demo folders.

  Always deny local secrets, credentials, private keys, raw production exports,
  and any user-marked "never touch" paths.

- **Anti-pattern**: Excluding source, tests, or generated environment files from
  reads. Codex cannot verify what it cannot inspect.

## 11.3 Network Scope

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**: Use limited network mode and allow only domains justified
  by GENESIS.md or ARCHITECTURE.md.

  Typical additions:
  - OpenAI/Codex docs for generated harness maintenance.
  - Official package registries for projects that install dependencies.
  - Official API/docs domains for selected external services.
  - Official citation sources for research/legal/security workflows.

  Store tokens and service credentials in environment variables or a local
  profile, never in shared config.

- **Anti-pattern**: Adding broad wildcard domains because they might be useful.

## 11.4 Approval and Command Safety

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/config-reference,
  https://developers.openai.com/codex/concepts/customization | Tier 1
- **Recommendation**: Use `approval_policy` plus AGENTS.md command guidance:

  ```toml
  approval_policy = "on-request"
  ```

  Generated AGENTS.md should list safe verification commands and call out actions
  requiring explicit user approval:
  - force pushes, hard resets, branch deletion;
  - production database mutations;
  - deploys and package publishing;
  - disk formatting, permission changes, or shell pipelines from the internet;
  - credential rotation or destructive cloud operations.

- **Anti-pattern**: Encoding command rules in unsupported config keys. If the
  current Codex reference does not define the key, use instructions and
  validation checks instead.

## 11.5 Sandboxing

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**: Use sandbox settings through the supported Codex config
  pattern for the target surface. When a permission profile is selected through
  `default_permissions`, do not also set top-level sandbox workspace keys.

  Subagents can still use `sandbox_mode` in their individual TOML files to signal
  read-only or workspace-write intent.

- **Anti-pattern**: Copying sandbox settings from another runtime or combining
  mutually exclusive config patterns.

## 11.6 Managed and Local Settings

- **Established**: 2026-06-03 Codex port
- **Source**: https://developers.openai.com/codex/config-reference | Tier 1
- **Recommendation**:
  - Shared `.codex/config.toml`: project defaults safe for the repo.
  - Local profile: machine paths, private service accounts, personal tool paths.
  - Managed settings: organization-level policy, model availability, plugin policy.

  The generated environment should document where the user should place local
  overrides and include that filename in VCS ignore guidance.

- **Anti-pattern**: Hardcoding local absolute paths or secrets into shared config.

## 11.7 Validation Checks

Validator must fail when:
- `.codex/config.toml` is not parseable TOML.
- It lacks `model_reasoning_effort`.
- It combines `default_permissions` with top-level `sandbox_mode`.
- It lacks sensitive-path denies.
- It hardcodes secrets, tokens, private keys, database URLs, or personal absolute
  paths.
- It contains unsupported command allow/deny arrays.

Validator should warn when:
- network mode is broader than the architecture justifies;
- no local-profile guidance exists for machine-specific paths;
- a conservative domain allows broad writes without explanation.

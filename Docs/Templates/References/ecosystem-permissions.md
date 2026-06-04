# Ecosystem Permissions Reference

Reusable Codex permission-profile guidance for generated `.codex/config.toml`
files. Profiles should add only filesystem and network policy that the official
Codex config schema supports. Command-level safety belongs in AGENTS.md,
GETTING_STARTED.md, and validator checks unless the current config reference adds
a verified command-policy surface.

Pair with:
- `Docs/Templates/Core/codex-config-toml.md`
- `Docs/AgentGuidelines/Topics/11-permissions.md`
- https://developers.openai.com/codex/config-reference

## Base Profile

Use this as the starting point for normal generated environments.

```toml
default_permissions = "generated-environment"

[permissions.generated-environment]
description = "Workspace write access with sensitive paths and network access constrained."
extends = ":workspace"

[permissions.generated-environment.filesystem.":workspace_roots"]
"." = "write"
"**/.env" = "deny"
"**/.env.*" = "deny"
"**/secrets/**" = "deny"
"**/*secret*" = "deny"
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

## Conservative Profile

Use this when the project handles regulated data, legal/financial claims,
production infrastructure, or highly sensitive customer material.

```toml
default_permissions = "conservative-environment"

[permissions.conservative-environment]
description = "Conservative workspace policy for sensitive projects."
extends = ":workspace"

[permissions.conservative-environment.filesystem.":workspace_roots"]
"Docs/**" = "write"
"_workspace/**" = "write"
".codex/**" = "write"
"AGENTS.md" = "write"
"**/.env" = "deny"
"**/.env.*" = "deny"
"**/secrets/**" = "deny"
"**/*secret*" = "deny"
"**/*credential*" = "deny"
"**/*.pem" = "deny"
"**/*.key" = "deny"
"data/raw/**" = "read"
"exports/private/**" = "read"

[permissions.conservative-environment.network]
enabled = true
mode = "limited"

[permissions.conservative-environment.network.domains]
"developers.openai.com" = "allow"
```

## Domain Network Additions

Add only domains justified by GENESIS.md or ARCHITECTURE.md.

| Domain | Typical allowed domains |
|---|---|
| Python/data | `pypi.org`, `files.pythonhosted.org`, `docs.python.org` |
| Node/web | `registry.npmjs.org`, `nodejs.org`, `developer.mozilla.org` |
| Cloud/DevOps | official provider docs and APIs for the selected provider only |
| Research/writing | official source domains selected during intake |
| Security audit | `nvd.nist.gov`, `osv.dev`, `github.com`, `docs.github.com` |

Do not add broad wildcard domains unless the user explicitly needs them.

## Command Guidance by Ecosystem

Document these commands in AGENTS.md and GETTING_STARTED.md as project-specific
verification or operational commands. Do not encode them as unsupported TOML
permission arrays.

| Ecosystem | Safe verification commands | Require explicit approval |
|---|---|---|
| Git | `git status`, `git diff`, `git log`, `git show`, `git blame` | force push, hard reset, clean, branch deletion |
| Python | `python -m pytest`, `ruff check`, `mypy`, `python -m compileall` | arbitrary package installs, system package changes |
| Node / TypeScript | `npm test`, `npm run build`, `npm run lint`, `npx tsc --noEmit` | publish, unpublish, destructive dependency changes |
| Go | `go test ./...`, `go vet ./...`, `gofmt` | release publishing, destructive clean operations |
| Rust | `cargo test`, `cargo check`, `cargo clippy`, `cargo fmt` | publish, yank, destructive clean operations |
| Java | `mvn test`, `mvn verify`, `./gradlew test` | deploy, publish, credentialed release actions |
| .NET | `dotnet test`, `dotnet build`, `dotnet format --verify-no-changes` | package publishing, production deploys |
| Docker | image inspection and local build commands | pruning, removing running containers, registry push |
| Infrastructure | `terraform plan`, `terraform validate`, `kubectl get`, logs/describe | apply, destroy, delete, production mutations |

## Data Files

When intake marks raw data as immutable, add read-only guidance in AGENTS.md and
deny or constrain write paths in the permission profile. Generated workflows
should write derived outputs to `Docs/_working/`, `_workspace/`, `output/`, or
`Outbox/`, not back into raw source directories.

## Local Profile

Machine-specific paths, local database URLs, and service credentials belong in a
gitignored local profile or environment variables. Shared `.codex/config.toml`
must never contain secrets or absolute paths unique to one developer's machine.

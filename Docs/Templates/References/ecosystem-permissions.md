# Ecosystem Permissions Reference

Reusable `settings.json` permission sets per language/tool ecosystem. Slim
starter profiles and bundled domains reference this file instead of inlining the
JSON. The component-generator composes a project's `settings.json` from the Base
set + Universal Deny + the ecosystems the intake identified. Pair with
`Docs/Templates/Core/settings-json.md` (structure) and topic 11 (permissions).

Ordering rule: deny -> ask -> allow. Always include the Universal Deny set.

## Base (all projects)

```json
{
  "permissions": {
    "allow": [
      "Read(./**)",
      "Edit(./Docs/**)", "Write(./Docs/**)",
      "Edit(./.claude/**)", "Write(./.claude/**)",
      "Edit(./CLAUDE.md)", "Write(./CLAUDE.md)",
      "WebSearch", "WebFetch(*)"
    ],
    "deny": [
      "Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)",
      "Read(./**/*credentials*)", "Read(./**/*secret*)"
    ]
  }
}
```

## Universal Deny (all languages -- always include)

```json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf /)", "Bash(rm -rf /*)", "Bash(sudo *)", "Bash(chmod 777 *)",
      "Bash(curl * | bash)", "Bash(curl * | sh)", "Bash(wget * | bash)",
      "Bash(wget * | sh)", "Bash(mkfs *)", "Bash(dd if=*)", "Bash(:(){ :|:& };:)"
    ]
  }
}
```

## Git

allow: `git status/diff/log/branch/add/commit/checkout/switch/stash/fetch/pull/show/blame *`,
`git push`, `git push origin *`, `git merge/rebase/cherry-pick/tag *`.
deny: `git push --force *`, `git push -f *`, `git reset --hard *`, `git clean -f *`,
`git checkout -- .`, `git branch -D *`.

## Python

allow: `python *`, `python3 *`, `pip install/list/show/freeze *`, `pytest *`,
`mypy *`, `ruff *`, `black *`, `isort *`, `flake8 *`, `poetry *`, `uv *`.
deny: `pip install --user *`, `python -m pip install --break-system-packages *`.
Verify: `pytest`, `mypy .`, `ruff check .`

## Node / TypeScript

allow: `node *`, `npm install/run/test/list *`, `npx *`, `yarn *`, `pnpm *`,
`tsc *`, `eslint *`, `prettier *`, `vitest *`, `jest *`.
deny: `npm publish/unpublish/deprecate *`, `yarn publish *`, `pnpm publish *`.
Verify: `npm test`, `npx tsc --noEmit`, `npx eslint .`

## Go

allow: `go build/test/run/vet/mod/fmt/generate *`, `golangci-lint *`, `staticcheck *`.
Verify: `go test ./...`, `go vet ./...`, `golangci-lint run`

## Rust

allow: `cargo build/test/run/check/clippy/fmt/doc *`, `rustfmt *`.
deny: `cargo publish *`, `cargo yank *`.
Verify: `cargo test`, `cargo clippy -- -D warnings`, `cargo check`

## Java

allow: `mvn *`, `gradle *`, `./gradlew *`, `java *`, `javac *`.
deny: `mvn deploy *`, `gradle publish *`, `./gradlew publish *`.
Verify: `mvn test`, `./gradlew test`, `mvn verify`

## C# / .NET

allow: `dotnet build/test/run/restore/format *`.
deny: `dotnet nuget push *`, `dotnet nuget delete *`.
Verify: `dotnet test`, `dotnet build --no-restore`, `dotnet format --verify-no-changes`

## Docker (when containerized)

allow: `docker *`, `docker-compose *`. deny: `docker system prune -a *`.

## Data / Python-analysis (pandas, notebooks)

allow (in addition to Python): `jupyter *`, `papermill *`. Treat large data files
as read-mostly; deny writes to raw-data directories if the intake flags them
immutable.

## Infrastructure (Terraform / Kubernetes / cloud CLIs)

allow: `terraform plan/validate/fmt *`, `kubectl get/describe/logs *`,
`aws *` / `gcloud *` / `az *` (read-oriented subcommands).
deny (gate behind human approval): `terraform apply *`, `terraform destroy *`,
`kubectl delete *`, `kubectl apply *`, any `* delete *` / `* rm *` cloud mutation.
These are the infrastructure safety gates -- never auto-approve state mutation.

## settings.local.json

Generate `settings.local.json` for machine-specific paths detected in intake
(custom tool dirs, local DB connection strings). Never commit secrets.

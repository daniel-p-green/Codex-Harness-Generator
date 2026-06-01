# 11. Permissions

## 11.1 Full Syntax Reference

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: Permission rule syntax:
  - `Tool` -- matches all uses of that tool
  - `Tool(specifier)` -- matches specific patterns
  - `Bash(npm run *)` -- wildcard patterns for commands
  - `Read(./.env)` -- file paths using gitignore syntax
  - `WebFetch(domain:example.com)` -- domain restrictions
  - `mcp__server__tool` -- MCP tool matching
  - `Task(AgentName)` -- subagent matching

  Path patterns:
  - `//path` -- absolute from filesystem root
  - `~/path` -- from home directory
  - `/path` -- relative to settings file
  - `path` or `./path` -- relative to current directory
  - `*` matches single directory, `**` matches recursively
- **Anti-pattern**: Using incorrect path syntax. The most common mistake is using
  backslashes on Windows; always use forward slashes in permission rules.

## 11.2 Evaluation Order (deny -> ask -> allow)

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: Permissions evaluate in strict order: deny first, then ask, then allow.
  First match wins. This means:
  - A deny rule always blocks, even if a later allow rule would match
  - Always put deny rules for sensitive files/operations
  - Use allow for routine, safe operations
  - Use ask for operations that need judgment

  Base deny rules for all environments:
  ```json
  {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(rm -rf /)",
      "Bash(sudo *)"
    ]
  }
  ```
- **Anti-pattern**: Assuming allow rules override deny rules. They do not. If you deny
  `Read(./.env)` and allow `Read(./**)`, the deny wins for .env files.

## 11.3 Sandbox Patterns (Dual Isolation)

- **Established**: 2025-10
- **Source**: claude-code-sandboxing.md | Tier 1
- **Recommendation**: Effective sandboxing requires BOTH filesystem and network isolation.
  Either boundary alone is insufficient:
  - Without network isolation: compromised agent can exfiltrate files
  - Without filesystem isolation: compromised agent can escape sandbox

  Implementation:
  - Filesystem: bubblewrap on Linux, Seatbelt on macOS, planned for Windows native
  - Network: Unix domain socket proxy restricting reachable domains
  - Activate: `/sandbox` command or `sandbox` config in settings

  Sandboxing achieves 84% reduction in permission prompts compared to permission-only
  security. Recommend `autoAllowBashIfSandboxed: true` for sandboxed environments.
- **Anti-pattern**: Relying on permission prompts alone for security. Approval fatigue causes
  users to stop reviewing, paradoxically reducing security. Sandboxing provides structural
  security without user fatigue.

## 11.3b April 2026 Permission Hardening

- **Established**: 2026-04-20
- **Source**: code.claude.com/docs/en/changelog v2.1.73-v2.1.113 | Tier 1
- **Recommendation**: Several permission behaviors changed in April 2026 Claude Code releases.
  Audit generated environments against these:
  - `Bash(find:*)` allow rules NO LONGER auto-approve `find -exec` or `find -delete` (v2.1.113).
    Split into explicit allow + deny if you need one and not the other.
  - Bash deny rules now correctly match commands wrapped in `env`, `sudo`, `watch`, `ionice`,
    `setsid` (v2.1.113). Prior bypasses closed.
  - Compound Bash commands (e.g., `cmd1 && cmd2`) now require permission prompts for
    per-command safety checks (v2.1.98). Generated allow rules for compound commands should
    be broken into individual entries.
  - Windows drive-letter paths are now correctly root-anchored; case-insensitive path
    matching (v2.1.101).
  - macOS `/private/{etc,var,tmp,home}` treated as dangerous under `Bash(rm:*)` allow
    rules (v2.1.113).
  - `Edit(//path/**)` / `Read(//path/**)` rules now check the resolved symlink target
    (v2.1.89). Generated rules using symlinked paths need verification.
  - PreToolUse hook `updatedInput` is re-checked against `permissions.deny` (v2.1.110).
    Hooks that modify input to bypass deny rules no longer work.
  - PreToolUse `defer` decision: headless sessions can pause and resume with
    `-p --resume` (v2.1.89).
- **Anti-pattern**: Shipping older permission rule patterns without re-validation. Rules
  that worked in 2025 may now produce unexpected prompts or denials.

## 11.4 Enterprise Controls

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: Managed settings for enterprise deployment:
  - `disableBypassPermissionsMode: "disable"` -- prevents bypass mode
  - `allowManagedPermissionRulesOnly: true` -- blocks user/project rules
  - `allowManagedHooksOnly: true` -- blocks user/project hooks
  - `strictKnownMarketplaces` -- controls plugin sources
  - `availableModels` -- restricts which models users can select (e.g., `["sonnet", "haiku"]`).
    Combine with `model` setting to enforce a specific model. Arrays merge across settings levels.
  - Managed settings location: system-level directories (varies by OS)

  Managed settings have highest precedence and cannot be overridden by project or user
  settings.

  Model pinning for third-party deployments (Bedrock, Vertex AI, Foundry): Set
  `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, and
  `ANTHROPIC_DEFAULT_HAIKU_MODEL` to version-specific IDs. Without pinning, model alias
  updates can silently break deployments when new versions are released.
- **Anti-pattern**: Deploying Claude Code in enterprise environments without managed settings.
  Users can bypass all restrictions with `--dangerously-skip-permissions` unless explicitly
  disabled via managed settings.

---

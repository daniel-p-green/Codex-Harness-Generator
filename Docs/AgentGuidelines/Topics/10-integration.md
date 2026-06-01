# 10. External Integration and MCP

Connecting generated environments to external services (VCS, build systems,
CLI tools, CI/CD) and configuring Model Context Protocol (MCP) servers.

## Table of contents

- 10.1 VCS Patterns (Git) [ALL]
- 10.2 Build Systems [ALL]
- 10.3 External Tools and CLIs [ALL]
- 10.4 Settings File Separation [ALL]
- 10.5 CI/CD Integration [ALL]
- 10.6 MCP Transport Types [ALL]
- 10.7 MCP Scopes [ALL]
- 10.8 MCP Tool Naming [ALL]
- 10.9 .mcp.json Patterns and Configuration [ALL]
- 10.10 Verified MCP Server Discipline [ALL]
- 10.11 MCP Tool Search for Context Reduction [4.7+]
- 10.12 Browser Automation Tools [ALL]
- 10.13 MCP Elicitation and OAuth [4.7+]

---

## 10.1 VCS Patterns (Git) [ALL]

- **Established**: Baseline
- **Source**: common-workflows.md, claude-code-best-practices.md | Tier 1
- **Recommendation**: Git integration patterns for generated environments:
  - Pre-approve safe operations: `Bash(git diff *)`, `Bash(git status)`, `Bash(git log *)`
  - Require confirmation for: `Bash(git push *)`, `Bash(git reset --hard *)`
  - Deny: `Bash(git push --force *)` unless explicitly requested
  - Session naming with ticket numbers: `/rename JIRA-1234-fix-auth`
  - Git worktrees for parallel work without Agent Teams
  - `gh` CLI is the most context-efficient way to interact with GitHub

  For Perforce environments, adapt with: `p4 edit`, `p4 add`, `p4 reopen` as safe;
  `p4 submit` as human-only.
- **Anti-pattern**: Not including VCS permissions in generated settings.json. Users get
  constant permission prompts for routine git operations, causing approval fatigue.

## 10.2 Build Systems [ALL]

- **Established**: Baseline
- **Source**: claude-code-best-practices.md, common-workflows.md | Tier 1
- **Recommendation**: Include build commands in CLAUDE.md and pre-approve them in
  settings.json:
  - `Bash(npm run build)`, `Bash(npm run test)`, `Bash(npm run lint)` for Node projects
  - `Bash(cargo build *)`, `Bash(cargo test *)` for Rust projects
  - `Bash(python -m pytest *)` for Python projects

  Verification is the #1 highest-leverage thing you can do. Invest in making your
  verification rock-solid. Include test commands, linters, type checkers appropriate to the
  language. Claude performs dramatically better with self-verification.
- **Anti-pattern**: Not providing verification commands. Without them, you become the only
  feedback loop, and Claude cannot self-correct.

## 10.3 External Tools and CLIs [ALL]

- **Established**: Baseline
- **Source**: claude-code-best-practices.md | Tier 1
- **Recommendation**: Tell Claude about CLI tools it can use: `gh`, `aws`, `gcloud`,
  `sentry-cli`, `terraform`, `kubectl`. Claude can learn unfamiliar CLIs by using their
  `--help` output. Include in CLAUDE.md: "Use 'foo-cli-tool --help' to learn about foo
  tool, then use it to solve A, B, C."

  MCP servers connect external services: Notion, Figma, databases, monitoring, issue
  trackers. Use `claude mcp add` to configure. See sections 10.6-10.11 for full MCP
  configuration guidance.
- **Anti-pattern**: Expecting Claude to discover tools on its own. Explicitly list available
  CLI tools and their primary use cases in CLAUDE.md.

## 10.4 Settings File Separation [ALL]

- **Established**: 2026-02
- **Source**: production game project production environment | Tier 2
- **Recommendation**: Use `settings.local.json` for machine-specific configuration
  (engine paths, local tool paths, user-specific hooks) and `settings.json` for
  shared team configuration (permissions, deny rules, ecosystem settings).

  `settings.local.json` is gitignored and contains paths that vary between developer
  machines. This prevents merge conflicts on team projects and avoids hardcoding
  local paths in shared configuration.

  Example split:
  - `settings.json`: permission rules, deny rules, ecosystem profiles, hook definitions
  - `settings.local.json`: absolute paths to engines/tools, user-specific Bash permissions,
    local MCP server configurations
- **Anti-pattern**: Putting machine-specific paths in settings.json. On team projects,
  every developer has different paths, causing constant merge conflicts or broken configs.

## 10.5 CI/CD Integration [ALL]

- **Established**: 2026-02
- **Source**: claude-code-docs.md, GitHub Actions documentation | Tier 1
- **Recommendation**: For software development environments using GitHub, suggest
  integrating Claude Code GitHub Actions for automated PR review and issue triage.
  Setup: `/install-github-app` in Claude Code CLI.

  When the intake identifies CI/CD needs, the architect should consider generating
  GitHub Actions workflow files:

  - `quality.yml`: lint, type-check, test with coverage threshold
  - `security.yml`: dependency audit, secrets scanning

  These are optional components -- only generate when the intake confirms CI/CD use.
  Do not generate workflows for projects without CI/CD infrastructure.

  For non-GitHub projects, document equivalent CI integration in GETTING_STARTED.md
  rather than generating platform-specific config files.
- **Anti-pattern**: Generating CI configs for projects that do not use CI/CD.
  Unused workflow files add confusion and maintenance burden.

## 10.6 MCP Transport Types [ALL]

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: Three transport options for MCP servers:
  - **HTTP** (recommended): `claude mcp add --transport http <name> <url>` -- modern,
    efficient, recommended for new integrations
  - **SSE** (deprecated): `claude mcp add --transport sse <name> <url>` -- legacy,
    streaming server-sent events
  - **stdio** (local): `claude mcp add --transport stdio <name> -- <command> [args]` --
    for local processes

  Windows note for stdio with npx: use `cmd /c` wrapper:
  `claude mcp add --transport stdio name -- cmd /c npx -y @package`
- **Anti-pattern**: Using SSE for new integrations. It is deprecated in favor of HTTP.

## 10.7 MCP Scopes [ALL]

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: MCP server scopes control visibility:
  - **local** (default): Private, current project only. Stored in `~/.claude.json`
  - **project**: Shared via `.mcp.json` (checked into VCS). Visible to all team members.
  - **user**: Available across all projects. Stored in `~/.claude.json`

  For generated environments, use project scope (`.mcp.json`) for team-shared integrations.
  Use local scope for per-developer credentials.
- **Anti-pattern**: Committing local-scope MCP configurations that contain credentials to
  VCS. Use project scope with environment variable expansion for secrets.

## 10.8 MCP Tool Naming [ALL]

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md, claude-code-docs.md | Tier 1
- **Recommendation**: Always use fully qualified names for MCP tools:
  `ServerName:tool_name` (e.g., `BigQuery:bigquery_schema`, `GitHub:create_issue`).
  In permission rules: `mcp__server__tool`. Without the server prefix, Claude may fail to
  locate the tool. Skills referencing MCP tools must use fully qualified names.

  When MCP tool definitions exceed 10% of context, Tool Search auto-enables (see 10.11).
  Control with `ENABLE_TOOL_SEARCH` (auto, auto:N, true, false).
- **Anti-pattern**: Using short tool names without server prefix. This causes tool resolution
  failures when multiple MCP servers are configured.

## 10.9 .mcp.json Patterns and Configuration [ALL]

- **Established**: Baseline
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: Generate `.mcp.json` for project-scoped MCP servers. Minimal
  structure:
  ```json
  {
    "mcpServers": {
      "server-name": {
        "command": "/path/to/server",
        "args": [],
        "env": {}
      }
    }
  }
  ```

  Example with a real server (GitHub via Docker, using env var expansion for the token):
  ```json
  {
    "mcpServers": {
      "github": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                 "ghcr.io/github/github-mcp-server"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"}
      }
    }
  }
  ```

  Support environment variable expansion: `${VAR}`, `${VAR:-default}`. Works in command,
  args, env, url, and headers fields. Use for all sensitive values.

  Managed MCP (`managed-mcp.json`) takes exclusive control in enterprise environments.
  `allowedMcpServers`/`deniedMcpServers` provide policy-based control.
- **Anti-pattern**: Hardcoding credentials, tokens, passwords, or API keys in `.mcp.json`.
  Use environment variable expansion for all sensitive values.

## 10.10 Verified MCP Server Discipline [ALL]

- **Established**: 2026-03
- **Source**: tool-registry.md, quality-gates.md gate 39 | Tier 1
- **Recommendation**: Every MCP server placed in a generated `.mcp.json` or settings.json
  MUST be a verified server drawn from the "Verified MCP Servers" section of
  `Docs/Templates/References/tool-registry.md`. Do not invent or hallucinate MCP package
  names, npm specifiers, or Docker images. If a needed integration is not in the registry,
  document the gap in GETTING_STARTED.md and let the user add it manually rather than
  emitting an unverified server config.

  This is enforced by validator quality gate 39 (no invented/hallucinated MCP packages)
  and gate 42 (every external dependency must have been approved in the ARCHITECTURE.md
  Environment Complexity decision table).
- **Anti-pattern**: Emitting a plausible-looking but unverified MCP server entry. A wrong
  package name yields a silent connection failure the user cannot easily diagnose.

## 10.11 MCP Tool Search for Context Reduction [4.7+]

- **Established**: 2026-02, expanded 2026-03
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: When MCP tool definitions exceed 10% of the context window, MCP
  Tool Search auto-enables. Instead of loading all tool definitions upfront, it indexes
  them and defers loading, using an on-demand search tool that loads only the tools Claude
  actually needs for the current task. This can reduce MCP-related context consumption by
  up to 95%.

  Configuration via the `ENABLE_TOOL_SEARCH` environment variable:
  - `auto` (default): enables when tool definitions exceed 10% of context
  - `auto:N` (e.g., `auto:5`): custom percentage threshold
  - `true`: always enable Tool Search regardless of tool count
  - `false`: disable Tool Search entirely

  For environments with 3+ MCP servers, recommend enabling Tool Search and document the
  setting in GETTING_STARTED.md with the recommended threshold:
  ```json
  {
    "env": {
      "ENABLE_TOOL_SEARCH": "auto:5"
    }
  }
  ```

  Include guidance on the server `instructions` field -- Tool Search uses server
  instructions to understand when to load which tools, so well-written instructions
  improve tool selection accuracy.
- **Anti-pattern**: Loading 10+ MCP servers without Tool Search. Each server's tool
  definitions consume context tokens; with many servers this can consume 20-30% of
  available context before any work begins. Also: not configuring server `instructions`
  fields when Tool Search is active -- without them, Tool Search relies only on tool names
  and descriptions, which may miss relevant tools or load unnecessary ones.

## 10.12 Browser Automation Tools [ALL]

- **Established**: 2026-03
- **Source**: microsoft/playwright-mcp (GitHub), testcollab.com/blog/playwright-cli,
  testdino.com/blog/playwright-cli-vs-mcp, ayyaztech.com | Tier 1 + Tier 2
- **Recommendation**: Three browser automation approaches exist for Claude Code,
  each with distinct trade-offs. Choose based on the project's needs:

  | Tool | Token Cost | Auth Sessions | Headless/CI | Best For |
  |------|-----------|---------------|-------------|----------|
  | **Playwright CLI** | ~27K/session (4x more efficient than MCP) | No | Yes | Coding agents: testing, scraping, automation in projects with shell access |
  | **Playwright MCP** | ~114K/session (33+ tools, full accessibility tree inline) | No | Yes | Sandboxed agents without filesystem access (Claude Desktop, chat interfaces) |
  | **Chrome DevTools MCP** | ~9% context for tool defs | No | Yes | Performance profiling, Core Web Vitals, network/console debugging |
  | **Claude in Chrome** | ~7.7% context for tool defs | Yes (logged-in sessions) | No | Authenticated workflows (Gmail, Notion, etc.), multi-tab |

  **For Claude Code environments (shell access), Playwright CLI is the default
  recommendation.** It saves snapshots to disk as YAML files with compact element
  references (e.g., `[ref=e21]`) instead of streaming full accessibility trees
  into context. The agent reads snapshot files on demand, keeping context clean.

  Install: `npm install -g @playwright/cli`
  Commands: `playwright-cli open <url>`, `snapshot`, `click <ref>`, `fill`,
  `screenshot`, `close`

  Sessions that degrade after ~15 interactions with MCP run stable for 50+ with
  CLI. The CLI also auto-generates executable Playwright test code as a side
  effect of browser automation.

  **When to recommend each during generation**:
  - Frontend/web dev, testing, web scraping -> Playwright CLI (default)
  - Need authenticated browser sessions -> Claude in Chrome
  - Performance profiling, Core Web Vitals -> Chrome DevTools MCP
  - Agent without shell access -> Playwright MCP (fallback only)
  - Multiple browser engines needed -> Playwright MCP (Chromium + Firefox + WebKit)

  **For generated environments**: When intake reveals browser automation needs,
  include Playwright CLI install command and basic usage in GETTING_STARTED.md.
  If the user also needs MCP for specific reasons, add both but note the token
  trade-off. Do NOT default to Playwright MCP for Claude Code environments --
  the 4x token overhead is unnecessary when shell access is available.
- **Anti-pattern**: Defaulting to Playwright MCP for Claude Code projects. MCP
  streams full accessibility trees (800+ tokens per page) into context on every
  interaction, causing context pollution in longer sessions. CLI is strictly
  better when the agent has filesystem access. Also: adding all three browser
  tools simultaneously without clear need for each.

## 10.13 MCP Elicitation and OAuth [4.7+]

- **Established**: 2026-04-20
- **Source**: code.claude.com/docs/en/changelog v2.1.76-v2.1.97 | Tier 1
- **Recommendation**: April 2026 brought several MCP enhancements relevant to environment
  generation:

  **Elicitation (v2.1.76)**: MCP servers can request structured input from the user
  mid-task via interactive dialog. Claude Code surfaces `Elicitation` and
  `ElicitationResult` hook events, so you can intercept and log these. Useful for MCP
  servers that need API keys or configuration decisions on first use rather than upfront.

  **Tool description cap (v2.1.84)**: MCP tool descriptions are now capped at 2KB each.
  OpenAPI-generated MCP servers that produced bloated descriptions will be truncated --
  prefer hand-authored descriptions for key tools.

  **OAuth improvements**:
  - RFC 9728 Protected Resource Metadata discovery supported (v2.1.85)
  - `oauth.authServerMetadataUrl` config honored on token refresh (v2.1.97)
  - Step-up authorization: 403 `insufficient_scope` triggers re-auth (v2.1.85)

  **Result size override (v2.1.91)**: MCP results can override result persistence size
  via `_meta["anthropic/maxResultSizeChars"]` up to 500k chars. Useful for servers that
  return large structured data (e.g., Perforce depot listings).

  **MCP deny rules (v2.1.78)**: `deny: ["mcp__servername"]` now properly removes tools
  before they're sent to the model (previously tools were filtered post-hoc).
- **Anti-pattern**: Generating MCP server configurations without hand-authored
  descriptions for key tools -- auto-generated ones may truncate at 2KB.

---

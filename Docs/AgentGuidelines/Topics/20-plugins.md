# 20. Plugins

## 20.1 Plugin Architecture

- **Established**: 2026-03
- **Source**: claude.com/blog/claude-code-plugins, code.claude.com/docs/en/plugins | Tier 1
- **Recommendation**: Plugins are lightweight packages bundling slash commands, subagents,
  MCP servers, and hooks into a single installable unit. Install via `/plugin` command.

  Plugin directory structure:
  ```
  my-plugin/
  +-- .claude-plugin/
  |   +-- plugin.json       # manifest (name, description, version, author)
  +-- skills/
  |   +-- my-skill/
  |       +-- SKILL.md      # skill definition (same format as project skills)
  +-- agents/               # optional agent definitions
  +-- hooks/                # optional hook definitions
  ```

  Plugin marketplaces: git/GitHub repos with `.claude-plugin/marketplace.json`.
  Add via `/plugin marketplace add user-or-org/repo-name`.

  For generated environments: recommend relevant community plugins in GETTING_STARTED.md
  rather than reimplementing common patterns. Plugins can be toggled on/off to reduce
  system prompt context.

  Test during development: `--plugin-dir` flag loads plugins without installation.
- **Anti-pattern**: Building complex custom skills when a well-maintained plugin already
  exists. Check the official Anthropic plugin marketplace first.

## 20.2 Plugin Considerations for Environment Generation

- **Established**: 2026-03
- **Source**: code.claude.com/docs/en/plugins | Tier 1
- **Recommendation**: When generating environments, consider whether functionality would be
  better delivered as a plugin (shareable, toggleable) or as project-local skills/agents
  (tightly coupled to project). Rules of thumb:
  - **Plugin**: Generic patterns reusable across projects (PR review, security scanning,
    framework-specific helpers, LSP support)
  - **Project-local**: Domain-specific logic tied to project structure, routing tables,
    memory schemas
  - Enterprise: Use `strictKnownMarketplaces` to restrict plugin sources to approved repos
  - Skill folder name becomes the command name, prefixed with the plugin namespace
- **Anti-pattern**: Distributing project-specific configuration as a plugin. Plugins should
  be project-agnostic; project-specific rules belong in `.claude/rules/` and project skills.

## 20.3 Anthropic Official Skills Repository

- **Established**: 2026-03
- **Source**: github.com/anthropics/skills, agentskills.io/specification | Tier 1
- **Recommendation**: Anthropic maintains an official skills repository at
  `github.com/anthropics/skills` containing production-quality skills organized into three
  plugin collections installable via the marketplace system:

  **Document skills** (`document-skills@anthropic-agent-skills`):
  - `xlsx`: Excel spreadsheet creation and manipulation
  - `docx`: Word document generation and editing
  - `pptx`: PowerPoint presentation creation
  - `pdf`: PDF extraction, form filling, and merging

  **Example skills** (`example-skills@anthropic-agent-skills`):
  - `skill-creator`: Meta-skill for creating, testing, benchmarking, and optimizing skills.
    Includes eval framework with grader/analyzer/comparator agents, test case management,
    variance analysis, and description optimization for triggering accuracy.
  - `mcp-builder`: Guide for creating MCP servers (TypeScript recommended). Covers API
    research, implementation, testing with MCP Inspector, and eval generation.
  - `webapp-testing`: Playwright-based web app testing with server lifecycle management.
  - `frontend-design`: Frontend design patterns and implementation guidance.
  - `canvas-design`: Visual canvas design capabilities.
  - `web-artifacts-builder`: Interactive HTML/JS artifact generation.
  - `algorithmic-art`: Generative art and algorithmic visual creation.
  - `brand-guidelines`: Brand consistency enforcement for generated content.
  - `doc-coauthoring`: Collaborative document drafting and editing.
  - `internal-comms`: Internal communication drafting (emails, announcements, memos).
  - `slack-gif-creator`: Slack-compatible GIF creation.
  - `theme-factory`: Theme and design system generation.

  **Claude API skill** (`claude-api@anthropic-agent-skills`):
  - `claude-api`: SDK reference for Python, TypeScript, Java, Go, Ruby, C#, PHP, cURL.
    Also a bundled skill that auto-activates on Anthropic SDK imports.

  Installation: `claude /plugin marketplace add anthropics/skills` then
  `claude /plugin install <collection>@anthropic-agent-skills`.

  These skills follow the Agent Skills open specification (agentskills.io). Key spec
  constraints: name max 64 chars (lowercase, hyphens), description max 1024 chars,
  SKILL.md under 500 lines, progressive disclosure via scripts/references/assets dirs.

  The repository is a living resource. New skills may be added over time. When generating
  environments, recommend installation from the latest repository rather than copying
  skill content statically, so users benefit from upstream improvements.

- **Anti-pattern**: Statically copying official skill content into generated environments.
  This creates maintenance burden and prevents users from receiving upstream improvements.
  Instead, recommend installing from the marketplace and document the install commands.

## 20.4 Plugin Recommendations During Environment Generation

- **Established**: 2026-03
- **Source**: github.com/anthropics/skills, code.claude.com/docs/en/skills | Tier 1
- **Recommendation**: During environment generation, match intake answers to available
  official plugins and recommend installation in GETTING_STARTED.md. Matching rules:

  | Intake Signal | Recommended Plugin | Install Command |
  |---|---|---|
  | Works with spreadsheets/CSV/Excel | document-skills | `/plugin install document-skills@anthropic-agent-skills` |
  | Produces Word documents | document-skills | `/plugin install document-skills@anthropic-agent-skills` |
  | Creates presentations | document-skills | `/plugin install document-skills@anthropic-agent-skills` |
  | Works with PDFs | document-skills | `/plugin install document-skills@anthropic-agent-skills` |
  | Frontend/web development | example-skills (frontend-design, web-artifacts-builder) | `/plugin install example-skills@anthropic-agent-skills` |
  | Web application testing | example-skills (webapp-testing) | `/plugin install example-skills@anthropic-agent-skills` |
  | Building MCP servers | example-skills (mcp-builder) | `/plugin install example-skills@anthropic-agent-skills` |
  | Brand/design guidelines | example-skills (brand-guidelines, theme-factory) | `/plugin install example-skills@anthropic-agent-skills` |
  | Internal communications | example-skills (internal-comms) | `/plugin install example-skills@anthropic-agent-skills` |
  | Building with Claude API/SDK | claude-api | `/plugin install claude-api@anthropic-agent-skills` |
  | Wants to create custom skills | example-skills (skill-creator) | `/plugin install example-skills@anthropic-agent-skills` |

  Format in GETTING_STARTED.md as an "Optional Plugins" section:
  ```
  ## Optional Plugins

  These official Anthropic plugins add capabilities to your environment. Install
  the marketplace first, then install the plugins you need:

  claude /plugin marketplace add anthropics/skills
  claude /plugin install <collection>@anthropic-agent-skills

  | Plugin | What It Adds | Install When |
  |--------|-------------|--------------|
  | document-skills | Excel, Word, PowerPoint, PDF tools | You work with office documents |
  | example-skills | Web testing, frontend design, MCP builder, skill creator | You build web apps or want to create custom skills |
  | claude-api | Claude SDK reference for all languages | You build applications using the Claude API |
  ```

  Do NOT auto-install plugins during generation. Document the commands and let the user
  choose. Different team members may need different plugin sets.

  For advanced users: mention the skill-creator skill as a way to extend their environment
  with custom skills that include test harnesses and performance benchmarks.

- **Anti-pattern**: Recommending every available plugin regardless of relevance. Only
  recommend plugins that match specific intake signals. An irrelevant plugin wastes
  context budget (skill descriptions are always loaded).

## 20.5 Plugin Enhancements (April 2026)

- **Established**: 2026-04-20
- **Source**: code.claude.com/docs/en/changelog v2.1.80-v2.1.105 | Tier 1
- **Recommendation**: Several plugin capabilities expanded in April 2026:

  **Plugin monitors (v2.1.105)**: Plugins can declare a `monitors` key in manifest that
  auto-arm background monitor tasks. Relevant when generating environments that need
  long-running passive watchers (file change listeners, CI polling, etc.).

  **User configuration (v2.1.101)**: `manifest.userConfig` lets plugins prompt for
  configuration at enable time. Values with `sensitive: true` are stored securely. Prefer
  this over environment variables for user-supplied plugin secrets.

  **Bundled executables (v2.1.91)**: Plugins can ship binaries in `bin/` that are invoked
  as bare commands from Bash. Useful for Pipeline pattern skills that wrap CLIs.

  **Inline plugin declarations (v2.1.80)**: `source: 'settings'` lets you declare plugin
  entries directly in settings.json without a separate manifest. Useful for
  environment-local custom plugins.

  **Skill name stability (v2.1.94)**: Plugin skills with `"skills": ["./"]` use
  frontmatter `name` instead of directory basename. Ensures consistent identity if the
  plugin gets renamed.

## 20.6 Plugin Enhancements (May 2026)

- **Established**: 2026-05-31
- **Source**: code.claude.com/docs/en/changelog v2.1.118-v2.1.157 | Tier 1
- **Recommendation**: Plugin authoring got simpler in May 2026:

  **Auto-load from `.claude/skills` (v2.1.157)**: Plugins placed in a `.claude/skills`
  directory now load automatically -- no marketplace registration required. This is the
  most common-case win: a generated environment can ship a local plugin under
  `.claude/skills/` and it just works. Plugins with a root-level `SKILL.md` and no
  `skills/` subdirectory are surfaced as skills (v2.1.142).

  **`claude plugin init <name>` (v2.1.157)**: Scaffolds a new plugin in `.claude/skills/`.
  Mention in GETTING_STARTED.md when the environment encourages users to author their own
  skills.

  **`defaultEnabled: false` (v2.1.154)**: Set in `plugin.json` or a marketplace entry to
  ship a plugin disabled; the user enables it with `/plugin` or `claude plugin enable`.
  Use for optional/heavy plugins so generated environments don't auto-activate everything.

  **Dependency enforcement (v2.1.143, v2.1.121)**: `claude plugin disable` refuses when an
  enabled plugin depends on the target; `enable` force-enables transitive deps; `prune`
  removes orphaned auto-installed deps. Declare plugin dependencies explicitly so this
  works.

  **Experimental schema namespacing (v2.1.129)**: `themes` and `monitors` keys must now
  live under an `"experimental": { ... }` object in the manifest. Update any generated
  manifests using the April 2026 `monitors` top-level form (20.5).

---

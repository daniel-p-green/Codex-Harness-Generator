# Template: settings.json

<!-- TEMPLATE ANNOTATION
  This template defines the generated .claude/settings.json file.
  It covers the full permission syntax, ecosystem-specific permission profiles,
  universal deny rules, hook configuration, MCP configuration, and sandbox config.

  QUALITY CRITERIA:
  - Complete JSON with all relevant sections
  - Permission evaluation order documented (deny -> ask -> allow)
  - Ecosystem profiles for major platforms (Python, Node, Git, Perforce)
  - Universal deny rules that apply to all environments
  - Hook configuration section with domain examples
  - MCP configuration reference (.mcp.json)
  - Sandbox configuration
  - Industry-specific network allowlists

  WHY THIS EXISTS:
  settings.json controls what Claude can and cannot do. A misconfigured settings
  file either blocks legitimate operations (user frustration) or allows dangerous
  ones (security risk). Getting this right out of the box is critical -- the plan
  identifies "settings.json requires zero manual permission fixes for the common case"
  as a success criterion.

  Permission evaluation order: deny -> ask -> allow. First match wins.
  This means deny rules always take priority over allow rules.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application (Python + Node ecosystem)
============================================================ -->

# Generated settings.json

## Base configuration (all environments)

<!-- BASE CONFIG
  WHY: Every generated environment needs these core permissions.
  Read is broadly allowed (reading files is always safe).
  Write/Edit scoped to Docs/ and .claude/ (environment management).
  Deny rules block universally dangerous operations.
-->

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",

  "permissions": {
    "allow": [
      "Read(./**)",
      "Edit(./Docs/**)",
      "Write(./Docs/**)",
      "Edit(./.claude/**)",
      "Write(./.claude/**)",
      "Edit(./CLAUDE.md)",
      "Write(./CLAUDE.md)",
      "WebSearch",
      "WebFetch(*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./**/*secret*)",
      "Read(./**/*credential*)",
      "Bash(rm -rf /)",
      "Bash(rm -rf ~)",
      "Bash(rm -rf .)",
      "Bash(sudo *)",
      "Bash(chmod 777 *)",
      "Bash(curl * | bash)",
      "Bash(wget * | bash)"
    ]
  }
}
```

## Permission syntax reference

<!-- PERMISSION SYNTAX
  WHY: The component-generator needs to construct permission rules correctly.
  This reference covers all supported patterns with examples.
-->

### Pattern types

| Pattern | Matches | Example |
|---|---|---|
| `Tool` | All uses of that tool | `WebSearch` |
| `Tool(specifier)` | Specific use pattern | `Bash(npm test)` |
| `Tool(path)` | File path (gitignore syntax) | `Read(./.env)` |
| `Tool(domain:X)` | Domain restriction | `WebFetch(domain:example.com)` |
| `Bash(cmd *)` | Wildcard command | `Bash(git diff *)` |
| `mcp__server__tool` | MCP tool | `mcp__github__create_issue` |
| `Task(AgentName)` | Subagent spawning | `Task(debugger)` |

### Evaluation order

1. **Deny** rules evaluated first (highest priority)
2. **Ask** rules evaluated second
3. **Allow** rules evaluated last
4. First matching rule wins
5. If no rule matches, Claude prompts the user

### Path syntax

- `./path` -- relative to project root
- `//path` -- absolute from filesystem root
- `~/path` -- from user home directory
- `*` -- matches one directory level
- `**` -- matches recursively

## Ecosystem permission profiles

<!-- ECOSYSTEM PROFILES
  WHY: Each language/framework ecosystem has its own set of safe commands.
  A Python developer needs pytest, pip, ruff. A Node developer needs npm, vitest.
  Pre-configuring these eliminates permission prompt friction.
-->

### Python ecosystem

```json
{
  "permissions": {
    "allow": [
      "Bash(python *)",
      "Bash(python3 *)",
      "Bash(pytest *)",
      "Bash(mypy *)",
      "Bash(ruff *)",
      "Bash(black *)",
      "Bash(pip list)",
      "Bash(pip show *)",
      "Bash(pip install -r requirements*.txt)",
      "Bash(alembic *)",
      "Bash(uvicorn *)"
    ],
    "deny": [
      "Bash(pip install *)",
      "Bash(pip uninstall *)"
    ]
  }
}
```

Note: `pip install` is denied by default (general installs). Only `pip install -r` is allowed.
This prevents accidental package installation while allowing dependency sync.

### Node.js ecosystem

```json
{
  "permissions": {
    "allow": [
      "Bash(node *)",
      "Bash(npm run *)",
      "Bash(npm test *)",
      "Bash(npm run build *)",
      "Bash(npm run lint *)",
      "Bash(npx *)",
      "Bash(vitest *)",
      "Bash(eslint *)",
      "Bash(prettier *)",
      "Bash(tsc *)"
    ],
    "deny": [
      "Bash(npm install *)",
      "Bash(npm uninstall *)",
      "Bash(npm publish *)"
    ]
  }
}
```

### Git ecosystem

```json
{
  "permissions": {
    "allow": [
      "Bash(git status *)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git branch *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git checkout -b *)",
      "Bash(git stash *)",
      "Bash(git show *)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(git merge *)",
      "Bash(git rebase *)"
    ],
    "deny": [
      "Bash(git push --force *)",
      "Bash(git push -f *)",
      "Bash(git reset --hard *)",
      "Bash(git clean -f *)",
      "Bash(git branch -D *)"
    ]
  }
}
```

### Perforce ecosystem

```json
{
  "permissions": {
    "allow": [
      "Bash(p4 opened *)",
      "Bash(p4 edit *)",
      "Bash(p4 add *)",
      "Bash(p4 reopen *)",
      "Bash(p4 diff *)",
      "Bash(p4 describe *)",
      "Bash(p4 changes *)",
      "Bash(p4 fstat *)",
      "Bash(p4 change *)",
      "Bash(p4 reconcile *)",
      "Bash(p4 sync *)",
      "Bash(p4 info)"
    ],
    "ask": [
      "Bash(p4 revert *)"
    ],
    "deny": [
      "Bash(p4 submit *)",
      "Bash(p4 obliterate *)"
    ]
  }
}
```

## Universal deny rules

<!-- UNIVERSAL DENY
  WHY: These operations are dangerous in ALL environments. They should never
  be auto-approved regardless of domain or permission profile.
-->

Always include these deny rules (merge with ecosystem-specific denies):

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./**/*secret*)",
      "Read(./**/*credential*)",
      "Read(./**/*.pem)",
      "Read(./**/*.key)",
      "Bash(rm -rf /)",
      "Bash(rm -rf ~)",
      "Bash(rm -rf .)",
      "Bash(sudo *)",
      "Bash(chmod 777 *)",
      "Bash(curl * | bash)",
      "Bash(wget * | bash)",
      "Bash(eval *)",
      "Bash(sh -c *)"
    ]
  }
}
```

## Data Processing Permissions

<!-- ANNOTATION: [Python and data tool permissions]
     WHY: Users who work with data files (Excel, CSV, databases) need Python and
     data processing tools. The Knowledge Work profile denies these by default
     because non-technical users should not accidentally run code. The Data & Analysis
     profile enables them because data processing IS the primary work.
     ADAPT: Only include these permissions when GENESIS.md explicitly indicates
     data processing needs. Do not add Python permissions to environments where
     the user has no data processing needs. -->

When the architect detects data processing needs (from GENESIS.md), include:

```json
{
  "permissions": {
    "allow": [
      "Bash(python *)",
      "Bash(python3 *)",
      "Bash(pip install *)",
      "Bash(pip list *)",
      "Bash(pip show *)",
      "Bash(pip freeze *)",
      "Bash(csvtool *)",
      "Bash(jq *)",
      "Bash(sqlite3 *)"
    ],
    "deny": [
      "Bash(pip install --user *)",
      "Bash(python -m pip install --break-system-packages *)"
    ]
  }
}
```

Common Python packages the analyst agent may need (suggest `pip install` in GETTING_STARTED.md):
- `openpyxl` -- reading/writing Excel files
- `pandas` -- data analysis and manipulation
- `numpy` -- numerical computation
- `matplotlib` -- chart generation (saved to files)

Anti-pattern: Do NOT add these permissions to environments where the user never
mentioned data files. Python permissions in a legal-only or writing-only environment
add unnecessary risk surface with no benefit.

## File Processing Tool Configuration

<!-- FILE PROCESSING TOOLS
  WHY: File processing tools (Pattern E) come in multiple flavors. The architect
  selects which tools suit the environment during ARCHITECTURE.md creation. The
  component-generator must include ONLY the permissions matching that selection.
  Including extra tool permissions violates least-privilege and confuses users
  who do not have those tools installed.

  CONDITIONAL: This entire section is conditional. Include nothing from it unless
  ARCHITECTURE.md specifies Pattern E (File Processing Pipeline).
-->

Include ONLY the permissions matching the tools selected by the architect. Do not
grant Python permissions for environments that don't use Python-based tools. The
MCP server approach for MarkItDown avoids needing Bash/Python permissions entirely.

### MarkItDown MCP Server (preferred when possible)

The MCP server gives Claude a native `convert_to_markdown` tool. No Bash permissions
needed for file reading. Configure in `.mcp.json` (not settings.json):

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "uvx",
      "args": ["markitdown-mcp"]
    }
  }
}
```

### MarkItDown CLI permissions (alternative to MCP)

Use when MCP is not suitable for the target environment:

```json
{
  "permissions": {
    "allow": [
      "Bash(markitdown *)",
      "Bash(python -m markitdown *)"
    ]
  }
}
```

### Pandoc permissions (formatted output)

Include only when the architect selects Pandoc for formatted deliverables:

```json
{
  "permissions": {
    "allow": [
      "Bash(pandoc *)"
    ]
  }
}
```

### Python data tools (Data & Analysis pattern)

Include when the environment needs full-fidelity data file manipulation:

```json
{
  "permissions": {
    "allow": [
      "Bash(python *)",
      "Bash(pip install openpyxl)",
      "Bash(pip install pdfplumber)"
    ]
  }
}
```

### PowerShell ImportExcel (Windows environments)

Include when the environment targets Windows and needs Excel manipulation without Python:

```json
{
  "permissions": {
    "allow": [
      "Bash(powershell -Command *ImportExcel*)"
    ]
  }
}
```

Anti-pattern: Do NOT include Pandoc permissions if the architect did not select Pandoc.
Do NOT include Python data tool permissions for environments that don't use Python-based
tools. Prefer the MCP server approach for MarkItDown -- it is the most seamless option
and requires zero Bash permissions.

## Hook configuration

<!-- HOOKS
  WHY: Hooks are deterministic automation that runs at specific lifecycle points.
  Unlike CLAUDE.md instructions (advisory), hooks are guaranteed to execute.
  Domain-specific hooks enforce quality gates without relying on Claude to remember.
-->

Hooks are optional. Include when the intake identifies quality gates or
automation needs. Common patterns:

### Post-edit linting (software development)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{
          "type": "command",
          "command": "ruff check --fix ${CLAUDE_PROJECT_DIR}/src/",
          "timeout": 30,
          "statusMessage": "Running linter..."
        }]
      }
    ]
  }
}
```

### Pre-tool binary asset protection (game development)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{
          "type": "command",
          "command": "bash -c 'echo $TOOL_INPUT | grep -qE \"\\.(uasset|umap|png|jpg|fbx)$\" && echo \"{\\\"hookSpecificOutput\\\":{\\\"hookEventName\\\":\\\"PreToolUse\\\",\\\"permissionDecision\\\":\\\"deny\\\",\\\"permissionDecisionReason\\\":\\\"Binary assets cannot be edited directly\\\"}}\" && exit 2 || exit 0'",
          "statusMessage": "Checking file type..."
        }]
      }
    ]
  }
}
```

### Session start state reminder

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "resume",
        "hooks": [{
          "type": "prompt",
          "prompt": "Check if Docs/_working/state/SESSION_SNAPSHOT.json exists. If it does, suggest the user run /state-load.",
          "timeout": 15
        }]
      }
    ]
  }
}
```

## MCP configuration

<!-- MCP
  WHY: MCP servers connect Claude to external services. The .mcp.json file
  is project-scoped and checked into VCS. Generated environments should
  include MCP configuration when external services were identified in intake.
-->

MCP servers are configured in `.mcp.json` at project root (separate from settings.json):

```json
{
  "mcpServers": {
    "github": {
      "command": "gh",
      "args": ["mcp", "serve"],
      "env": {}
    },
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

When generating MCP configuration:
- Use `${VAR}` for environment variable expansion (never hardcode secrets)
- Include only servers identified during intake
- Skills referencing MCP tools must use fully qualified names: `ServerName:tool_name`

## Sandbox configuration

<!-- SANDBOX
  WHY: Sandboxing provides OS-level isolation for Bash commands. When enabled
  with auto-allow, sandboxed commands run without permission prompts while
  maintaining security boundaries.
-->

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "network": {
      "allowedDomains": [
        "github.com",
        "*.github.com",
        "pypi.org",
        "*.pypi.org",
        "npmjs.org",
        "*.npmjs.org",
        "registry.npmjs.org"
      ]
    }
  }
}
```

## Industry-specific network allowlists

<!-- NETWORK ALLOWLISTS
  WHY: Different domains need access to different external services.
  Pre-configuring the right domains eliminates network permission friction.
-->

| Industry | Additional allowed domains |
|---|---|
| Web development | `cdn.jsdelivr.net`, `unpkg.com`, `fonts.googleapis.com` |
| Data science | `huggingface.co`, `kaggle.com`, `*.amazonaws.com` |
| Game development | `*.unrealengine.com`, `*.unity3d.com` |
| Cloud/DevOps | `*.aws.amazon.com`, `*.googleapis.com`, `*.azure.com` |
| Documentation | `*.readthedocs.io`, `docs.python.org`, `developer.mozilla.org` |

## Environment variables

<!-- ENV VARS
  WHY: Settings.json can set environment variables that affect Claude Code behavior.
  Key variables are configured here rather than relying on system environment.
-->

```json
{
  "env": {
    "CLAUDE_CODE_EFFORT_LEVEL": "high",
    "CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE": "85"
  }
}
```

| Variable | Purpose | Recommended |
|---|---|---|
| `CLAUDE_CODE_EFFORT_LEVEL` | Thinking depth (low/medium/high) | `high` for complex projects |
| `CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE` | Trigger compaction earlier/later | Omit for most projects (default 95 is fine). Use `85` only for very large codebases with heavy context needs. Never go below 80 -- lower values cut sessions too short. |
| `ENABLE_TOOL_SEARCH` | Lazy-load MCP tool definitions | `auto` (default). Set to `true` for environments with 5+ MCP servers to reduce context consumption by up to 95%. |

## Settings file separation

<!-- SETTINGS SEPARATION
  WHY: Machine-specific paths (engine installations, local tool paths) differ
  between developers. Putting them in settings.json causes merge conflicts on
  team projects. settings.local.json is gitignored and holds machine-specific config.
-->

When the environment has machine-specific paths (build tools, engine paths, local
MCP servers), generate both files:

- `settings.json`: Shared team configuration (permissions, deny rules, hooks)
- `settings.local.json`: Machine-specific overrides (absolute paths, local tools)

```json
// settings.local.json (gitignored)
{
  "permissions": {
    "allow": [
      "Bash(\"C:\\Path\\To\\Local\\BuildTool.exe\" *)"
    ]
  }
}
```

Settings are merged: `settings.local.json` overrides `settings.json` for matching keys.
Include `settings.local.json` in `.gitignore` and `.claudeignore`.

Document in GETTING_STARTED.md: "Copy `settings.local.json.example` and update paths
for your machine."

## CI/CD integration (optional)

<!-- CI/CD
  WHY: Projects using GitHub benefit from automated quality gates in CI.
  Claude Code has official GitHub Actions support. When CI/CD is identified
  during intake, suggest setup and optionally generate workflow files.
-->

When the intake identifies GitHub-based CI/CD, suggest:
1. Run `/install-github-app` in Claude Code CLI for automated PR review
2. Optionally generate `.github/workflows/` files:

```yaml
# .github/workflows/quality.yml
name: Quality
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: npm ci  # or pip install, etc.
      - name: Lint
        run: npm run lint
      - name: Type check
        run: npm run typecheck
      - name: Test
        run: npm test -- --coverage
```

Only generate CI workflows when explicitly identified during intake.
Do not generate for projects without CI/CD infrastructure.

## Complete generated example

<!-- COMPLETE EXAMPLE
  WHY: Shows how all sections merge into one final settings.json.
  The component-generator uses this as the target format.
-->

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",

  "env": {
    "CLAUDE_CODE_EFFORT_LEVEL": "high",
    "CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE": "85"
  },

  "permissions": {
    "allow": [
      "Read(./**)",
      "Edit(./Docs/**)",
      "Write(./Docs/**)",
      "Edit(./.claude/**)",
      "Write(./.claude/**)",
      "Edit(./CLAUDE.md)",
      "Write(./CLAUDE.md)",
      "Edit(./src/**)",
      "Write(./src/**)",
      "Edit(./tests/**)",
      "Write(./tests/**)",
      "WebSearch",
      "WebFetch(*)",
      "Bash(python *)",
      "Bash(python3 *)",
      "Bash(pytest *)",
      "Bash(mypy *)",
      "Bash(ruff *)",
      "Bash(npm run *)",
      "Bash(npm test *)",
      "Bash(npx *)",
      "Bash(git status *)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git branch *)",
      "Bash(git checkout -b *)",
      "Bash(git stash *)",
      "Bash(git show *)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(git merge *)",
      "Bash(git rebase *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./**/*secret*)",
      "Read(./**/*credential*)",
      "Read(./**/*.pem)",
      "Read(./**/*.key)",
      "Bash(rm -rf /)",
      "Bash(rm -rf ~)",
      "Bash(rm -rf .)",
      "Bash(sudo *)",
      "Bash(chmod 777 *)",
      "Bash(curl * | bash)",
      "Bash(wget * | bash)",
      "Bash(pip install *)",
      "Bash(npm install *)",
      "Bash(npm publish *)",
      "Bash(git push --force *)",
      "Bash(git push -f *)",
      "Bash(git reset --hard *)",
      "Bash(git clean -f *)",
      "Bash(git branch -D *)"
    ]
  },

  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{
          "type": "command",
          "command": "ruff check --fix ${CLAUDE_PROJECT_DIR}/src/",
          "timeout": 30,
          "statusMessage": "Running linter..."
        }]
      }
    ]
  }
}
```

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Python + Node ecosystem permissions merged
  - Git VCS permissions with push in "ask"
  - Post-edit linting hook

  KNOWLEDGE WORK:
  - Minimal Bash permissions (basic file operations only)
  - No VCS permissions (or minimal git)
  - Broad Read/Write for document directories
  - No hooks typically needed
  - Network: allow research databases, academic sources

  GAME DEVELOPMENT:
  - Perforce ecosystem permissions (no git)
  - Binary asset protection hook (PreToolUse deny for .uasset/.umap)
  - Build system permissions (UnrealBuildTool, editor commands)
  - Network: game engine CDN, asset stores

  CONSERVATIVE DOMAINS:
  - Very restrictive Bash permissions (only explicitly listed commands)
  - Network: only pre-approved domains
  - Additional deny: any external write operations
  - Hooks: audit trail for all tool uses
-->

<!-- ANTI-PATTERNS

  1. NO DENY RULES
     Problem: Claude can read .env files, run sudo, force-push.
     Fix: Always include universal deny rules. They are non-negotiable.

  2. OVERLY RESTRICTIVE ALLOW
     Problem: User prompted for every file read, every test run.
     Fix: Pre-allow common safe operations for the project's ecosystem.

  3. HARDCODED SECRETS IN MCP CONFIG
     Problem: Database URL or API key directly in .mcp.json.
     Fix: Use ${VAR} for environment variable expansion.

  4. ALLOW * WITHOUT DENY
     Problem: Everything permitted, no safety boundaries.
     Fix: deny -> ask -> allow order. Deny rules always take priority.

  5. MISSING ECOSYSTEM PERMISSIONS
     Problem: Python project but no pytest/mypy/ruff in allow list.
     Fix: Select ecosystem profile based on intake answers.

  6. PIP INSTALL / NPM INSTALL ALLOWED
     Problem: Claude installs arbitrary packages, potentially compromising environment.
     Fix: Deny general install, allow only from requirements/package files.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Valid JSON (parseable)
  [ ] $schema reference included
  [ ] Universal deny rules present (secrets, rm -rf, sudo, curl|bash)
  [ ] Ecosystem-specific permissions included for identified languages
  [ ] VCS permissions appropriate to project VCS
  [ ] Permission evaluation order documented (deny -> ask -> allow)
  [ ] No hardcoded secrets in any configuration
  [ ] Hook configuration relevant to domain (if hooks generated)
  [ ] MCP configuration uses ${VAR} for secrets (if MCP generated)
  [ ] Sandbox configuration included
  [ ] Network allowlist relevant to domain
  [ ] Environment variables section with effort level
  [ ] Complete merged example provided
  [ ] Source directories (src/, tests/) in allow list
  [ ] Docs/ and .claude/ in allow list
  [ ] CLAUDE.md in allow list
  [ ] ASCII-only
-->

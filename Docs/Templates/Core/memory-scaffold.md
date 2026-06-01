# Template: Memory Scaffold

<!-- TEMPLATE ANNOTATION
  This template defines the dual-purpose memory system for generated environments.
  Memory serves two audiences simultaneously:
  1. Claude's on-demand knowledge base (loaded just-in-time per task)
  2. Human-readable project wiki (browsable locally or via GitHub Pages)

  The key insight: a developer wanting to understand "how does the combat system
  work" needs the same information Claude needs. One artifact serves both.

  QUALITY CRITERIA:
  - Three tiers defined (Lite/Standard/Enterprise) with selection criteria
  - index.md always loaded (primary navigation / wiki home page)
  - Just-in-time retrieval with depth-aware reading
  - Documentation-quality content (not machine-oriented stubs)
  - Working memory separated from publishable wiki content
  - GitHub Pages compatible structure
  - Metadata signaling conventions
  - Staleness detection rules
  - Auto-memory integration note

  WHY THIS EXISTS:
  Memory bridges sessions AND bridges team members. Without it, every session
  starts from scratch and every new developer reads code blind. The dual-purpose
  approach means the documentation stays current because Claude updates it as
  part of normal work -- not as a separate documentation task that gets neglected.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application (Standard tier)
============================================================ -->

# Memory structure

<!-- CORE PRINCIPLES
  WHY: These principles prevent memory from becoming stale, bloated, or
  useful to Claude but useless to humans (or vice versa).
-->

## Principles

1. **index.md is always loaded**. It is the wiki home page and Claude's
   table of contents. Keep it under 50 lines.
2. **Everything else loads on demand**. Agents read specific pages when
   needed, not the entire wiki.
3. **Depth-aware retrieval**: Area pages have a summary at the top (quick
   context) and detailed sections below (deep work). Claude reads the
   depth appropriate to the task.
4. **Dual-purpose content**: Every page must be useful to both Claude and
   a human developer. Write documentation-quality prose, not machine stubs.
5. **Working memory is separate**: Session state, friction logs, and
   transient data live in `Docs/_working/` (excluded from wiki publishing).
6. **Staleness detection**: Every document has "Last Updated" and optionally
   "Last Verified" dates.

## Directory structure

The wiki (publishable content) and working memory (transient state) are
separated at the directory level:

```
Docs/                           # Wiki root (publishable via GitHub Pages)
  index.md                      # Home page / table of contents (always loaded)
  overview.md                   # Project overview, architecture, team
  GETTING_STARTED.md            # Onboarding guide
  Areas/                        # Subsystem documentation
    api.md
    frontend.md
    database.md
  Decisions/                    # Architectural Decision Records
    001-streaming-exports.md
  Symbols/                      # Key class/component reference (optional)
    UserService.md
  Environment/                  # Generator metadata (optional to publish)
    GENESIS.md
    ARCHITECTURE.md
    VERSION.md

Docs/_working/                  # Working memory (NOT published)
  state/                        # Session snapshots, build status
    SESSION_SNAPSHOT.json
    SESSION_CONTEXT.md
  sessions/                     # Session history (auto-pruned after 30 days)
    2026-02-14.md
  retro/                        # Self-learning friction logs
    2026-02.md
```

The `_working/` prefix ensures Jekyll (GitHub Pages) ignores this directory
by default. Working memory is useful to Claude but not to wiki readers.

**VCS exclusion (REQUIRED):** `Docs/_working/` MUST be excluded from version
control so each developer has independent working state. The component-generator
adds this to `.gitignore` (or `.p4ignore` for Perforce projects) automatically.
Without this, working state from one developer bleeds into another's sessions.

**Session segmentation (optional):** For users running parallel Claude Code
sessions, state files can be segmented by session:
- Default: `_working/state/SESSION_SNAPSHOT.json` (single file, latest wins)
- Segmented: `_working/state/<session-slug>/SESSION_SNAPSHOT.json` (per-session)

Use segmented when GENESIS.md indicates parallel sessions or team usage.

## Tier selection

<!-- TIER SELECTION
  WHY: One-size-fits-all memory serves nobody. A solo developer's side project
  needs a single file. A 20-person team needs area indexes, decision records,
  and team-specific context.
-->

| Criteria | Lite | Standard | Enterprise |
|---|---|---|---|
| Team size | Solo or 1-2 casual | 1-5 people | 6+ people |
| Project complexity | Small, single-focus | Medium, multi-area | Large, multi-team |
| Session frequency | Occasional | Regular (daily/weekly) | Continuous |
| Decision tracking | Informal | Important decisions | Formal ADR process |
| Recommended for | Side projects, scripts, small tools | Most software projects | Large codebases, regulated industries |

## Tier: Lite

```
Docs/
  index.md              # Home page + project context (always loaded)
  GETTING_STARTED.md    # Onboarding
Docs/_working/
  state/                # Session state
  retro/                # Friction logs
```

### index.md (Lite)

```markdown
# Project Name

> One-sentence project description.

Last Updated: 2026-02-14

## Overview

[2-3 paragraphs: what the project does, how it is built, key conventions]

## Architecture

[Key components and how they connect]

## Quick Reference

| Item | Value |
|------|-------|
| Language | Python 3.11 + TypeScript 5 |
| Framework | FastAPI + React |
| Database | PostgreSQL 15 |
| Test runner | pytest + vitest |
| Build | `npm run build` (frontend) |

## Conventions

[Coding standards, naming conventions, patterns used]

## Common Tasks

[How to build, test, deploy -- step by step]

## Gotchas

[Non-obvious behaviors, known issues, workarounds]
```

For Lite tier, index.md contains everything. It serves as both the wiki home
page and the complete project context. Upgrade to Standard when this file
exceeds 100 lines.

## Tier: Standard

```
Docs/
  index.md              # Home page (always loaded)
  overview.md           # Project overview, architecture, team
  GETTING_STARTED.md    # Onboarding
  Areas/                # Subsystem documentation
    api.md
    frontend.md
    database.md
  Decisions/            # Architectural decisions
    001-streaming-exports.md
  Symbols/              # Key class reference (optional, on demand)
Docs/_working/
  state/
  sessions/
  retro/
```

### index.md (Standard)

```markdown
# Project Name

> One-sentence project description.

Status: NEW_ENVIRONMENT
Last Updated: 2026-02-14

## Project

- [Overview](overview.md) -- Architecture, team structure, conventions

## Areas

- [REST API](Areas/api.md) -- FastAPI routes, middleware, authentication
- [Frontend](Areas/frontend.md) -- React components, state management, routing
- [Database](Areas/database.md) -- PostgreSQL schema, migrations, query patterns

## Decisions

- [001: Streaming CSV exports](Decisions/001-streaming-exports.md) -- 2026-02-14

## Quick Reference

| Item | Value |
|------|-------|
| Language | Python 3.11 + TypeScript 5 |
| Framework | FastAPI + React |
| Database | PostgreSQL 15 |
| Test | pytest (backend), vitest (frontend) |
| Build | `npm run build` (frontend) |
```

### Area document format (depth-aware)

Area pages use progressive disclosure. The top sections give quick context
(for both a skimming developer and Claude doing a quick lookup). The lower
sections provide depth (for a developer learning the system or Claude
working in this area).

```markdown
# REST API

> FastAPI-based REST API serving the React frontend. Handles authentication,
> CRUD operations, and data export. All routes are under `/api/v1/`.

Last Updated: 2026-02-14
Last Verified: 2026-02-14

## Overview

The API layer is built with FastAPI and uses SQLAlchemy for database access.
Authentication uses JWT tokens issued by the `/auth/login` endpoint. All
endpoints require authentication except `/auth/login` and `/health`.

Response format is standardized: `{"data": ..., "meta": {"page": 1, "total": 100}}`.

## Key Files

| File | Purpose |
|------|---------|
| src/api/customers.py | Customer CRUD endpoints |
| src/api/export.py | CSV export endpoint (streaming) |
| src/middleware/auth.py | JWT authentication middleware |
| src/api/deps.py | Shared dependencies (DB session, current user) |

## Architecture

Request flow: Client -> Auth middleware -> Route handler -> Service -> Repository -> DB

The service layer contains business logic. Route handlers only parse requests
and format responses. Repositories handle database queries.

## Patterns and Conventions

- Route files grouped by resource (`customers.py`, `orders.py`, not by HTTP method)
- Every endpoint returns a standard response envelope
- Pagination uses cursor-based pagination (not offset)
- Errors raise HTTPException with structured detail

## Integration Points

- **Frontend** calls all `/api/v1/` endpoints via Axios client
- **Database** accessed through SQLAlchemy async sessions
- **Export** uses StreamingResponse for large CSV downloads (see Decision 001)

## Gotchas

- The auth middleware skips OPTIONS requests (CORS preflight) -- do not add
  auth checks to CORS middleware
- Export endpoint streams data; Content-Length header is not set
- Customer soft-delete: `is_active=False`, not actual row deletion
```

**Depth-aware retrieval for Claude**: When the task only needs to know what
the API area covers, read the Summary and Overview sections (first ~10 lines).
When working in this area, read the full page. When debugging a specific issue,
also read related area pages via Integration Points.

### Decision document format

```markdown
# Decision: Use streaming response for CSV exports

Date: 2026-02-14
Status: Accepted
Context: Export endpoint needs to handle datasets with 100K+ rows

## Problem

Large CSV exports cause memory issues when loaded fully into memory.

## Decision

Use FastAPI StreamingResponse with chunked CSV generation.

## Alternatives Considered

- Load all data into memory: rejected (OOM risk on large datasets)
- Background job with file download: deferred (adds complexity, not needed yet)

## Consequences

- Exports work for any dataset size
- Cannot add headers like Content-Length (unknown until complete)
- Client must handle streaming download
```

### Symbol page format (optional)

Symbol pages provide reference documentation for key classes, functions, or
components. They are populated on demand when Claude explores the codebase.

```markdown
# UserService

> Core service handling user CRUD operations, authentication, and profile management.

Last Updated: 2026-02-14
Defined in: `src/services/user_service.py`
Inherits from: `BaseService`

## Public Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| get_by_id | user_id: UUID | User | Fetch user by primary key |
| create | data: UserCreate | User | Create new user with hashed password |
| authenticate | email, password | User or None | Validate credentials |
| update_profile | user_id, data | User | Update non-auth fields |

## Usage Patterns

Called by API route handlers via dependency injection. Never called directly
from other services -- use events for cross-service communication.

## Dependencies

- `PasswordHasher` for credential hashing
- `UserRepository` for database access
- `EventBus` for publishing user lifecycle events
```

## Tier: Enterprise

```
Docs/
  index.md
  overview.md
  GETTING_STARTED.md
  Areas/
    api/
      index.md          # Sub-index for this area
      overview.md
      auth.md
      export.md
    frontend/
      index.md
      overview.md
      components.md
    database/
      index.md
      schema.md
      migrations.md
  Decisions/
    001-streaming-exports.md
    002-auth-strategy.md
  Symbols/
    UserService.md
    OrderService.md
  Teams/                # Team-specific context
    backend/
      conventions.md
    frontend/
      conventions.md
Docs/_working/
  state/
  sessions/
  retro/
```

Enterprise tier uses sub-directories within Areas/ so that each major
subsystem has its own index and multiple detail pages. This prevents
individual area files from growing past 300 lines.

## GitHub Pages integration

The `Docs/` directory is designed to work as a GitHub Pages source:

1. All links use relative Markdown links (work in both raw and rendered)
2. `index.md` in each directory serves as the landing page
3. `_working/` directory is automatically excluded by Jekyll
4. No special configuration required for basic rendering

Optional: add a `Docs/_config.yml` for enhanced rendering:

```yaml
title: "Project Name"
description: "Project documentation and knowledge base"
theme: just-the-docs
nav_order: 1
```

If the team does not use GitHub Pages, the wiki is still useful -- any
developer can browse the Markdown files locally or in their IDE.

## Content quality standards

When Claude populates area pages (through exploration, implementation, or
debugging), it must write documentation-quality content:

- **Complete sentences**, not just tables of file paths
- **Explain WHY patterns exist**, not just what they are
- **Include context a new developer needs** to understand the system
- **Use domain vocabulary** naturally (the wiki teaches project concepts)
- **Keep summaries concise** but detailed sections thorough
- **Update existing pages** rather than creating new ones when possible

Bad (machine-oriented):
```
## Key Files
| (needs codebase scan) | |

## Patterns
(Populate after codebase scan)
```

Good (documentation-quality):
```
## Key Files
| File | Purpose |
|------|---------|
| Source/Combat/Abilities/GA_MeleeAttack.h | Base melee ability with combo support |
| Source/Combat/Effects/GE_Damage.h | Standard damage gameplay effect |

## Patterns
Abilities follow a naming convention: `GA_` prefix for gameplay abilities,
`GE_` for gameplay effects, `AS_` for attribute sets. Each ability has a
matching gameplay cue with the `GC_` prefix for visual/audio feedback.
```

## Metadata signaling

Conventions for all tiers:
- File names use domain vocabulary (`api.md`, not `area-1.md`)
- Every page starts with a blockquote summary (one sentence)
- Every document includes `Last Updated: YYYY-MM-DD`
- Optional: `Last Verified: YYYY-MM-DD` (separate from Last Updated)
- Optional: `Confidence: High | Medium | Low`
- `Status: NEW_ENVIRONMENT` on index.md until first codebase scan

## Staleness detection

A document is considered stale when:
- `Last Updated` is more than 30 days ago AND the area has active changes
- `Confidence` is `Low` (needs verification before relying on it)
- The file paths listed in the document no longer exist

When staleness is detected:
- Flag it in `/health-check` output
- Suggest updating during the next relevant task (do not update speculatively)
- On update, write documentation-quality content (not placeholder stubs)

## Auto-memory integration

Claude Code maintains automatic memory at `~/.claude/projects/<project>/memory/`.
This is separate from the wiki:

| Feature | Docs/ wiki | Auto-memory |
|---|---|---|
| Shared with team | Yes (via VCS) | No (local to user) |
| Structure | Defined by this environment | Claude's automatic notes |
| Loaded by default | index.md only | First 200 lines of MEMORY.md |
| Purpose | Team knowledge base + wiki | Personal preferences and learnings |
| Managed by | /state-save, /update, agents | Claude automatically |

Both systems complement each other. The wiki is the team knowledge base.
Auto-memory is personal preferences. Do not duplicate information between them.

## Working memory details

Working memory lives in `Docs/_working/` and contains transient data:

### state/ directory
- `SESSION_SNAPSHOT.json` -- programmatic state (6-category taxonomy)
- `SESSION_CONTEXT.md` -- human-readable session summary
- `build-status.json` -- last build result and timestamp
- Other tool-specific state files

### sessions/ directory
- One file per session with summary and key findings
- Auto-pruned after 30 days
- Before pruning, extract lasting value into wiki pages

### retro/ directory
- Monthly friction logs for self-learning
- Entries feed the `/update` skill's improvement analysis

Session auto-pruning: sessions older than 30 days are flagged for cleanup
during `/health-check` or `/update`. Extract lasting decisions or area
updates into wiki pages before removing session files.

## Multi-Entity Variant

<!-- ANNOTATION: [Multi-entity memory structure]
     ADAPT: Replace "Entities" with domain-appropriate terminology -->

Use this variant when GENESIS.md describes repeatable workflows across
independent entities.

Structure:
```
Docs/
  index.md
  overview.md
  Areas/
    entity-tracker.md           # Master list of all entities
    methodology-notes.md        # Shared methodology
  Entities/                     # Per-entity isolation
    <EntityName>/
      overview.md
      deliverables.md
      notes/
  Templates/                    # Reusable document templates
    engagement-template.md
  Decisions/
Docs/_working/
  state/
  sessions/
  retro/
```

Anti-patterns:
- Do NOT put all entity data in a single file
- Do NOT use the entity tracker for detailed notes
- Do NOT load multiple entity folders simultaneously

## Inbox/Outbox/Data Scaffolding

Use this variant when ARCHITECTURE.md includes Pattern E (File Processing
Pipeline).

Structure:
```
<project>/
  Inbox/
    README.md
  Outbox/
    README.md
  Data/
    README.md
```

### Inbox/README.md

```markdown
# Inbox

Drop files here for processing. Supported formats depend on your
environment's tool configuration.

Common formats: .xlsx, .docx, .pdf, .csv, .json, .pptx, .html, .txt

## How to use
1. Place your file(s) in this folder
2. Tell your assistant what you want
3. Results will appear in the Outbox/ folder
```

### Outbox/README.md

```markdown
# Outbox

Your assistant places processed results here.
```

### Data/README.md

```markdown
# Data

Working data files managed by your assistant. Includes intermediate
processing results, reference data, and converted file formats.
```

Anti-patterns:
- Do NOT generate Inbox/Outbox/Data directories for environments without Pattern E
- Do NOT store final deliverables in Data/ (those go in Outbox/)

## Brand Assets Scaffolding

Use this variant when Pattern E is active AND intake flagged brand requirements.

Structure:
```
Brand/
  Templates/
    README.md
  Guidelines/
    README.md
  brand-rules.md
  README.md
```

See brand-related README content in the architect agent's Pattern E
specification. Anti-patterns:
- Do NOT generate Brand/ if intake did not flag brand requirements
- Do NOT pre-populate brand-rules.md with placeholder content
- Brand/Templates/ should start empty (user provides their own templates)

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Areas map to code areas (API, frontend, database, infrastructure)
  - Decisions are architectural (ADR-style)
  - Symbols for key services and components

  KNOWLEDGE WORK:
  - Areas map to topics or projects (not code areas)
  - Decisions track research conclusions and methodology choices
  - Lite tier usually sufficient (solo researcher)

  GAME DEVELOPMENT:
  - Areas map to game systems (combat, UI, networking, AI)
  - Decisions include gameplay design and replication strategy choices
  - Symbols for key gameplay classes (character, abilities, weapons)
  - Standard or Enterprise tier (game codebases are large)

  CONSERVATIVE DOMAINS:
  - Enterprise tier recommended even for small teams (audit requirements)
  - Decisions include compliance justification
-->

<!-- ANTI-PATTERNS

  1. LOADING ALL MEMORY AT SESSION START
     Problem: Entire wiki loaded into context. Uses 30%+ of context window.
     Fix: Load index.md only. Load specific pages on demand.

  2. ONE GIANT FILE
     Problem: Everything in a single file. File grows to 500+ lines.
     Fix: Split into areas when file exceeds 100 lines. Upgrade to Standard.

  3. MACHINE-ORIENTED STUBS
     Problem: Area pages say "(needs codebase scan)" -- useless to humans.
     Fix: Write documentation-quality content from the start. If the area
     has not been explored yet, write what is known from intake/architecture
     and mark Confidence: Low. Never leave empty placeholders.

  4. STALE DOCUMENTS WITHOUT SIGNALS
     Problem: Area doc from 6 months ago. Agent relies on outdated info.
     Fix: Last Updated field. Staleness detection in /health-check.

  5. MIXING WIKI AND WORKING MEMORY
     Problem: Session snapshots and friction logs published to wiki.
     Fix: Working memory in Docs/_working/ (excluded from publishing).

  6. DUPLICATING AUTO-MEMORY
     Problem: Same preferences stored in wiki and auto-memory.
     Fix: Wiki = team knowledge. Auto-memory = personal.

  7. NEVER PRUNING SESSIONS
     Problem: Sessions directory grows indefinitely.
     Fix: Auto-prune after 30 days. Extract lasting value first.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Three tiers defined with selection criteria
  [ ] index.md format specified for each tier
  [ ] index.md includes Status marker (NEW_ENVIRONMENT / ACTIVE)
  [ ] index.md under 50 lines
  [ ] Depth-aware area document format with progressive disclosure
  [ ] Content quality standards documented (no machine stubs)
  [ ] Working memory separated into Docs/_working/
  [ ] GitHub Pages compatibility noted
  [ ] Decision document format (ADR-style)
  [ ] Symbol page format (optional)
  [ ] Metadata conventions (Last Updated, Confidence)
  [ ] Staleness detection rules
  [ ] Auto-memory integration explanation
  [ ] Session auto-pruning rules
  [ ] Quick Reference section in index.md
  [ ] ASCII-only
-->

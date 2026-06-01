# Template: Memory Management Rule (05-memory-management.md)

<!-- TEMPLATE ANNOTATION
  This template defines how the generated environment manages persistent knowledge
  published in Docs/ (the wiki). The wiki is the environment's long-term knowledge --
  research findings, project context, decisions, and session artifacts. Without
  disciplined memory management, either the context window is flooded with stale
  data or agents repeatedly rediscover the same information.

  QUALITY CRITERIA:
  - Under 120 lines in generated output
  - index.md as sole default load (explicit)
  - On-demand retrieval protocol with examples
  - Staleness detection triggers enumerated
  - Cross-linking conventions specified
  - Auto-memory integration path (self-learning -> persistent memory)
  - Size limits per memory file
  - Pruning/archival rules for _working/sessions/

  WHY THIS EXISTS:
  The wiki directory can grow indefinitely. Without management rules, agents
  either load everything into context (exhausting it) or ignore the wiki entirely
  (rediscovering things). This rule ensures knowledge is accessed efficiently,
  stays current, and self-maintains.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application
============================================================ -->

# Memory management

<!-- CORE PRINCIPLE
  WHY: Establishes the mental model that the wiki is a disk-backed knowledge
  store, not something to load wholesale into the context window.
-->
Persistent knowledge is published in `Docs/` (the wiki). It is accessed on demand, not bulk-loaded.

## Default load rule

<!-- DEFAULT LOAD
  WHY: Loading all wiki files at session start wastes context on content that
  may be irrelevant to the current task. index.md is small and tells you where
  to look. This is the single most important rule in this file.
-->
At session start, load ONLY:
- `Docs/index.md`

Do NOT load other wiki files until a specific need arises. index.md contains
the table of contents with one-line summaries. Use it to decide which files
to read for the current task.

## On-demand retrieval protocol

<!-- ON-DEMAND RETRIEVAL
  WHY: Agents need a clear protocol for when and how to access wiki knowledge.
  Without this, they either read everything (context waste) or nothing
  (knowledge loss). The protocol gives a decision tree.
-->
When you need information from the wiki:

1. Check index.md for relevant entries
2. Read ONLY the specific file(s) that match the current need
3. If a file is large (>200 lines), read only the relevant section
4. After using the information, do not keep the file contents in working memory --
   trust that you can re-read it if needed

Examples of correct retrieval:
- Need API conventions? Read `Docs/Areas/api-conventions.md` only
- Need a past decision rationale? Read the specific `Docs/Decisions/YYYY-MM-DD_*.md` file
- Starting a new task? Read index.md, then the relevant Area file, nothing else

## Staleness detection

<!-- STALENESS DETECTION
  WHY: Stale knowledge is worse than no knowledge -- it gives confident wrong answers.
  These triggers ensure wiki content stays current without requiring manual audits.
-->
A wiki entry is likely stale when:

| Trigger | Action |
|---|---|
| Referenced file paths no longer exist | Update or archive the entry |
| Described behavior contradicts current code | Update the entry with current facts |
| Entry older than 90 days with no recent reference | Flag in index.md as "needs review" |
| User corrects information that originated from the wiki | Update immediately |
| A session discovers facts that contradict an entry | Update immediately |

When updating a stale entry, add a "Last Verified" date at the top.

## Cross-linking conventions

<!-- CROSS-LINKING
  WHY: Wiki entries that reference each other create a navigable knowledge
  graph. Without conventions, links break or become circular dead ends.
-->
When one wiki entry references another:

- Use relative paths: `[API conventions](Areas/api-conventions.md)`
- Link to the file, not a section (sections change more often than files)
- If a referenced file does not exist yet, create a stub with a one-line summary
  and mark it `Status: Stub` at the top
- When creating a new entry, check index.md for related entries and add
  cross-links in both directions

## Auto-memory integration

<!-- AUTO-MEMORY
  WHY: The self-learning system (03-self-learning.md) discovers patterns and
  corrections. Some of these should become persistent memory rather than
  remaining only in retro logs. This defines the promotion path.
-->
When the self-learning system identifies a pattern that represents durable
project knowledge (not just a friction observation):

1. Create or update the appropriate wiki file in `Docs/Areas/` or `Docs/Decisions/`
2. Add the entry to index.md
3. Reference the originating retro entry for traceability

Promotion criteria:
- CORRECTION entries that establish a project convention -> `Docs/Areas/` file
- PATTERN entries about project structure or behavior -> `Docs/Areas/` file
- Decisions made during implementation -> `Docs/Decisions/` file
- One-off facts that do not generalize -> do NOT promote (leave in retro)

## Size limits

<!-- SIZE LIMITS
  WHY: Large wiki files defeat the purpose of on-demand retrieval.
  If a file is too large to skim, it needs to be split.
-->

| File type | Max size | Action when exceeded |
|---|---|---|
| index.md | 100 lines | Split into sub-indexes by category |
| Areas/ files | 200 lines | Split into sub-topic files |
| Decisions/ files | 50 lines | Keep decisions concise; move context to Areas/ |
| _working/sessions/ files | 150 lines | Summarize, then auto-prune after 30 days |

## Session file lifecycle

<!-- SESSION LIFECYCLE
  WHY: _working/sessions/ accumulates working files that are valuable short-term but
  become noise long-term. Auto-pruning keeps the directory manageable.
-->
- New session files are created in `Docs/_working/sessions/YYYY-MM-DD_<slug>.md`
- Scripts and working artifacts go in `Docs/_working/sessions/YYYY-MM-DD_<slug>/`
- After 30 days, session files are auto-pruned during `/health-check`
- Before pruning, any durable findings must be promoted to `Docs/Areas/` or `Docs/Decisions/`
- `/health-check` warns about sessions approaching the 30-day mark that contain
  un-promoted findings

## index.md format

<!-- INDEX FORMAT
  WHY: A consistent index format makes it machine-readable and skimmable.
-->
Each index.md entry follows this format:
```
- [<title>](<relative-path>) -- <one-line summary> (Updated: YYYY-MM-DD)
```

Group entries by category (Areas, Decisions, _working/sessions). Mark stale entries
with `(NEEDS REVIEW)` suffix.

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Areas: api-conventions, architecture, testing-strategy, deployment
  - Sessions: implementation notes, debugging sessions, refactor plans
  - Staleness: code-path references can be validated automatically

  KNOWLEDGE WORK:
  - Areas: research-topics, document-inventory, style-guide, output-styles
  - Sessions: drafting sessions, research sessions
  - Staleness: check if cited sources have been updated/retracted
  - Longer retention for _working/sessions/ (60 days -- research builds over time)

  DATA ANALYSIS:
  - Areas: data-inventory, methodology-notes, output-inventory, output-styles
  - Sessions: analysis scripts, intermediate datasets
  - Staleness: check if source data files have been updated (modified date)
  - Script files in _working/sessions/ may need indefinite retention for reproducibility

  GAME DEVELOPMENT:
  - Areas: system maps, replication notes, gameplay parameters
  - Sessions: playtest results, debug sessions, build notes
  - Higher size limits for Areas/ (300 lines -- game systems are complex)
-->

<!-- ANTI-PATTERNS

  1. LOAD ALL MEMORY AT SESSION START
     Problem: Context exhausted before any real work begins.
     Fix: Load ONLY index.md. Retrieve specific files on demand.

  2. NEVER READING MEMORY
     Problem: Same research repeated every session. Decisions re-debated.
     Fix: On-demand retrieval protocol. Check index.md before doing new work.

  3. MEMORY FILES THAT GROW FOREVER
     Problem: A single Areas/ file becomes 500+ lines, too large to skim.
     Fix: Size limits with mandatory split when exceeded.

  4. NO STALENESS DETECTION
     Problem: Memory says "the API uses JWT auth" but it was changed to OAuth.
     Fix: Staleness triggers check against current reality.

  5. SESSIONS/ NEVER PRUNED
     Problem: 200+ session files from months ago clutter the directory.
     Fix: Auto-prune after 30 days with promotion check.

  6. CROSS-LINKS TO NONEXISTENT FILES
     Problem: Entry references a file that was renamed or deleted.
     Fix: Create stubs for forward references. /health-check validates links.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 120 lines in generated output
  [ ] index.md identified as sole default load
  [ ] On-demand retrieval protocol with decision tree
  [ ] Staleness detection triggers table (4+ triggers)
  [ ] Cross-linking conventions with relative path format
  [ ] Auto-memory integration path from self-learning
  [ ] Promotion criteria (what gets promoted, what does not)
  [ ] Size limits table with actions when exceeded
  [ ] Session file lifecycle with pruning rules
  [ ] index.md format specified
  [ ] References /health-check for maintenance
  [ ] ASCII-only
-->

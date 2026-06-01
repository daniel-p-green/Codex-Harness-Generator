# Template: Generated HUB_GENESIS.md

<!-- TEMPLATE ANNOTATION
  Written by the orchestrator at the end of hub intake, immutable after
  intake completes. Captures shared basics that apply to every work area
  and the registry of areas themselves.

  HUB_GENESIS.md lives at `<target>/Docs/Environment/HUB_GENESIS.md`.
  Each work area additionally has its own GENESIS.md at
  `<target>/<area-slug>/Docs/Environment/GENESIS.md` with that area's
  profile, domain, and customization answers.

  QUALITY CRITERIA:
  - Only include content that applies to every work area. Per-area
    specifics (domain, tools, workflows) belong in per-area GENESIS.md.
  - Work-area registry must be exhaustive -- every subfolder the user
    wants Claude to treat as a separate area is listed here.
  - HUB_STATUS must be COMPLETE before architect runs. INCOMPLETE halts
    the pipeline.
  - ASCII-only throughout.
-->

# Hub Genesis

HUB_STATUS: COMPLETE
Created: YYYY-MM-DD
Hub vocabulary: "work area" (user-facing); "area" or "area-slug" (internal)

## Shared Basics

<!-- Experience level calibrates doc depth and agent count for every area.
     A mixed team should record the lowest experience level represented. -->

Experience level: <beginner | intermediate | advanced>

<!-- Autonomy defaults. Per-area GENESIS.md may override for that area. -->

Autonomy posture: <proactive | conservative>
Human approval required for: <list, or "none">

<!-- Team shape. If solo, areas inherit solo. If team, per-area GENESIS.md
     specifies whether that area is worked on by the whole team or a subset. -->

Team shape: <solo | small-team | multi-role-team>
Team size: <N or "not specified">

<!-- Shared tools are tools every area uses. Area-specific tools belong
     in per-area GENESIS.md. Common shared items: VCS, a chat platform,
     a PKM tool, a language runtime everybody relies on. -->

Shared tools:
- VCS: <git | perforce | none>
- Shared runtime/language: <e.g., Python 3.12 used across areas>
- Shared PKM: <Obsidian vault path | Notion workspace | none>
- Shared CI/CD: <e.g., GitHub Actions config reused across areas>

Shared AI ecosystem:
- Local model(s): <Ollama models, or "none">
- Shared MCP servers: <list with server names and purposes>
- Shared API providers: <e.g., "Anthropic API for all areas">

Token cost priority: <cost-conscious | balanced | quality-first>

## Work Area Registry

<!-- Every subfolder the user wants Claude to treat as a separate area.
     Slug rules: lowercase, hyphen-separated, matches the directory name
     under <target>/. One-line description is what surfaces in the parent
     CLAUDE.md "Work areas in this setup" section. -->

| Area slug | Display name | One-line description | Profile | Folder |
|---|---|---|---|---|
| policy | Policy Framework | Governance policy drafting and stakeholder review | knowledge-work | `<target>/policy/` |
| training | Training Curriculum | Employee training content and quizzes | knowledge-work | `<target>/training/` |
| audit-tool | Compliance Audit Tool | Python CLI that audits config against policy | software-development | `<target>/audit-tool/` |

## Cross-Area Interactions

<!-- How often do the areas touch each other? Informs the parent routing table.
     Options: isolated (never cross), occasional (reference one area from another),
     tightly-coupled (shared artifacts, frequent switching). -->

Cross-area interaction level: <isolated | occasional | tightly-coupled>
Shared artifacts (if any): <e.g., "policy doc outputs feed training content">

## Constraints Applying To All Areas

<!-- Compliance requirements, regulatory concerns, data classifications
     that apply everywhere. Per-area specifics go in per-area GENESIS.md. -->

Sensitive data: <yes (with type) | no>
Compliance regime: <e.g., SOC2, HIPAA, GDPR, or "none">
Hard rules (all areas must follow): <list>

## Pending Questions

<!-- Populated by orchestrator during multi-round intake. Empty when
     HUB_STATUS is COMPLETE. -->

(none)

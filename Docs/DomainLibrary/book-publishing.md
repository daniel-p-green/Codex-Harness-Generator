# Bundled Domain: E-Book Publishing

Adapted from revfactory/harness-100 11-book-publishing. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim) -- a starting point the architect adapts; it points at templates, it
does not inline them.

## Profile Metadata

- **Target audience**: self-publishing authors, indie presses, and editors
  producing e-book deliverables (edited manuscript, proofread report, cover
  concept, metadata/distribution package, release QA)
- **Out of scope**: EPUB/PDF file conversion, store-account registration,
  print/POD ordering, and marketing execution. This domain prepares the
  deliverables and the metadata/distribution package; the author runs the
  actual upload, conversion, and promotion
- **Primary tools**: Markdown manuscripts, an image-generation tool for covers,
  web search for classification/convention/keyword lookups
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: proactive | **VCS**: Git (optional -- manuscripts are documents, not code)

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| manuscript-editor | high-effort | Developmental + line editing: structure, flow, pacing, ToC design, author-voice preservation; never introduces a new factual claim, named source, statistic, quote, or case study during rewrite (flag for author verification); builds a continuity ledger for fiction | drafter.md |
| proofreader | medium-effort | Spelling/grammar/punctuation correction and notation standardization (original -> corrected); notation baseline re-grounded to the target language/house style (see Customization) | reviewer.md |
| cover-designer | medium-effort | Cover concept, typography/color strategy, image-gen prompts, A/B variants | custom (concept + image-gen direction) |
| metadata-manager | medium-effort | BISAC classification, sales description, keyword SEO, pricing, distribution settings; never fabricates an endorsement, review quote, credential, award, or sales statistic (mark [AUTHOR/PUBLISHER TO VERIFY]); introduces no new factual claim during copywriting | custom (metadata + SEO + distribution) |
| publishing-reviewer | high-effort | Cross-validate manuscript/proof/cover/metadata; spec compliance; release-readiness QA; runs a rights-clearance pass (scan for epigraphs, song lyrics, quotations beyond fair use, images needing permission) (read-only) | reviewer.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy, context-management, self-learning, error-handling, memory-management;
optional `vcs-git.md` if the author version-controls manuscripts. **Required
domain rule:** a publishing-integrity rule (rights clearance + attribution
honesty + accuracy) -- pin it; see Integrity below.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/publish-book` (full
pipeline orchestrator), `/edit-manuscript`, `/design-cover`, `/build-metadata`.
The three domain knowledge skills (developmental-editing, cover-design-psychology,
metadata-seo) become `references/` bundled under the matching domain skill --
not standalone skills.

## Domain Routing Table

No agent invents attribution (endorsement, review quote, credential, award,
sales statistic) or introduces a new factual claim during editing/copywriting --
flag for author verification instead. See Integrity.

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | "Publish my e-book" / full prep | /publish-book pipeline (editor -> proof+cover -> metadata -> review) | Capture genre, goal, platforms first | intake (if scope unclear) |
| 2 | "Edit my manuscript" (structure/flow) | manuscript-editor | Preserve author voice; ToC + pacing notes | drafter direct (short piece) |
| 3 | "Just proofread" / fix grammar | proofreader | Work from edited manuscript; build notation list | answer directly (one page) |
| 4 | "Create a book cover" | cover-designer | Pull tone/genre/target from editor notes | clarify genre + title first |
| 5 | "Set up metadata" / classification | metadata-manager | BISAC + keywords + description + price | research (unfamiliar genre) |
| 6 | "Write the book description / blurb" | metadata-manager (AIDA structure) | Sales copy, not summary | manuscript-editor (tone input) |
| 7 | "Pick keywords" / improve discoverability | metadata-manager | Reader-language over jargon; long-tail | research (competitor scan) |
| 8 | "Final review before release" / QA | publishing-reviewer | Cross-check all deliverables; RED/YELLOW/GREEN | full pipeline (if gaps) |
| 9 | "Design a table of contents" | manuscript-editor | One chapter = one complete unit | planning mode (no manuscript) |
| 10 | "I have a topic but no manuscript yet" | manuscript-editor (planning mode) | Design ToC + chapter outlines from topic | intake (clarify scope) |
| 11 | "Cover already exists, do the rest" | /publish-book with cover phase skipped | Copy existing file, skip its agent | per-agent route |
| 12 | "Check title/author consistency" | publishing-reviewer | Manuscript <-> cover <-> metadata match | answer directly (single field) |
| 13 | "What price should I set" | metadata-manager | Genre/length/competitor norms; X.99 effect | research (market data) |
| 14 | "Distribution settings for [platform]" | metadata-manager | Per-platform format/keyword/DRM specs | research (new platform rules) |
| 15 | "How does X publishing rule work" | research -> answer directly | Conventions, ISBN, royalty splits | answer directly (well-known) |
| 16 | "Pacing feels off / readers drop here" | manuscript-editor | Chapter energy map; insert/merge/reorder | reviewer (diagnose first) |
| 17 | Flag quoted/included third-party material | publishing-reviewer (rights-clearance pass) | Scan epigraphs, song lyrics, quotations beyond fair use, images needing permission; list each as a clearance item, do not assert fair use | answer directly (clearly public-domain/own work) |
| 18 | "Check story continuity" / fiction | manuscript-editor (continuity pass) | Build a continuity ledger: character details, timeline, setting; report breaks against it | proofreader (notation-level only) |

Complexity scaling: Simple (1 agent: proofread one chapter, pick keywords,
answer a convention question) | Standard (2-3 agents: edit + proof, cover +
metadata, single-mode work) | Complex (full /publish-book pipeline: all 5
agents with the review gate and revision loop).

## Ecosystem Permissions

Base + Universal Deny -- see `Docs/Templates/References/ecosystem-permissions.md`.
Add Git only if the author version-controls manuscripts. No language ecosystem
needed (this is a document domain). Domain-specific additions:

- writable `_workspace/**` -- the pipeline writes every
  deliverable (`00_input.md` .. `05_review_report.md`, `covers/`) here
- `web search`, `browser/web retrieval` -- classification codes, genre conventions,
  competitor scans, keyword research (already in Base)
- The cover image-generation tool is selected during intake as an AI Ecosystem
  Extension (see Customization Points), not a fixed permission

## Integrity (rights, attribution, accuracy)

A book is published under the author's name and exposes them to takedown,
chargeback, and reputational risk. These belong in the pinned publishing-
integrity rule; keep them proportionate -- guardrails, not regulatory machinery:

- **Rights / permissions:** publishing-reviewer runs a rights-clearance pass --
  scan for epigraphs, song lyrics, quotations beyond fair use, and images that
  need permission. List each as a clearance item the author must resolve before
  release; do not assert that a use is fair use (that is a legal judgment).
- **Attribution honesty:** metadata-manager NEVER fabricates an endorsement,
  review quote, credential, award, or sales statistic. Any such item that is not
  author-supplied is marked `[AUTHOR/PUBLISHER TO VERIFY]` -- never invented to
  fill a blurb or author bio.
- **Accuracy (nonfiction):** manuscript-editor and metadata-manager introduce no
  new factual claim, named source, statistic, quote, or case study during
  rewrite or copywriting. If a rewrite needs one, flag it for author
  verification rather than supplying it from model memory.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Title/author/subtitle drift across deliverables -- cover and
  metadata disagree with the manuscript. Mitigation: proofreader finalizes notation
  first; cover-designer and metadata-manager both read it before producing.
- [PATTERN] (pre-seeded) Description written as a summary, not sales copy -- reads
  flat. Mitigation: enforce AIDA structure (hook -> value -> gain -> CTA) in metadata.
- [PATTERN] (pre-seeded) Cover unreadable at thumbnail size -- title too small/busy.
  Mitigation: 3-word title rule + thumbnail test before accepting a concept.
- [PATTERN] (pre-seeded) Editor over-rewrites and loses author voice. Mitigation: always
  present "original preserved + revision proposed", never silent replacement.
- [PATTERN] (pre-seeded) Keywords chosen in jargon readers never search. Mitigation:
  prefer everyday reader language; add long-tail terms; scan competitor titles.
- [PATTERN] (pre-seeded) No manuscript provided but full pipeline requested -- agents stall.
  Mitigation: route to planning mode (design ToC + outlines), skip proofreading.
- [PATTERN] (pre-seeded) Unlicensed third-party material shipped -- epigraph, song lyric,
  long quotation, or image included without permission. Mitigation: publishing-reviewer
  runs a rights-clearance pass; each item is a clearance to-do, not assumed fair use.
- [PATTERN] (pre-seeded) Fabricated attribution -- an endorsement, review quote, credential,
  award, or sales stat invented to fill a blurb or author bio. Mitigation: metadata-manager
  never invents these; non-author-supplied items are marked [AUTHOR/PUBLISHER TO VERIFY].
- [PATTERN] (pre-seeded) New unverified fact introduced during rewrite -- editor/metadata adds
  a statistic, named source, quote, or case study not in the source. Mitigation: no new
  factual claim during edit/copywriting; flag for author verification instead.
- [PATTERN] (pre-seeded) Fiction continuity break -- character detail, timeline, or setting
  contradicts itself across chapters. Mitigation: manuscript-editor builds a continuity
  ledger and checks against it before sign-off.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve pipeline state across long
  manuscripts. See `Docs/Templates/Optional/hooks-template.md`.
- Optional **Stop hook consistency check** -- on pipeline completion, flag if
  title/author differ across `_workspace/` deliverables. Keep a re-entry guard.
- No code-test hooks (document domain, no build/test step).

## Cost / Model Notes

GPT-5.5 for the reasoning roles -- manuscript-editor (developmental judgment,
pacing, structure) and publishing-reviewer (cross-deliverable consistency
reasoning, release-readiness calls). medium-effort GPT-5.5 for the established-pattern execution
roles -- proofreader (rule-driven correction), cover-designer (convention-driven
concepting), metadata-manager (classification + templated description/keyword
work). Defaults: balanced (GPT-5.5 on reasoning, medium-effort GPT-5.5 on execution; compaction
95%; AGENTS.md ~200 lines). Cost-conscious override: all medium-effort GPT-5.5, compaction 85%,
full RTK in GETTING_STARTED. Quality-first: GPT-5.5 on metadata too (description is
the conversion lever). Image generation bills separately per the chosen tool.

## Customization Points

Intake follow-ups the architect most often varies for this domain:

- **Genre** (business/self-help, fiction, essay, technical) -- drives editing
  standards, cover conventions, and classification defaults
- **Publishing goal** (self-publish, publisher submission, internal) -- changes
  the metadata/distribution depth and whether ISBN guidance is needed
- **Target platforms** (KDP, regional storefronts, subscription) -- per-platform
  keyword counts, formats, DRM, and royalty rules differ
- **Cover image-generation tool** -- present 2-3 options from
  `tool-registry.md`; record in GENESIS.md "AI Ecosystem Extensions". If none,
  cover-designer delivers a text concept + prompt for the author to run
- **Solo author vs. small press** (multi-role / approval gates)
- **Manuscript scale** -- very long manuscripts trigger chapter prioritization
  and split-publishing suggestions; consider Git for version control
- **AI-content disclosure** -- ask how much of the work is AI-generated (cover,
  text, edits); several storefronts (e.g., Amazon KDP) require disclosing
  AI-generated content at upload. Surface that requirement at the distribution
  step so the author can declare it; do not declare on their behalf
- **Notation baseline / house style** -- the bundled proofreader rules are
  localized (Korean conventions). Re-ground to the target language and house
  style (CMOS or AP for English) at generation; do not lightly edit the
  inherited convention tables

## Team-architecture pattern

Pipeline with an embedded Fan-out and a Producer-Reviewer gate: editor first,
then proofreader + cover-designer fan out in parallel (both depend on the edited
manuscript), metadata-manager joins their outputs, and publishing-reviewer is the
reviewer gate that loops revisions (up to 2). Subagents are the Harness Generator default
and cover this fine. The source harness ran it as an Agent Team for live
SendMessage cross-validation; consider Agent Teams (~15x cost) only when the
author wants the proofread/cover phase running truly concurrently with
back-and-forth -- otherwise serial subagent delegation is cheaper and sufficient.

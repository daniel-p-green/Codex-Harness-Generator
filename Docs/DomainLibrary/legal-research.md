# Bundled Domain: Legal Research

Adapted from revfactory/harness-100 70-legal-research. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim). A starting point the architect adapts -- it points at templates, it does
not inline them. Builds on the Knowledge Work base profile; specializes it for
case-law research, doctrinal analysis, opinion drafting, and litigation strategy.

**Audience framing:** this seeds a tool FOR legal professionals (in-house counsel,
paralegals, law clerks) producing **draft work product a supervising licensed
attorney must independently verify and adopt** before any client-facing use. It
does not give legal advice and does not replace attorney judgment (Model Rules
5.1/5.3 supervision; 5.5 UPL).

## Profile Metadata

- **Target audience**: in-house counsel, paralegals, law clerks, legal researchers,
  compliance teams producing reference memos and dispute-response strategy
- **Primary tools**: WebSearch/WebFetch (case-law lookup), Markdown deliverables;
  no programming languages by default
- **Complexity**: Standard | **Memory tier**: Lite (solo) or Standard (team) |
  **Action default**: conservative (confirm before overwriting filed work product;
  attach the draft-for-attorney-review disclaimer; never present unverified
  authority) | **VCS**: None (document-centric)

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| case-searcher | opus | Find precedents; for EACH cite record provenance (VERIFIED via a retrieved official/primary source with URL, vs UNVERIFIED-RECALL from memory), good-law status (overruled/superseded/reversed/vacated/good/unknown), and binding-in-forum vs persuasive vs non-precedential | researcher.md -- **grant Write/Edit scoped to `./_workspace/**`** (the template is read-only; this agent must write its handoff artifact) |
| legal-analyst | opus | Issue-spot, build the issue tree, doctrinal analysis (separate ratio decidendi from dicta), state applicable standard of proof + who bears the burden per element, assess strength | analyst.md (prose-reasoning variant: opus, no Bash, doctrinal reasoning not data-cleaning; keeps scoped `./_workspace/**` Write as a producer) |
| opinion-writer | sonnet | Draft IRAC opinions; populate the Rule slot ONLY with VERIFIED, good-law authority; state certainty (L1-L5); anticipate counterarguments; attach disclaimer | drafter.md |
| strategy-advisor | opus | Strategy options (litigate/arbitrate/mediate/negotiate), risk + cost-benefit; cross-validate all deliverables AND audit that every cite carries a provenance + good-law tag | planner.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (conservative), context-management, self-learning, error-handling,
memory-management. No VCS rule. **Required domain rules:** (1) a disclaimer +
supervising-attorney review gate before any client-facing work product; (2)
`sensitive-data-rule.md` -- matter material is Confidential/Restricted by default
(see Safeguards).

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/legal-research` (full pipeline
orchestrator) and `/process-inbox` (ingest contracts/evidence/prior opinions via
MarkItDown -- treat all ingested matter as privileged/confidential). Two
methodology references ship as loadable docs (store under `Docs/Areas/`, load on
demand): a case-analysis framework (IRAC, L1-L5 confidence, issue tree,
issue-strength scoring, ratio-vs-dicta, binding-vs-persuasive) and a legal-writing
methodology (opinion template, argumentation, citation formats). For common-law
targets these must be REGENERATED, not lightly edited -- the bundled defaults are
civil-law-shaped (see Customization).

## Domain Routing Table

The orchestrator NEVER emits a case name, citation, or holding from memory --
any specific authority routes through case-searcher for retrieval-backed
verification.

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | Full legal research on an issue | /legal-research (case-searcher -> legal-analyst -> opinion-writer -> strategy-advisor) | Capture issue, facts, forum/jurisdiction, client position first | clarify (if facts thin) |
| 2 | Find precedents / case law on X | case-searcher | Favorable + unfavorable; provenance + good-law + binding/persuasive tag per cite | case-searcher (verify the cite before naming it -- never assert from memory) |
| 3 | Analyze the doctrine for this issue | case-searcher -> legal-analyst | Reasoning method per legal system: analogical/precedent-matching (common law) or syllogistic norm->facts->conclusion (civil law); majority vs minority | legal-analyst alone (cases already gathered + verified) |
| 4 | Identify / structure the legal issues | legal-analyst | Issue tree; elements of claim, who bears the burden, applicable standard of proof | answer directly (single clear issue) |
| 5 | Draft a legal opinion / memo | opinion-writer | IRAC; Rule slot only VERIFIED good-law authority; certainty level; disclaimer | clarify (no verified analysis on file) |
| 6 | Litigation / dispute-response strategy | strategy-advisor | Compare litigate/arbitrate/mediate/negotiate; risk matrix | opinion-writer first (no opinion yet) |
| 7 | Assess strength / likelihood of success | legal-analyst | Issue-strength = legal basis x factual support (vs the applicable proof standard) x case-law support | strategy-advisor (if framing options) |
| 8 | Anticipate the opposing party's arguments | opinion-writer | Counterargument/rebuttal table | legal-analyst (doctrinal counterview) |
| 9 | Cost-benefit / settle-vs-litigate | strategy-advisor | EV = win prob x award - costs; label win-prob an AI estimate, not actuarial | answer directly (rough order of magnitude) |
| 10 | Cite-check / validate authority | case-searcher | Confirm court/date/number IS REAL via a retrieved source AND check negative treatment (overruled/superseded/reversed/vacated/distinguished) AND good-law status; tag UNVERIFIED-RECALL if not retrievable | case-searcher (reformatting still requires confirming the cite is real and good law) |
| 11 | Review / proofread a drafted opinion | opinion-writer (revise) or strategy-advisor (cite + consistency audit) | Cross-validate logic AND citation provenance across `_workspace/` | answer directly (single paragraph, no cites) |
| 12 | Ingest contract / evidence / prior opinion | /process-inbox (MarkItDown) -> agent | Treat as privileged/confidential; do not copy verbatim into retro/state | answer directly (already plain text) |
| 13 | Compliance / regulatory check | legal-analyst -> case-searcher | State jurisdiction; verify the statute/reg is the CURRENT in-force version (amendment/repeal, effective date) | answer directly (well-known, then verify) |
| 14 | Summarize a long case or filing | answer directly (read + summarize the provided text) | Separate holding/ratio from dicta; no new cites from memory | case-searcher (multi-case synthesis) |
| 15 | "Could there be legal issues here?" (vague) | clarify -> legal-analyst | Ask for facts, domain, forum, position; note "facts unverified" | /legal-research (once facts provided) |

Complexity scaling: Simple (1 agent/direct: single-case summary of provided text,
known-rule questions -- never emitting a fresh cite from memory) | Standard
(2 agents serial) | Complex (full 4-agent pipeline with cross-validation).

## Ecosystem Permissions

Base + Universal Deny only -- see `Docs/Templates/References/ecosystem-permissions.md`.
No language ecosystem; document-centric. Uses `WebSearch` + `WebFetch(*)` (in
Base) for retrieval-backed cite verification; `Write/Edit(./Docs/**)`,
`Write/Edit(./_workspace/**)` (pipeline deliverables), `Write(./Outbox/**)`
(exported memos). Deny programming runtimes (`Bash(python *)`, `Bash(node *)`,
`Bash(pip *)`) and `git *`. MarkItDown via the MCP server (no Python). Generate
`settings.local.json` for machine-specific paths.

## Safeguards (privilege, conflicts, citation integrity)

Legal matter material is the most sensitive data this library handles. These are
not optional for the domain:

- **Confidentiality / privilege (Model Rule 1.6):** classify all matter material
  (ingested contracts, evidence, prior opinions, facts, party identities) as
  Confidential/Restricted via `sensitive-data-rule.md`. EXCLUDE privileged content
  and client identifiers from `Docs/_working/retro/`, `/state-save` output, and
  PreCompact summaries -- store an opaque matter-ID, not the facts. A disclaimer
  does not protect privilege; leaking confidences into long-lived logs can waive it.
- **Conflicts / matter segregation (Rules 1.7/1.9):** do not research both sides of
  the same live dispute in one shared-memory environment. For distinct clients/
  matters with possibly adverse interests, use per-matter `_workspace/` subfolders
  or the hub multi-area shape. Conflicts screening is a human-attorney duty the
  tool does not perform.
- **Citation integrity (Rule 3.3 -- fabricated cites get practitioners sanctioned):**
  every cite is tagged VERIFIED (retrieved via WebFetch from an official/primary
  source -- court site, official reporter, government legislation portal -- with the
  URL recorded; a secondary-web mention is a lead, not verification) or
  UNVERIFIED-RECALL. An UNVERIFIED-RECALL cite may NEVER populate the IRAC Rule
  slot, a counterargument table, or a strategy memo -- only a clearly separated
  "Leads to verify (NOT authority)" list. Quoted holdings and pinpoint cites are
  quoted from the retrieved passage, never paraphrased from memory; parallel cites
  must resolve to the same retrieved case. On web-search failure, do NOT proceed
  from general legal knowledge as if authoritative -- report the gap.
- **Good law:** every relied-upon case also carries a good-law status; opinion-writer
  drops or downgrades any authority not confirmed good law.
- **Enforcement:** the PreToolUse gate (below) defaults DETERMINISTIC for the legal
  domain, blocking client-facing/Outbox writes that lack the disclaimer or contain
  UNVERIFIED-RECALL authority.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Missing disclaimer on work product -- opinions ship without
  the draft-for-attorney-review notice. Mitigation: opinion-writer + final summary
  prepend it; orchestrator gates client-facing output on it.
- [PATTERN] (pre-seeded) Citation fabricated or recalled-not-retrieved -- a case
  (name/court/number/holding) is asserted without a retrieved source. Mitigation:
  tag every cite VERIFIED vs UNVERIFIED-RECALL; UNVERIFIED-RECALL never appears as
  authority, only as a lead to verify.
- [PATTERN] (pre-seeded) Stale / no-longer-good law -- a real case is cited without
  checking negative treatment (overruled/superseded/reversed/vacated). Mitigation:
  case-searcher records good-law status; opinion-writer drops unconfirmed authority.
- [PATTERN] (pre-seeded) Only favorable precedents surfaced. Mitigation: classify
  favorable AND unfavorable cases per issue before handoff.
- [PATTERN] (pre-seeded) Certainty overstated. Mitigation: L1-L5 scale; downgrade to
  uncertain on conflicting authority; label any win-probability % as an AI estimate.
- [PATTERN] (pre-seeded) Client confidence leaked into retro/state/compaction --
  privileged facts or client identity written to long-lived stores. Mitigation:
  exclude matter content from retro/state/PreCompact; reference an opaque matter-ID.
- [PATTERN] (pre-seeded) Strategy defaults to "sue". Mitigation: strategy-advisor
  always compares arbitration/mediation/negotiation + reputational/business impact.
- [PATTERN] (pre-seeded) Pipeline context lost between agents. Mitigation: enforce
  `_workspace/0N_*.md` handoff files; each agent reads prior outputs first.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve issue tree, gathered cites
  (with their tags), draft status; exclude privileged matter content.
- **PreToolUse legal gate** (domain-unique, **deterministic by default**): on
  Write/Edit to Outbox/ or client-facing paths, block if (a) the disclaimer is
  absent OR (b) any citation lacks a provenance tag / is UNVERIFIED-RECALL used as
  authority. Disclaimer-presence may downgrade to advisory only when the user
  confirms all output stays internal and attorney-reviewed; the citation check
  stays deterministic.

## Cost / Model Notes

Opus for case-searcher, legal-analyst, strategy-advisor (reasoning, multi-source
judgment, cross-validation); Sonnet for opinion-writer (established IRAC once
verified analysis exists). Balanced default (Opus on the three reasoning roles,
compaction 95%, CLAUDE.md ~200). Cost-conscious: all-Sonnet except legal-analyst
on high-stakes/compliance issues, compaction 85%, CLAUDE.md ~150. Full pipeline ~4x
direct chat; route single-purpose asks to one agent.

## MCP Suggestions

Offer during intake only if the user names the service (verified servers in
`tool-registry.md`): **MarkItDown** (recommended -- inbound contracts/filings to
Markdown, no Python; config in `settings.local.json`); **Notion/Confluence** (read
access to a matter KB or precedent library). Direct legal-database (Westlaw/Lexis-
class) integration is explicitly out of scope -- do NOT invent an MCP server for it;
WebSearch + retrieval-backed verification + good-law flags are the documented
fallback, and case-searcher must name the jurisdiction's authoritative free source.

## Customization Points

- Jurisdiction + legal SYSTEM: the analytical methodology -- not just citation
  format and statute tables -- is civil-law-shaped in the harness defaults. For
  common-law targets, re-ground it: analogical/precedent reasoning, stare decisis,
  binding-vs-persuasive authority, court hierarchy, circuit/jurisdiction splits;
  de-emphasize the civil-law "academic majority/minority theory" weighting.
  Regenerate (do not lightly edit) the case-analysis-framework and legal-writing
  references. Replace the Korean Civil-Act/court-format defaults.
- Citation style (Bluebook, OSCOLA, neutral-citation) + the authoritative free
  source for the jurisdiction.
- Confidentiality/conflicts: will this handle privileged or client-identifying
  material (almost always yes)? -> sensitive-data rule + PII/matter exclusion from
  memory; per-matter segregation if multiple clients.
- Disclaimer/gate enforcement: deterministic default; advisory only if all output
  stays internal and attorney-reviewed.
- Solo vs team (Lite vs Standard memory; multi-role for distinct practice areas).
- Practice area (civil/criminal/administrative/labor/IP) -- seeds the elements-of-
  claim and proof-standard tables.

## Team-architecture pattern

Pipeline (case search -> doctrinal analysis -> opinion -> strategy) with a
Producer-Reviewer finish (strategy-advisor cross-validates logical consistency AND
citation provenance across all `_workspace/0N_*.md` deliverables). Subagents are
the default and fit the serial dependency chain at far lower token cost than the
harness's Agent Team; each agent writes its `_workspace/0N_*.md` artifact and the
next reads it (case-searcher needs `_workspace` write access despite its read-only
researcher base). Consider Agent Teams only if a multi-issue matter genuinely
benefits from parallel per-issue analysis.

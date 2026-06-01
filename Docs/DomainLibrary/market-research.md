# Bundled Domain: Market Research

Adapted from revfactory/harness-100 44-market-research. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim) -- a starting point the architect adapts; it points at templates rather
than inlining them.

## Profile Metadata

- **Target audience**: founders, product/strategy teams, consultants, and analysts
  producing industry, competitor, consumer, and trend analysis for a business decision
- **Primary tools**: web research + Markdown deliverables; no code, no VCS by default
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: conservative
  (cite every figure, confirm before overwriting a delivered report) | **VCS**: None

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim).
The five harness analysts collapse onto two reusable templates -- one research
specialist parameterized per analysis stream, one read-only reviewer. The four
analysts each land a deliverable, so grant them Write/Edit scoped to
`./_workspace/**` -- `researcher.md` is read-only by default and must be widened
for these producer roles. research-reviewer stays read-only:

| name | model | role | template |
|---|---|---|---|
| industry-analyst | opus | Market size (TAM/SAM/SOM), CAGR, value chain, Porter 5 Forces, regulatory | researcher.md |
| competitor-analyst | opus | Competitor mapping, strategic groups, SWOT, positioning, moat analysis | researcher.md |
| consumer-analyst | sonnet | Segmentation, journey mapping, jobs-to-be-done, personas, research methods | researcher.md |
| trend-analyst | opus | PESTLE, technology/micro trends, scenario analysis, 3-5 year outlook | researcher.md |
| research-reviewer | opus | Cross-stream consistency, insight synthesis, strategic recs (read-only) | reviewer.md |
| report-writer | sonnet | Assemble analyst outputs into the integrated report deliverable | drafter.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (conservative), context-management, self-learning, error-handling, and
memory-management. **Pin one domain rule:** a source-integrity guardrail -- every
market figure carries source + dates and a RETRIEVED vs RECALLED tag, and no
recalled or fabricated figure is presented as data (see Source Integrity). Add
`data-handling-rule.md` only if the intake names internal sales/CRM data feeding
the sizing.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/market-research` (pipeline
orchestrator -- see Pattern G), `/porter-five-forces` (industry-structure
framework), `/tam-sam-som` (market-sizing methodology).

## Domain Routing Table

The orchestrator NEVER presents a market figure (size, CAGR, share, competitor
revenue/funding, pricing) from memory as data -- any specific number routes
through an analyst for retrieval and carries a source + dates + a RETRIEVED vs
RECALLED tag (see Source Integrity).

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | "Do full market research on X" | /market-research (fan-out 4 analysts -> reviewer -> report-writer) | Capture objective, market, geography, decision in 00_input | clarify scope first (if market unspecified) |
| 2 | "How big is this market" / sizing / TAM | industry-analyst (+ /tam-sam-som) | Run top-down AND bottom-up; report a RANGE with the convergence band (cross-validate within 2x), the 2-3 most sensitive assumptions, not a single point | answer directly (well-published number, with source + dates) |
| 3 | "Is this industry attractive" / 5 Forces | industry-analyst (+ /porter-five-forces) | Score each force 1-5; the 1-5 sum is a rough heuristic -- weight by materiality, do not treat the total as precise | answer directly (single-force question) |
| 4 | "Analyze the competition" / competitor landscape | competitor-analyst | 3-5 direct + 2-3 indirect; never "no competitors"; tag each figure REPORTED (filing/press) vs INFERRED (estimated) | industry-analyst (need structure first) |
| 5 | SWOT / positioning map for named rivals | competitor-analyst | Use public signals (filings, jobs, reviews); revenue/funding REPORTED vs INFERRED, never present inferred as reported | answer directly (one competitor, known) |
| 6 | "Who is the customer" / segments / personas | consumer-analyst | Segment by behavior + JTBD, not demographics alone; label each persona/segment by evidence basis (primary survey/interview vs a few reviews/posts), never as fact | competitor-analyst (feature comparison input) |
| 7 | Customer journey / pain points / unmet needs | consumer-analyst | Map end-to-end stages, touchpoints, opportunities | answer directly (single known pain point) |
| 8 | "What trends will shape this" / PESTLE / outlook | trend-analyst | Separate trends from fads; tie to implications | answer directly (one obvious macro trend) |
| 9 | Scenario / future outlook (3-5 yr) | trend-analyst | Optimistic / base / pessimistic; label scenario probabilities subjective (analyst judgment, not measured) | answer directly (short-horizon question) |
| 10 | "Verify / cross-check the analyses" | research-reviewer | Consistency matrix; classify CRITICAL/WARNING/INFO | answer directly (single-claim check) |
| 11 | "Synthesize findings into recommendations" | research-reviewer -> report-writer | Integration is the value; rank recs by priority | report-writer (if inputs already verified) |
| 12 | "Write up / format the report" | report-writer | Assemble 01-04 + recs into 05; every figure carries source + pub date + as-of date and a RETRIEVED/RECALLED tag; flag any figure >2-3 yrs old as stale for fast-moving markets | answer directly (one-section tidy-up) |
| 13 | "Market entry strategy for X" | /market-research (full) -> research-reviewer (entry lens) | Frame recs around go/no-go and entry mode | industry + competitor only (if narrow) |
| 14 | "Update the analysis with new data" | reviewer identifies affected streams -> re-run those analysts | Re-validate sizing if inputs moved >20% | answer directly (typo/format fix) |
| 15 | "Just the executive summary" | report-writer (condense existing 05) | Lead with conclusion; 1 page; "so what" framing | research-reviewer (if no integrated report yet) |

Complexity scaling: Simple (1 agent or direct -- a single sizing number, one
SWOT, a definition) | Standard (2-3 agents serial -- one analysis stream plus
review) | Complex (full pipeline: 4 analysts fan-out, reviewer, report-writer).

## Source Integrity (research credibility -- the core axis)

A market study guides a real business decision; a fabricated or stale figure is
the failure mode that destroys its value. This is lighter than the legal domain
(no privilege, no good-law machinery) but the same discipline applies to numbers:

- **Every figure is sourced and dated.** Each market figure (size, CAGR, share,
  competitor revenue/funding, pricing) carries a source (named source or URL),
  a publication date, and an as-of date. Tag it RETRIEVED (pulled from a named
  source/URL this session) vs RECALLED (from memory -- unverified). A RECALLED
  or fabricated figure is NEVER presented as data; it appears only as a clearly
  separated "to verify" lead, not in a sizing table or a competitor row.
- **Staleness.** Flag any figure older than 2-3 years as stale for fast-moving
  markets; prefer a fresher retrieved number or downgrade confidence.
- **Methodology / persona honesty.** Personas and segments are labeled by
  evidence basis -- primary survey/interview vs a thin proxy (a few reviews,
  forum or social posts). A persona built on thin, self-selected data is never
  presented as fact; say what it rests on.
- **Confidence framing.** Market sizing is reported as a RANGE with the
  convergence band (top-down and bottom-up within 2x), naming the 2-3 most
  sensitive assumptions -- not a single point estimate. Scenario probabilities
  are labeled subjective (analyst judgment). The Porter 1-5 force scores are a
  rough heuristic: weight by materiality, do not present the sum as precise.
- **Reported vs inferred.** Competitor revenue/funding is tagged REPORTED (from
  a filing or press release) vs INFERRED (estimated from signals); an inferred
  figure is never presented as reported.
- **Enforcement is advisory.** research-reviewer flags an unsourced, RECALLED, or
  inferred-as-reported figure as CRITICAL during cross-validation; report-writer
  carries the source + dates + tag through to the deliverable. (No deterministic
  PreToolUse gate by default -- this domain's stakes do not warrant the legal
  domain's blocking hook; offer one only if the intake asks for it.)

## Ecosystem Permissions

Base + Universal Deny -- see `Docs/Templates/References/ecosystem-permissions.md`.
No language ecosystem (research/writing domain, no code). Allow `WebSearch` and
`WebFetch(*)` (core to every analyst). Add `Write(./_workspace/**)` and
`Edit(./_workspace/**)` so the four analysts land deliverables (00_input through
05_research_report) without prompts -- the `researcher.md` template is read-only
by default, so widen Write/Edit to `./_workspace/**` for these producer roles
(research-reviewer stays read-only). If the intake adds inbound report files,
include `Bash(markitdown *)` per the document-parsing note in tool-catalog.
Generate `settings.local.json` for any machine-specific paths or MCP keys.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Figure recalled or fabricated, presented as data -- an analyst
  states a market size, CAGR, share, or competitor revenue with no source, or from memory.
  Mitigation: every figure carries source + pub date + as-of date and a RETRIEVED vs
  RECALLED tag; RECALLED/fabricated numbers never enter a sizing table or competitor row,
  only a "to verify" lead; reviewer flags as CRITICAL.
- [PATTERN] (pre-seeded) Sizing reported as a single point -- TAM stated as one number with
  no band or assumptions. Mitigation: report a RANGE with the convergence band, name the
  2-3 most sensitive assumptions; scenario probabilities labeled subjective.
- [PATTERN] (pre-seeded) Stale figure used as current -- a 5-year-old number cited for a
  fast-moving market. Mitigation: flag figures >2-3 yrs old as stale; prefer a fresher
  retrieved number or downgrade confidence.
- [PATTERN] (pre-seeded) Persona built on thin data, presented as fact -- a few reviews or
  forum posts dressed up as a validated segment. Mitigation: label each persona/segment by
  evidence basis (primary survey/interview vs proxy), never as fact.
- [PATTERN] (pre-seeded) Inferred competitor figure presented as reported -- an estimated
  revenue/funding number stated like a filing. Mitigation: tag REPORTED (filing/press) vs
  INFERRED (estimated); never present inferred as reported.
- [PATTERN] (pre-seeded) Porter score sum treated as precise -- the 1-5 force total drives
  a verdict. Mitigation: the sum is a rough heuristic; weight by materiality.
- [PATTERN] (pre-seeded) TAM inflated to "the whole internet" -- top-down sizing skips
  segment filtering. Mitigation: require top-down AND bottom-up, converge within 2x.
- [PATTERN] (pre-seeded) "No competitors" claim -- competitor-analyst under-counts.
  Mitigation: always name 3-5 direct + 2-3 indirect; substitutes count as competition.
- [PATTERN] (pre-seeded) Trends vs fads conflated -- trend-analyst lists hype as lasting
  trends. Mitigation: assess durability and timeline before listing; tie each to impact.
- [PATTERN] (pre-seeded) Streams contradict each other -- industry growth segment does not
  match consumer segment. Mitigation: reviewer runs a consistency matrix before synthesis.
- [PATTERN] (pre-seeded) Report restates analyses instead of integrating -- report-writer
  concatenates. Mitigation: cross-analysis insights and ranked recommendations are required.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve research direction, source
  criteria, and which streams are complete before compaction. See
  `Docs/Templates/Optional/hooks-template.md`.
- Optional **Stop hook** review reminding the orchestrator to confirm all four
  streams ran, every figure carries source + dates + a RETRIEVED/RECALLED tag,
  and CRITICAL findings (unsourced/recalled/inferred-as-reported figures) were
  resolved before reporting done.
- Optional **PreToolUse source-integrity gate** (advisory by default, NOT
  generated unless the intake asks): on Write/Edit to `_workspace/05_*` or an
  exported report, warn if a figure lacks a source/date/tag. The legal domain's
  deterministic blocking version is deliberately not the default here.

## Cost / Model Notes

Opus for the reasoning-heavy streams (industry, competitor, trend) and the
research-reviewer; Sonnet for consumer-analyst and report-writer (segmentation
and assembly follow established structure). Default: balanced (Opus on the three
analytical streams + reviewer, Sonnet on execution; compaction 95%; CLAUDE.md
~200 lines). Cost-conscious override: all-Sonnet except research-reviewer on
Opus, compaction 85%, CLAUDE.md ~150. The full fan-out pipeline runs four
analysts plus a reviewer -- the most expensive path; reserve it for genuine
full-research requests and route single-stream asks to one agent.

## Customization Points

- Scope shape: full pipeline vs. a single stream (drives whether /market-research
  or a lone analyst is the default route)
- Industry/geography focus (calibrates analyst prompts and data sources)
- Internal data feeding sizing (CRM/sales exports -> add data-handling-rule.md)
- Output format: Markdown only vs. .docx/.pptx deliverable (-> Pandoc + report-writer)
- Citation strictness / source allowlist (paywalled vs. free sources); source-
  integrity enforcement: advisory reviewer flag (default) vs. a PreToolUse gate
  on exported reports if the user wants it deterministic
- Sizing rigor: require both top-down and bottom-up, or accept one with caveats

## Team-architecture pattern

Fan-out-Fan-in: the four analysts run in parallel (industry + competitor first,
then consumer + trend, which depend on their handoffs), then research-reviewer
fans in to cross-validate and report-writer assembles -- a Producer-Reviewer
finish on a Fan-out body. This is the one market-research phase that justifies
Agent Teams over the subagent default: the harness's `/market-research` skill
uses a five-agent team with direct cross-validation. For lighter single-stream
work, stay on subagents (~4x) rather than a team (~15x).

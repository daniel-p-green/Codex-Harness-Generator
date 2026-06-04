# Bundled Domain: Product Management

Adapted from revfactory/harness-100 46-product-manager. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim). A starting point the architect adapts -- it points at templates, it
does not inline them.

## Profile Metadata

- **Target audience**: product managers, product owners, founders, and PM-adjacent
  leads who produce roadmaps, PRDs, user stories, sprint plans, and retros
- **Primary tools**: Markdown deliverables; optional Jira/Linear, Notion, GitHub;
  no compilation step (document- and planning-centric)
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: conservative (confirm before overwriting an approved roadmap/PRD) | **VCS**: optional Git (docs repo)

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| strategist | high-effort | Product vision, OKRs, theme-based roadmap (Now/Next/Later), RICE/ICE prioritization | researcher.md (reframe research output as strategy reasoning) |
| prd-writer | medium-effort | Author the PRD: problem, solution, scoped functional + non-functional requirements, success metrics; tag the problem source (user-reported / research-backed / PM-hypothesis) and mark user-not-supplied impact/scope figures unverified | drafter.md |
| story-writer | medium-effort | Decompose PRD into INVEST user stories with Given-When-Then AC and story points | drafter.md |
| sprint-planner | medium-effort | Capacity calc, sprint-goal setting, story allocation, risk buffer, retro template | analyst.md (reframe data work as capacity/velocity math) |
| pm-reviewer | high-effort | Cross-validate roadmap->PRD->stories->sprint consistency, traceability, feasibility; flag vanity/gameable success metrics and dark-pattern engagement targets (read-only) | reviewer.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy, context-management, self-learning, error-handling, memory-management;
**a pinned evidence-integrity guardrail** (one short rule -- every RICE/ICE input,
success-metric baseline, and market/user number is tagged SOURCED or ASSUMED;
never assert a market/user number as fact -- see Evidence Integrity below);
conditional `vcs-git.md` (if deliverables live in a Git repo) and
`output-styles-template.md` (consistent PRD/story house style).

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/plan-product` (full
pipeline orchestrator -- adapt `Docs/Templates/Skills/build.md` as the
multi-phase driver), `/rice-score` (RICE/ICE/MoSCoW prioritization -- custom;
carries data-source discipline: each input tagged SOURCED with its data source --
analytics/survey/CS tickets/interviews -- or ASSUMED; Confidence <=50% triggers a
validation spike), `/estimate-points` (Fibonacci SP, velocity, decomposition
criteria -- custom; carries the harness bias-prevention: anchoring (independent
estimates before discussion), optimism (include test/review/deploy, weigh worst
case), Parkinson (SP measures complexity not time -- "3 SP" not "2 days")).

## Domain Routing Table

Evidence discipline (applies to every row): every RICE/ICE input, success-metric
baseline, and market/user number is tagged SOURCED (cite the source -- analytics,
survey, CS tickets, interview count) or ASSUMED (model estimate). Never assert a
market or user number as fact.

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | "Plan this product" / full PM workflow | /plan-product -> strategist -> prd-writer -> story-writer -> sprint-planner -> pm-reviewer | Capture product, goals, team, constraints in `_working/00_input.md` first | clarify (if product/goal unclear) |
| 2 | "Build a roadmap" / set the vision | strategist -> pm-reviewer | Theme-based Now/Next/Later, OKR links, North Star Metric | answer directly (single-quarter tweak) |
| 3 | "Write a PRD" | strategist -> prd-writer -> pm-reviewer | PRD needs roadmap context; reads `01_product_roadmap.md` | prd-writer alone (roadmap already exists) |
| 4 | "Decompose into user stories" (PRD exists) | story-writer -> pm-reviewer | Reads PRD; INVEST + Given-When-Then AC, 8 SP cap per story | strategist -> prd-writer (no PRD yet) |
| 5 | "Plan the sprints" (stories exist) | sprint-planner -> pm-reviewer | 70-80% capacity, dependency-aware allocation, 20% buffer | story-writer (no stories yet) |
| 6 | "Prioritize the backlog" / "what to build next" | /rice-score -> strategist | RICE = (Reach x Impact x Confidence) / Effort; ICE for quick calls | answer directly (2-3 items, obvious) |
| 7 | "Estimate story points" / "how big is this" | /estimate-points -> story-writer | Fibonacci; SP = max(technical, domain, uncertainty); 13+ must decompose | answer directly (trivial 1-2 SP) |
| 8 | "Review this plan" / consistency check | pm-reviewer | Traceability matrix; RED/YELLOW/GREEN; up to 2 rework rounds | answer directly (single doc spot-check) |
| 9 | "Set OKRs for the quarter" | strategist | Objective + measurable KRs; link KRs to success metrics | answer directly (refine existing OKR) |
| 10 | "Write a retro template" / sprint retro | sprint-planner | Start-Stop-Continue + action owners + velocity tracking | answer directly (use stock template) |
| 11 | "Scope this down to an MVP" | strategist (MoSCoW) -> prd-writer (In/Out-of-scope) | Cut to Must-haves; record Out-of-scope with reasons | clarify (success criteria undefined) |
| 12 | "Trace requirement X to its stories/sprint" | pm-reviewer | Build/read Requirements Traceability Matrix (FR -> US -> Sprint) | explorer-style search of `_working/` |
| 13 | "Turn this feedback into a feature request" | strategist (frame the problem) -> prd-writer | Separate user problem from business problem before solutioning | answer directly (log to backlog) |
| 14 | "Compare these two roadmap options" | strategist (RICE per option) -> pm-reviewer | Score both; show strategic-weight adjustment if intuition conflicts | answer directly (one clearly wins) |
| 15 | "Draft the release plan / timeline" | sprint-planner | Map sprints -> releases, key features, dates, dependency chain | prd-writer (timeline section only) |
| 16 | "Size the market" / "competitive analysis" / TAM-SAM-SOM | strategist | Tag every figure SOURCED (name the source) or ASSUMED (model estimate); never assert a market number as fact; show the estimation method, not a bare total | clarify (no inputs/comparables given) |

Complexity scaling: Simple (1 agent: a single OKR tweak, one estimate, a stock
retro template) | Standard (2-3 agents serial: PRD-from-roadmap, stories-from-PRD,
sprint-from-stories, each with a review pass) | Complex (all 5 agents: full
plan-product pipeline with cross-verification and rework loop).

## Ecosystem Permissions

Base + Universal Deny -- see `Docs/Templates/References/ecosystem-permissions.md`.
Add **Git** only if PM deliverables live in a versioned docs repo. No language
ecosystem needed (no build/test). Add writable `_working/**` and `Docs/**`
for the staged deliverables (`00_input.md` through
`05_review_report.md`). If a tracker MCP is approved (see MCP suggestions),
allow only its read + create-issue tools; gate bulk delete/close behind human
approval. Generate `local config profile` for any machine-specific vault or
tracker path.

## Evidence Integrity

PM deliverables drive build-vs-cut decisions, so the numbers behind them must not
be laundered into false certainty. This is a light additive guardrail, not
regulatory machinery:

- **SOURCED vs ASSUMED tagging:** every RICE/ICE input (Reach, Impact, Confidence,
  Effort), success-metric baseline, and market/user number carries one tag --
  SOURCED (cite the source: product analytics, survey, CS tickets, interview count,
  pricing data) or ASSUMED (PM model estimate). RICE Confidence already encodes how
  much data backs the score; the tag makes the source explicit alongside it.
- **Never assert a market or user number as fact.** TAM/SAM/SOM, adoption rates, and
  "X% of users want Y" are estimates or sourced figures, never bare assertions.
  Show the estimation method behind a total, not just the total.
- **Problem-source tagging (prd-writer):** each problem statement is tagged
  user-reported / research-backed / PM-hypothesis. Any impact or scope figure the
  user did not supply is marked unverified -- prd-writer does not invent reach or
  impact magnitudes and present them as measured.
- **Vanity / gameable-metric check (pm-reviewer):** flag success metrics that are
  vanity (raw pageviews, downloads, registered-not-active) or trivially gameable;
  prefer outcome metrics tied to a user or business value. Also flag any
  engagement target that only moves via a dark pattern (forced friction, deceptive
  defaults, manufactured urgency) -- engagement bought that way is a YELLOW finding.
- **MVP framing:** "MVP = the smallest thing that tests the riskiest assumption,"
  not the smallest shippable feature set. Scope-down (route 11) names the riskiest
  assumption and what evidence would validate or kill it.

```
- [PATTERN] (pre-seeded) Solutioning before the problem is framed -- PRD jumps to
  "build a dashboard" before naming the user/business problem. Route problem-framing
  to strategist first; prd-writer describes What/Why, not How.
- [PATTERN] (pre-seeded) Stories drift from the PRD -- story-writer invents scope not
  in the PRD, or skips edge/error cases. pm-reviewer must run the traceability matrix
  (every FR maps to >=1 US) before sprint planning.
- [PATTERN] (pre-seeded) Over-committed sprints -- sprint-planner fills 100% of capacity.
  Enforce 70-80% planned, 20% buffer; flag any sprint above 80% as YELLOW.
- [PATTERN] (pre-seeded) RICE Effort guessed, not derived -- Effort estimated as a single
  number with no eng/design/QA breakdown. Require person-month components; Confidence
  <=50% triggers a validation spike before commitment.
- [PATTERN] (pre-seeded) Date-based roadmap creep -- roadmap reverts to hard dates per
  initiative. Default to theme-based Now/Next/Later; dates live in the sprint/release plan only.
- [PATTERN] (pre-seeded) Oversized stories slip through -- a 13+ SP story enters a sprint
  un-decomposed. estimate-points must split by workflow/data/user-type/CRUD/happy-sad path.
- [PATTERN] (pre-seeded) Numbers asserted as fact -- RICE inputs, metric baselines, or
  market/user figures stated without a source. Mitigation: tag every such number SOURCED
  (analytics/survey/CS tickets/interviews) or ASSUMED (model estimate); never assert a
  market/user number as fact; show the estimation method behind any total.
- [PATTERN] (pre-seeded) Problem source unmarked -- prd-writer states a user problem and
  its impact/scope as if measured. Mitigation: tag the problem user-reported /
  research-backed / PM-hypothesis; mark any impact/scope figure unverified if the user
  did not provide it; do not invent reach/impact magnitudes.
- [PATTERN] (pre-seeded) Vanity or gameable success metric -- a metric tracks raw
  pageviews/downloads/registrations or is easily gamed, or an engagement target only
  moves via a dark pattern. Mitigation: pm-reviewer flags it YELLOW and prefers an
  outcome metric tied to user/business value; no engagement bought with deceptive UX.
- [PATTERN] (pre-seeded) MVP defined as "smallest shippable thing" rather than the
  smallest thing that tests the riskiest assumption. Mitigation: scope-down names the
  riskiest assumption and the evidence that would validate or kill it.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve the active roadmap/PRD/story
  state across compaction. See `Docs/Templates/Optional/hooks-template.md`.
- Optional **Stop hook consistency nudge** -- on session stop, remind to run
  pm-reviewer if `02_prd.md` changed but `03_user_stories.md` did not (drift guard).
  Keep a re-entry guard. Not a code self-review; this domain produces docs, not code.

## Cost / Model Notes

GPT-5.5 for the reasoning roles (strategist, pm-reviewer) where prioritization
judgment and cross-document consistency matter; medium-effort GPT-5.5 for the execution roles
that fill established templates (prd-writer, story-writer, sprint-planner).
Defaults: balanced (high-effort GPT-5.5 on strategy/review, medium-effort GPT-5.5 on authoring; compaction 95%;
AGENTS.md ~200 lines). Cost-conscious override: all medium-effort GPT-5.5, compaction 85%, brief
RTK note in GETTING_STARTED. Quality-first: GPT-5.5 on prd-writer too (PRD clarity is
the cost center downstream). Subagents ~4x direct; the full Agent-Team pipeline ~15x.

## Customization Points

- Agile flavor (Scrum vs Kanban -> sprint-planner vs flow/WIP framing)
- Prioritization framework default (RICE vs ICE vs MoSCoW vs Kano)
- Team shape and velocity data (drives capacity math; default 4-6 person Scrum)
- Tracker integration (Jira / Linear / GitHub Issues -> MCP + permission scope)
- Deliverable house style (PRD/story templates, P0-P3 vs MoSCoW priority labels)
- Solo PM vs PM-with-eng/design stakeholders (reviewer rigor, approval gates)

## MCP Suggestions (optional)

If the intake names a tracker, add the verified server from tool-registry
(GitHub MCP for GitHub Issues; Linear/Jira via their official or verified
connectors) for read + create-issue. Keep ticket sync read-mostly; never
auto-close or bulk-edit issues without human approval.

## Team-architecture pattern

Pipeline with a Producer-Reviewer terminal stage: strategist -> prd-writer ->
story-writer -> sprint-planner feed forward, and pm-reviewer cross-verifies the
whole chain with a bounded rework loop (max 2 iterations). The harness original
runs this as a live Agent Team (SendMessage cross-talk); for the Harness Generator default,
subagents-on-disk handoff through `_working/0N_*.md` is cheaper (~4x vs ~15x) and
preserves traceability -- reserve Agent Teams for the full plan-product pipeline
when real-time cross-agent revision genuinely pays for itself.

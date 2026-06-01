# Bundled Domain: Financial Modeling

Adapted from revfactory/harness-100 53-financial-modeler. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim) -- a starting point the architect adapts; it points at templates, it
does not inline them.

**Output framing:** this produces decision-driving, investor-facing numbers
(valuations, IRR/MOIC, per-share values, multi-year projections). Those are
forward-looking estimates built on assumptions -- not investment advice and not a
guarantee. External deliverables carry a forward-looking-statements /
not-investment-advice notice (see Disclaimer & integrity).

## Profile Metadata

- **Target audience**: founders, FP&A analysts, VC/PE associates, and operators
  building revenue models, cost structures, scenario analyses, and valuations
  (fundraising decks, internal plans, M&A, feasibility studies)
- **Primary tools**: Markdown deliverables + spreadsheets (CSV/XLSX); optional
  Python (pandas) for FCF/sensitivity math; web research for benchmarks/comps
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: conservative (numbers carry assumptions -- surface them; attach the forward-looking/not-advice notice to external output) | **VCS**: Git (optional -- model versions matter)

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| revenue-modeler | opus | Revenue streams, pricing, TAM/SAM/SOM, growth curves, unit economics; distinguish bookings/billings from RECOGNIZED revenue | analyst.md |
| cost-analyst | sonnet | Fixed/variable classification, COGS/OpEx/CapEx, break-even (= fixed / unit contribution margin), margins | analyst.md |
| scenario-planner | opus | Bear/Base/Bull (internally consistent -- Bull revenue implies Bull-level cost/CAC), sensitivity (tornado/2-way), probability-weighting (default 20/60/20) | performance-analyst.md |
| valuation-expert | opus | DCF/WACC (CAPM w/ size premium; unlever/relever beta; EV->equity bridge), multiples, IRR/MOIC; present a RANGE | analyst.md (valuation-judgment variant: opus, no data-cleaning framing) |
| model-reviewer | opus | Cross-validate formulas, three-statement articulation, units/currency, recognition, false precision (read-only QA) | reviewer.md (model-integrity variant -- see Disclaimer & integrity) |
| summary-drafter | sonnet | Edit the model into an investor/executive summary; attach the forward-looking notice | drafter.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy, context-management, self-learning, error-handling (with diagnostic
discipline for tracing numeric discrepancies), memory-management, `vcs-git.md`
(optional), and `data-handling-rule.md` (source financials read-only). **Required
domain rule:** pin the not-investment-advice + forward-looking-statements
disclaimer to any investor/lender/M&A-facing deliverable.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/build-model` (full pipeline
orchestration -- adapt `build.md`; pins the canonical deliverable filename map
00_input..06_review_report), `/unit-economics` (LTV/CAC, CM1-3, cohorts),
`/sensitivity-analysis` (tornado, 2-way tables, scenarios; Monte Carlo only with
the Python engine), `/dcf-valuation` (FCFF, WACC, terminal value, multiples
cross-check). The last three are agent-extension skills (custom): their content
must carry the load-bearing formulas (WACC = E/V*Ke + D/V*Kd*(1-T); CAPM Ke = Rf +
beta*MRP + size premium; unlever/relever beta; FCFF = NOPAT + D&A - CapEx - dNWC;
EV->equity bridge = EV - net debt - preferred - minority; cohort-discounted LTV;
break-even). Treat these skill files as the formula authority; do not
let the generator reconstruct these from priors.

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | "Build a full financial model" | revenue -> cost -> scenario -> valuation -> model-reviewer (-> [Must-Fix] back to author, max 2 rounds) -> summary-drafter | Deliverables to `_workspace/0X_*.md` | clarify business model first |
| 2 | "Just do revenue forecasting" | revenue-modeler -> model-reviewer | Top-down + bottom-up; bookings vs recognized revenue | intake (if business model unclear) |
| 3 | "Analyze our cost structure" | cost-analyst -> model-reviewer | Needs revenue scale; itemize granularly | revenue-modeler first |
| 4 | "What's our break-even?" | cost-analyst | Fixed costs / unit contribution margin | revenue-modeler (if no cost data) |
| 5 | "Run scenarios / sensitivity" | scenario-planner (+/sensitivity-analysis) | One variable at a time; internally-consistent scenarios | intake (which variables matter) |
| 6 | "Stress test / what's our runway" | scenario-planner (Bear + cash burn) | Survival test; runway, next-raise timing | cost-analyst (if cost model thin) |
| 7 | "Value the company / DCF" | valuation-expert (+/dcf-valuation) | Needs scenario financials; >=2 methods, present a RANGE | scenario-planner first |
| 8 | "What multiple should we use" | valuation-expert (comparable analysis) | Web-research peers; record source + date + as-of | answer directly (well-known sector, then verify) |
| 9 | "Unit economics / LTV/CAC" | revenue-modeler (+/unit-economics) | Cohort-discounted LTV; paid-with-paid CAC, not blended; CM1-3 | answer directly (single ratio) |
| 10 | "Review / sanity-check this model" | model-reviewer | Cross-compare; 3-statement articulation; units/recognition; 3-tier severity | answer directly (one formula) |
| 11 | "Investor-ready summary / exec deck" | summary-drafter | After model-reviewer signs off; range + forward-looking notice | model-reviewer first (unvalidated) |
| 12 | "Update an assumption and reflow" | scenario-planner -> valuation-expert -> model-reviewer | Propagate downstream; re-validate | answer directly (isolated cell) |
| 13 | "Pre-revenue startup, no numbers" | revenue-modeler (bottom-up TAM/SAM/SOM) -> scenario-planner -> valuation-expert | Pure idea/MVP: VC method / scorecard / Berkus + PSR. High-growth-with-revenue: 2-stage DCF, VC discount 25-35%. Emphasize cash burn | propose 3 revenue model types first |
| 14 | "Check my formulas / numbers tie out" | model-reviewer | FCFF = NOPAT + D&A - CapEx - dNWC (change, not balance); revenue + cash + BS tie across docs | answer directly (single check) |

Complexity scaling: Simple (1 agent: a ratio, a break-even, a comp lookup, an
isolated formula check) | Standard (2-3 agents) | Complex (4-6 agents serial: full
build, or assumption-change reflow with re-validation).

## Disclaimer & integrity (load-bearing for this domain)

- **Not investment advice:** external deliverables (decks, valuations, M&A
  materials) carry a forward-looking-statements / not-investment-advice / not-a-
  substitute-for-professional-counsel notice. summary-drafter and valuation-expert
  prepend it; the orchestrator gates external output on its presence (optional
  PreToolUse disclaimer gate, advisory by default / deterministic for fundraising
  + M&A).
- **Three-statement articulation + circularity:** if the model includes a balance
  sheet / debt schedule, model-reviewer verifies BS balances each period, ending
  cash on the CF = cash on the BS, net income flows to retained earnings; and the
  interest<->cash<->interest circularity is handled with an iterative-calc toggle
  or an average-balance circuit-breaker, with convergence checked.
- **Revenue recognition:** distinguish bookings/billings from recognized revenue;
  multi-period (e.g. annual prepaid) contracts are recognized over the term with a
  deferred-revenue balance (ASC 606 / IFRS 15) -- not booked up front.
- **Assumptions discipline:** all drivers live in one assumptions block/tab;
  formula cells reference assumptions, never embed literals (other than unit
  conversions); every output traces to an assumption with a stated basis.
- **Units / currency / FY:** one units scale and one reporting currency across all
  deliverables; multi-currency inputs show the FX rate + date; FY vs CY periods
  align before any sum or comparison.
- **Honest precision:** round outputs to the precision the inputs justify
  (typically 2-3 sig figs for valuations); present a range, never a falsely-precise
  point; probability-weighted point estimates are secondary to the Bear/Base/Bull
  range and their weights are labeled subjective inputs.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Assumptions buried in cells -- every figure needs an
  explicit basis (benchmark/source/method); tag estimates as "estimate"; drivers
  in one assumptions block, no literals inside formula cells.
- [PATTERN] (pre-seeded) Numbers drift between deliverables -- revenue/cash must tie
  across revenue model, scenarios, valuation, and (if present) the balance sheet.
- [PATTERN] (pre-seeded) Balance sheet doesn't balance / circularity unconverged --
  for debt-bearing 3-statement models, check A=L+E each period and the
  interest<->cash circuit converges (iterative toggle or avg-balance breaker).
- [PATTERN] (pre-seeded) Bookings recognized as revenue -- prepaid/multi-period
  contracts must recognize over the term with a deferred-revenue liability (ASC 606).
- [PATTERN] (pre-seeded) Undiscounted LTV overstates value -- prefer cohort LTV with
  a discount rate + finite horizon; compute LTV/CAC on a consistent CAC basis
  (paid-with-paid), not blended LTV vs paid CAC.
- [PATTERN] (pre-seeded) Terminal value distorts DCF -- g must be strictly < WACC
  (else the Gordon denominator is invalid: a HARD constraint, not a warning). Warn
  when TV > ~65% of EV, hard-flag > 75%; check g <= long-run GDP.
- [PATTERN] (pre-seeded) Single-point / falsely-precise valuation -- present a range
  across >=2 methods (DCF + multiples); round to the precision the inputs justify.
- [PATTERN] (pre-seeded) Web comps used without provenance -- multiples cited without
  source/date/as-of drift stale and inflate valuations; flag any comp older than
  ~12 months or from a different rate/market regime.
- [PATTERN] (pre-seeded) Investor output ships without the forward-looking / not-
  investment-advice notice. Mitigation: summary-drafter + valuation-expert prepend
  it; orchestrator gates external deliverables on it.
- [PATTERN] (pre-seeded) Units/currency drift -- mixed scale (thousands vs millions)
  or currency/FX or FY-vs-CY mismatch silently 1000xs a figure; one scale + one
  currency + aligned periods, FX rate + date shown.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve in-flight assumptions and
  `_workspace/` state across compaction.
- **PreToolUse disclaimer gate** (domain-unique) -- on Write/Edit to a summary/deck
  or client-facing path, confirm the forward-looking/not-advice notice; advisory by
  default, deterministic for fundraising/M&A output.
- **Stop hook self-review** (optional) -- "do the totals tie out, does the BS
  balance, is every figure sourced, is precision honest?" Keep a re-entry guard.

## Cost / Model Notes

Opus for reasoning-heavy roles (revenue-modeler, scenario-planner,
valuation-expert, model-reviewer); Sonnet for established-pattern roles
(cost-analyst, summary-drafter). Balanced default (compaction 95%, CLAUDE.md ~200).
Cost-conscious: cost-analyst + revenue-modeler drop to Sonnet, keep
valuation-expert + model-reviewer on Opus (valuation judgment and QA are where
errors are most expensive), compaction 85%, full RTK. Quality-first: all reasoning
roles on Opus, widen sensitivity/comparable scope.

## Customization Points

- Business stage (idea/MVP/PMF/scale-up) -- top-down vs bottom-up revenue; DCF vs
  VC-method/Berkus/scorecard valuation.
- Business model (SaaS/marketplace/manufacturing/retail/biotech) -- unit-economics
  formulas, cost drivers, which multiples apply (with reference sanity-bands that
  are recency-sensitive: confirm by current web research).
- Accounting basis (cash vs accrual) and revenue recognition (point-in-time vs
  over-time, ASC 606 / IFRS 15) -- drives whether statement-linked checks apply.
- Macro/rate inputs (Rf, MRP, Kd, size premium) -- re-source as-of the analysis
  date; never take a skill's illustrative ranges as authoritative.
- Math engine -- Markdown tables vs Python/pandas (drives the Python/data permission
  sets; Monte Carlo requires Python).
- Currency, fiscal-year convention, forecast horizon (default 5y: monthly Y1-2,
  annual Y3-5); disclaimer enforcement strength (deterministic for external output).

## Team-architecture pattern

Pipeline with a Producer-Reviewer gate: revenue -> cost -> scenario -> valuation
flows sequentially (each consumes the prior deliverable), then model-reviewer
cross-validates and returns up to two rounds of Must-Fix requests to the relevant
author before summary-drafter produces the investor-facing output (the loop is a
real routing edge, not just prose). The hard data-dependency between phases makes
the subagent default the right fit; Agent Teams are only worth the ~15x cost if an
early-revenue pass and cost can genuinely run in parallel, which is rare since cost
depends on revenue scale.

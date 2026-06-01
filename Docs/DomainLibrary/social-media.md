# Bundled Domain: Social Media Management

Adapted from revfactory/harness-100 10-social-media-manager. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md` (slim).
A starting point the architect adapts -- it points at templates, it does not
inline them.

## Profile Metadata

- **Target audience**: social media managers, content marketers, agencies, and
  brand teams producing content calendars, post copy, visual plans, and hashtag
  strategy across Instagram, TikTok, X/Twitter, LinkedIn, Facebook
- **Primary tools**: web search (trend/algorithm checks), Markdown deliverables,
  optional image-generation tool for visual concepts
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: proactive | **VCS**: optional (Git only if deliverables are versioned)

Scope note (carry into CLAUDE.md): this domain *plans and writes* content. Live
account operations (posting, replies, DMs), paid-ad execution, analytics-API
pulls, and influencer outreach are out of scope -- the assistant drafts, it does
not publish.

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| strategist | opus | Channel analysis, audience personas, content-pillar mix, monthly calendar, campaign design | planner.md |
| copywriter | sonnet | Platform-optimized captions, threads, short-form scripts, CTAs, A/B alternates. Asks "is this sponsored/affiliate/incentivized?" and embeds a clear-and-conspicuous disclosure when yes; never asserts efficacy/health/income claims as fact; marks any hook statistic `[SOURCE NEEDED -- brand to verify]` | drafter.md |
| visual-planner | sonnet | Image concepts, carousel/card-news layouts, Reels storyboards, image-gen prompts. Recommends the platform commercial/royalty-free audio library; does not assume trending-audio clearance for business accounts | custom (visual concept + storyboard planner; reads strategy + copy, writes no code) |
| hashtag-analyst | sonnet | Pyramid hashtag sets, trend/competitor research, shadowban screening, reach prediction. Hashtag counts, competitor metrics, and reach/engagement figures are web-verified-with-source or labeled estimate, never fabricated | researcher.md |
| reviewer | opus | Cross-validate strategy/copy/visuals/hashtags for KPI fit, brand + platform consistency (read-only QA). FAILS posts missing a required FTC disclosure, asserting unsubstantiated claims, newsjacking tragedies, or using unverified-clearance audio (see Brand Safety & Compliance) | reviewer.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy, context-management, self-learning, error-handling, memory-management.
Add `vcs-git.md` only if deliverables are tracked in Git. No sensitive-data rule
unless the brand handles regulated/PII campaigns. **Required domain rule:** a
pinned `brand-safety.md` -- FTC disclosure on sponsored/affiliate/incentivized
posts, claims substantiation, audio/IP clearance, and crisis/brand-safety
guardrails (see Brand Safety & Compliance); the reviewer enforces it.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/content-pipeline` (full
5-stage run, adapt `build.md` as a multi-stage producer), `/review-content`
(adapt `review.md` for the consistency-matrix QA pass); knowledge skills
`platform-algorithms`, `viral-copywriting`, `hashtag-science` (specialist
reference packs the strategist/visual-planner, copywriter, and hashtag-analyst
load on demand -- adapt `map-codebase.md` progressive-disclosure shape: thin
SKILL.md + `references/`).

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | "Create SNS content" / full management | /content-pipeline (all 5 agents) | Gather brand, platforms, period, goals first | intake (if brand info thin) |
| 2 | "Build a content calendar" | strategist -> reviewer | Pillar mix + posting cadence + KPIs | answer directly (single week, simple) |
| 3 | "Write Instagram captions / posts" | copywriter -> hashtag-analyst -> reviewer | Read strategy first; enforce char limits; ask sponsored/affiliate? -> embed disclosure; mark hook stats `[SOURCE NEEDED]` | copywriter only (one-off post) |
| 4 | "Write an X/Twitter thread" | copywriter | Hook tweet + RT-worthy body + self-reply link; same disclosure/claims discipline | answer directly (single tweet) |
| 5 | "Write a TikTok / Reels script" | copywriter -> visual-planner | 3-sec hook, loop structure, text overlay; trending audio is NOT assumed cleared for business -> use platform commercial library | copywriter only |
| 6 | "Plan the visuals / carousel / storyboard" | visual-planner | Needs copy + specs; emits image-gen prompts | strategist (if no brand guide) |
| 7 | "Analyze / build hashtag sets" | hashtag-analyst -> reviewer | Pyramid tiers, shadowban screen, web-verify trends | answer directly (a few obvious tags) |
| 8 | "Which posting times / how often" | strategist (load platform-algorithms) | Golden hours + frequency table per platform | answer directly (well-known) |
| 9 | "How does the [platform] algorithm work" | answer directly (load platform-algorithms) | Ranking signals, format weights | strategist (if it changes the plan) |
| 10 | "Repurpose this post for other platforms" | copywriter (+ visual-planner if formats differ) | Cross-platform conversion guide | answer directly (trivial trim) |
| 11 | "Review / QA this content" | reviewer | RED/YELLOW/GREEN + consistency matrix; FAIL missing FTC disclosure, unsubstantiated claims, uncleared audio, tragedy newsjacking | answer directly (one short post) |
| 12 | "Design a campaign" (awareness/conversion) | strategist -> copywriter -> hashtag-analyst -> reviewer | Goal-aligned KPIs drive the calendar | clarify goal first |
| 13 | "Use my brand guide / existing calendar" | orchestrator copies to working memory, skips covered stages | Skip strategist if calendar supplied | full pipeline (if guide partial) |
| 14 | "Check the latest trend / what's viral now" | hashtag-analyst or strategist (web search) | Note "trend data limited" if search fails; never fabricate counts/metrics -- web-verify-with-source or label estimate | answer directly (general knowledge) |
| 15 | "Fix the RED items from the review" | reviewer routes to owning agent -> re-verify | Max 2 rework cycles per item | answer directly (copy-edit tweak) |
| 16 | "Here are my last month's metrics / paste of analytics" | strategist/hashtag-analyst interpret the pasted figures | Use ONLY the numbers the user supplied; do not invent or back-fill missing rows; label any benchmark/estimate as such | clarify (if the paste is ambiguous or partial) |

Complexity scaling: Simple (1 agent or direct answer -- single post, one hashtag
set, an algorithm question) | Standard (2-3 agents serial -- captions + hashtags
+ review, calendar + review) | Complex (full /content-pipeline, 5 agents with a
parallel copy+hashtag stage and a reviewer rework loop).

## Brand Safety & Compliance

Published social content carries real regulatory and reputational exposure for the
brand. These are not optional for the domain; the reviewer enforces them and the
`brand-safety.md` rule is pinned:

- **FTC disclosure (sponsored/affiliate/incentivized content):** before writing any
  post, the copywriter asks "is this sponsored, a paid partnership, an affiliate
  link, or otherwise incentivized?" If yes, embed a clear-and-conspicuous disclosure
  -- `#ad`, `#sponsored`, the platform's "Paid partnership" label, or "I may earn a
  commission" -- placed where viewers see it before they engage (not buried at the
  end of a hashtag block, not behind a "more" cut). The reviewer FAILS any post that
  needs a disclosure and lacks one.
- **Claims substantiation:** never assert efficacy, health, medical, weight-loss,
  income, or investment-return outcomes as fact. Any statistic or number used in a
  hook is marked `[SOURCE NEEDED -- brand to verify]` rather than fabricated. Apply
  extra caution to regulated categories (health, finance, supplements) -- prefer
  qualified phrasing ("may", "some users report") and defer hard claims to the brand.
- **Audio / music / IP clearance:** trending audio or music is NOT assumed
  commercially cleared for a business/creator account. Recommend the platform's
  commercial/royalty-free library (or a track the brand already licenses); flag any
  request to reuse third-party images, logos, or copyrighted text for brand sign-off.
- **Crisis / brand-safety:** no newsjacking of tragedies, disasters, or active crises.
  Flag divisive or political hooks for brand sign-off rather than shipping them, and
  check the brand's prohibited-expression list (from the brand guide) before writing.
- **Accuracy / no fabrication:** hashtag counts, competitor metrics, and
  reach/engagement figures are web-verified-with-source or explicitly labeled an
  estimate -- never invented. Algorithm signal-weight tables are labeled "directional
  heuristics, not published weights" with a freshness/date stamp.
- **Platform-terms integrity:** never recommend engagement manipulation -- engagement
  pods, buying followers/likes, or follow-unfollow churn all violate platform terms
  and risk the account. Recommend organic-growth tactics instead.

## Ecosystem Permissions

Base + Universal Deny -- see `Docs/Templates/References/ecosystem-permissions.md`.
This domain is content-not-code: no language ecosystem is needed by default. Add
`Git` only if deliverables are versioned. Allow `WebSearch` / `WebFetch(*)` (in
Base) for trend and algorithm checks. Pre-approve the deliverable output path so
the agents do not prompt on every write:

```json
{ "permissions": { "allow": ["Edit(./Docs/_working/content/**)", "Write(./Docs/_working/content/**)"] } }
```

If an image-generation tool is wired in (see Customization Points), add only its
specific CLI/MCP allow rule -- never a blanket external-network allow.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Copy ignores the strategy -- copywriter writes before
  reading the calendar, so tone/pillar drift. Mitigation: copywriter reads
  01_strategy first; reviewer flags pillar-ratio mismatch.
- [PATTERN] (pre-seeded) Char-limit overruns -- captions/tweets exceed platform
  caps. Mitigation: enforce limits at write time (X 280, IG ~150-300 rec,
  LinkedIn 500-1000 rec); keep trimmed text as an "extended version".
- [PATTERN] (pre-seeded) Stale algorithm/trend claims -- frequency and golden-hour
  guidance ages fast. Mitigation: web-verify before stating; tag unverifiable
  claims "trend data limited" rather than asserting.
- [PATTERN] (pre-seeded) Shadowban-risk hashtags slip in -- banned/over-broad tags
  hurt reach. Mitigation: hashtag-analyst screens each set; reviewer rejects
  unrelated mega-tags and repeated identical sets (rotate 30%+ per post).
- [PATTERN] (pre-seeded) Scope creep into publishing -- user asks the assistant to
  post or reply. Mitigation: state the plan-not-publish scope, hand back
  copy-paste-ready deliverables instead.
- [PATTERN] (pre-seeded) Reviewer rework loops forever -- RED items bounce between
  agents. Mitigation: cap at 2 rework cycles per item, then ship with the issue
  noted in the report.
- [PATTERN] (pre-seeded) Missing FTC disclosure on paid/affiliate/incentivized posts
  -- sponsored content ships without #ad or a Paid-partnership label. Mitigation:
  copywriter asks the sponsored/affiliate/incentivized question first and embeds a
  clear-and-conspicuous disclosure; reviewer FAILS any post that needs one and lacks it.
- [PATTERN] (pre-seeded) Fabricated or unsubstantiated claims -- efficacy/health/
  income/investment outcomes asserted as fact, or a hook statistic invented.
  Mitigation: never state regulated outcomes as fact; mark any hook number
  `[SOURCE NEEDED -- brand to verify]`; extra caution for health/finance/supplements.
- [PATTERN] (pre-seeded) Uncleared trending audio assumed safe for a business account
  -- a viral sound is dropped into a brand Reel as if licensed. Mitigation:
  visual-planner recommends the platform commercial/royalty-free library; flag
  third-party images/logos/text for brand sign-off.
- [PATTERN] (pre-seeded) Newsjacking or off-brand hooks -- content piggybacks a
  tragedy or wades into a divisive/political topic. Mitigation: no tragedy/disaster
  newsjacking; flag divisive/political hooks for brand sign-off; check the brand
  prohibited-expression list.
- [PATTERN] (pre-seeded) Fabricated metrics / unlabeled algorithm weights -- hashtag
  counts, competitor numbers, or reach figures invented; signal-weight tables stated
  as published fact. Mitigation: web-verify-with-source or label an estimate; label
  algorithm tables "directional heuristics, not published weights" + date stamp.
- [PATTERN] (pre-seeded) Engagement manipulation suggested -- pods, buying followers,
  follow-unfollow churn. Mitigation: these violate platform terms and risk the
  account; recommend organic-growth tactics instead.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserves the brand brief, calendar,
  and in-flight deliverables across compaction. See
  `Docs/Templates/Optional/hooks-template.md`.
- Optional **Stop hook content-check** -- a light prompt-type hook that warns if a
  draft caption looks over the platform char limit, or if a post flagged sponsored/
  affiliate has no disclosure token (#ad, "Paid partnership"). Not deterministic;
  advisory only. Skip for solo casual use. For agencies with hard FTC-compliance
  obligations, the architect may make the disclosure check a PreToolUse gate that
  blocks deliverable writes lacking a disclosure when the post is marked sponsored.

## Cost / Model Notes

Opus for strategist and reviewer (audience reasoning, campaign design,
cross-deliverable QA judgment); Sonnet for copywriter, visual-planner, and
hashtag-analyst (established-pattern execution -- hook templates, spec tables,
pyramid tiers). Defaults: balanced (Opus on reasoning roles, Sonnet on execution;
compaction 95%; CLAUDE.md ~200 lines). Cost-conscious override: all-Sonnet with
reviewer still verifying, compaction 85%, full RTK in GETTING_STARTED. The full
/content-pipeline is the expensive path (5 agents + rework loop) -- reserve it for
"full management" requests; route single-deliverable asks to 1-2 agents.

## Customization Points

Platforms in scope (drives copy limits, specs, hashtag counts, algorithm packs);
posting cadence and time zone; brand guide present or to-be-defined (tone,
colors, fonts, prohibited expressions); image-generation tool wired in or
prompt-only output (capability gap -- see `Docs/Templates/References/tool-registry.md`
and topic 23 multi-modal selection); KPI focus (awareness / engagement /
conversion / community); regulated or PII campaigns (-> add sensitive-data rule);
sponsored/affiliate content expected (-> disclosure discipline, optionally a
deterministic disclosure gate); regulated product category -- health / finance /
supplements / alcohol (-> stricter claims-substantiation handling).

## Team-architecture pattern

Pipeline with a Producer-Reviewer tail: strategist -> (copywriter || hashtag-analyst
in parallel) -> visual-planner -> reviewer, where the reviewer loops fixes back to
the owning producer. The parallel copy+hashtag stage and the cross-validating
reviewer make the full pipeline the one phase that can justify Agent Teams
(harness-100 ran it as a 5-member team with direct messaging) over the subagent
default -- but only for genuine "full management" runs; single-deliverable
requests stay on cheaper serial subagents.

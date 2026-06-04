# Bundled Domain: Customer Support

Adapted from revfactory/harness-100 49-customer-support. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md` (slim)
-- a starting point the architect adapts; it points at templates, it does not
inline them.

This domain builds customer-support *documentation systems*: FAQs, response
manuals, escalation policies, and CS analytics frameworks. It is document-centric
knowledge work, not software -- no CRM/helpdesk development, no live chatbot, no
call-center infrastructure.

**Audience framing:** these deliverables are not internal notes. The FAQs,
scripts, manuals, and escalation copy this environment produces get READ TO REAL
CUSTOMERS -- by agents on a call, pasted into a reply, or published as
self-service help. So every customer-facing factual claim must be safe and
grounded in a user-supplied authoritative source, and every monetary/SLA/legal
commitment is a policy decision the human owner approves, not a value the
assistant settles. The assistant drafts; a human owner reviews and adopts before
anything reaches a customer.

## Profile Metadata

- **Target audience**: CS leads, support-ops managers, customer-experience teams
  standing up or improving a support knowledge base
- **Primary tools**: Markdown deliverables; web search/browser retrieval (grounding against
  the user's published policy/help pages); MarkItDown (inbound docs), Pandoc
  (outbound .docx/.pdf) when formatted handoffs are needed
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**:
  conservative (confirm before overwriting an existing FAQ/manual; never assert a
  policy/product fact without a source; mark every commitment [PROPOSED]) | **VCS**: None

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| faq-builder | medium-effort | Build categorized FAQs; map customer search language; 80/20 coverage; ground every factual answer in a user-supplied source, bracket unknowns [VERIFY] | drafter.md |
| response-specialist | medium-effort | Write scenario scripts, tone-and-manner guide, channel + emotional-response protocols; insert identity-verification + safety-critical routing where required | drafter.md |
| escalation-manager | high-effort | Design L1-L4 tiers, routing/trigger matrix, SLAs, crisis + breach protocols, authority matrix -- monetary/SLA values as [PROPOSED -- requires owner approval] | custom (policy design; closest planner.md) |
| cs-analyst | high-effort | Define CSAT/NPS/CES/FCR/AHT metrics, VOC framework, reporting/dashboard design; benchmark numbers as [PROPOSED] | analyst.md |
| cs-reviewer | high-effort | Cross-validate FAQ <-> manual <-> escalation <-> analytics; audit grounding, [PROPOSED] markers, identity-verification gates, safety-critical routing; customer-journey simulation (read-only) | reviewer.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (conservative), context-management, self-learning, error-handling,
memory-management. No VCS rule. Add `Optional/output-styles-template.md` (brand
voice + channel tone) since deliverables are customer-facing. **Required domain
rules:** (1) a pinned grounding-and-commitments rule (every customer-facing fact
sourced; unknowns bracketed [VERIFY]; commitments [PROPOSED]; safety-critical
escalation pre-empts business tiers -- see Safeguards); (2) `sensitive-data-rule.md`
-- customer PII and transcripts are Confidential/Restricted by default (see
Safeguards).

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/build-cs-system` (full
pipeline, adapt `build.md`), `/csat-analyze` (metric design + VOC, custom),
`/escalation-design` (tier/SLA/crisis flowchart, custom); conditional
`/process-inbox` (`process-inbox.md`) when users drop existing FAQs/manuals to
revise (treat ingested tickets/transcripts as Confidential -- see Safeguards).

## Domain Routing Table

The orchestrator NEVER asserts a policy or product fact (refund window, fee, SLA,
eligibility, contractual term, feature behavior) from memory -- it grounds it in a
user-supplied source or brackets it [VERIFY]. Any message that smells
safety-critical (row 0) pre-empts every business tier below.

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 0 | SAFETY-CRITICAL signal in any input/scenario (self-harm/suicide; threat-to-others / CSAM; medical emergency / physical danger) | escalation-manager (safety-critical class, ABOVE all business tiers) | self-harm -> immediate human + crisis-line referral; threat/CSAM -> immediate human + preserve-and-report; medical/danger -> immediate human. Never auto-resolve, never queue by SLA | none -- always a human; do not script around it |
| 1 | "Build a customer support system" / full CS setup | faq-builder + response-specialist (parallel) -> escalation-manager -> cs-analyst -> cs-reviewer | Capture service type, channels, team size, scale, AND authoritative policy/ToS/spec sources first | intake (if service info too thin -> generic template, tag "needs customization") |
| 2 | "Write / expand our FAQ" | faq-builder -> cs-reviewer | 80/20; customer search language; every factual answer cites a source or is bracketed [VERIFY] | answer directly (single Q&A, only if sourced) |
| 3 | "Create a response manual / agent scripts" | response-specialist -> cs-reviewer | Empathize -> Confirm -> Resolve -> Verify; frameworks not word-for-word; insert identity-verification step before any disclosure/account-change script | faq-builder first (if FAQ scope undefined) |
| 4 | "Design an escalation policy" | escalation-manager -> cs-reviewer | L1-L4 tiers, trigger matrix, SLA by priority, handoff standard; authority limits as [PROPOSED] | /escalation-design (methodology only) |
| 5 | "Set up CS metrics / KPIs / a dashboard" | cs-analyst | CSAT/NPS/CES/FCR/AHT; every metric leads to action ("So what?"); benchmark targets [PROPOSED] | /csat-analyze (methodology only) |
| 6 | "Analyze our VOC / customer feedback" | cs-analyst | Sentiment + topic + severity; trends WoW; strip customer PII from examples (opaque IDs) | answer directly (one-off sentiment read, deidentified) |
| 7 | "Define / tune our SLAs" | escalation-manager | Priority P1-P4 targets; tier by customer grade; numeric targets [PROPOSED -- owner approval] | cs-analyst (if SLA must be measurable) |
| 8 | "Crisis / outage response plan" | escalation-manager | SEV-1 availability protocol: T+0/15/30/60, status-page notice, post-mortem; public copy is DRAFT-only, "legal/PR review required before sending" | response-specialist (customer-facing notice wording, same DRAFT marker) |
| 9 | "Review / audit our CS docs for consistency" | cs-reviewer | FAQ<->manual<->escalation<->analytics matrix; audit grounding, [PROPOSED] markers, ID-verification gates, safety routing; 3 journey simulations | answer directly (single short doc) |
| 10 | "Improve a low CSAT / FCR / high AHT metric" | cs-analyst (diagnose) -> response-specialist or faq-builder (fix) | Low FCR -> strengthen FAQ/KB; high AHT -> macros/templates | answer directly (well-known lever) |
| 11 | "Set our brand voice / tone for support" | response-specialist | Recommended vs prohibited expressions; per-channel tone | answer directly (single tone tweak) |
| 12 | "Onboarding material for new agents" | response-specialist | First-week essentials + role-play scenarios | faq-builder (knowledge-base side) |
| 13 | "Revise this existing FAQ/manual I'm attaching" | /process-inbox (MarkItDown convert) -> relevant builder -> cs-reviewer | Copy into workspace; treat tickets/transcripts as Confidential; skip that build phase | answer directly (plain-text snippet, deidentified) |
| 14 | "Produce a .docx/.pdf of the final package" | drafter-role agent -> Pandoc convert | Pandoc required; falls back to Markdown; do not export until [PROPOSED]/[VERIFY] markers are resolved or owner-approved | answer directly (Markdown handoff) |
| 15 | Regulated-vertical script request (financial, health/insurance, utilities, telecom, safety) | escalation-manager (boundary check) -> qualified human / compliance-reviewed template | Do NOT script regulated legal/medical/financial advice; provide process + handoff copy only | clarify the vertical, then route to a human reviewer |
| 16 | Vulnerable-customer handling (distressed, minor, disability/accessibility, elderly, language barrier) | response-specialist (vulnerable-customer protocol) + escalation-manager (human-handoff path) | Slower pace, plain language, no upsell/retention scripting; escalate to a trained human, not a self-service loop | row 0 if any safety signal appears |
| 17 | Personal-data breach (customer data exposed/leaked/unauthorized access) | escalation-manager (breach class -> DPO/legal/security) | DISTINCT from an availability SEV-1: GDPR 72h-to-authority clock + notify-affected clock; preserve evidence; public copy DRAFT-only, legal review | row 8 only if it is an availability outage with no data exposure |
| 18 | DSAR / privacy request (access, deletion, correction, opt-out) | escalation-manager -> data-protection owner | Verify requester identity first; route to the data-protection owner; honor statutory deadlines; do not auto-fulfill in a script | clarify the request type, then route |

Complexity scaling: Simple (1 agent / direct: single sourced FAQ entry, one tone
fix, one metric explanation) | Standard (1 builder + reviewer: a FAQ, a manual, an
escalation policy) | Complex (parallel build + serial review: full CS system,
cross-doc audits, metric-driven redesign). Safety-critical (row 0), breach (17),
and DSAR (18) routing always overrides the complexity tier -- never collapse them
into a direct answer.

## Ecosystem Permissions

Base + Universal Deny -- see `Docs/Templates/References/ecosystem-permissions.md`.
This is a document workflow with **no language ecosystem and no VCS**: deny the
programming tool families (`pip`, `npm`, `node`, `python`, `go`, `cargo`) as the
Knowledge Work profile does, and allow only safe text utilities (`wc`, `sort`,
`diff`, `date`, `ls`, `find`, `head`, `tail`). Allow `scoped writes` to `Docs/**`
and an `Outbox/**` deliverable folder. **Keep web search and browser/web retrieval (in
Base) enabled** -- they are the grounding mechanism for verifying a customer-facing
fact against the user's published policy/ToS/help pages; without them every fact
is an unsourced assertion. Document `pandoc` only if Pandoc is installed;
prefer the MarkItDown MCP server over enabling Python for inbound conversion.
Generate `local config profile` for machine-specific tool paths.

## Safeguards (grounding, commitments, safety, sensitive data)

Customer-facing copy carries real liability -- a wrong refund window, a fabricated
fix-date, an account disclosure to the wrong person, a missed crisis signal. These
are not optional for the domain:

- **Grounding (pinned domain rule):** every customer-facing factual claim --
  refund/return windows, fees, SLAs, eligibility, legal/contractual terms, feature
  behavior -- must be grounded in a user-supplied authoritative source (policy,
  ToS, product spec, KB). Unknowns are bracketed `[VERIFY]`, never asserted. Do
  NOT fabricate a policy or product fact. On a grounding gap, surface `[VERIFY]`
  and the question; do not paper over it with a plausible-sounding default.
- **Commitments are policy decisions, not values to settle:** monetary authority
  limits (refund/comp ceilings), compensation criteria, SLA targets, and analytics
  benchmark numbers render ONLY as clearly-marked `[PROPOSED -- requires owner
  approval]` placeholders -- never as settled figures. Never state delivery dates,
  fix ETAs, or roadmap commitments in customer-facing copy without an authoritative
  source. Any such defaults (e.g. "refunds up to $X", "first response 15 min")
  are template slots, not approved policy.
- **Safety-critical class (pre-empts all business tiers):** self-harm/suicide ->
  immediate human + crisis-line referral; threat-to-others / CSAM -> immediate
  human + preserve-and-report; medical emergency / physical danger -> immediate
  human. These never get auto-resolved, queued by SLA, or scripted to a
  self-service loop. A vulnerable-customer path (distressed/minor/disabled/elderly/
  language-barrier) routes to a trained human, not a retention or upsell script.
- **Regulated-advice boundary:** scripts/FAQ for regulated verticals (financial,
  health/insurance, utilities, telecom, safety) must NOT script regulated legal,
  medical, or financial advice. Provide process and handoff copy; route the
  substance to a qualified human or a compliance-reviewed template.
- **Identity verification:** any generated script or escalation tier that DISCLOSES
  account data or PERFORMS an account-changing action (refund, cancellation,
  address/email change, password reset) must require step-up identity verification
  FIRST. cs-reviewer fails any disclosure/account-action script missing the gate.
- **Sensitive data (`sensitive-data-rule.md`, required):** classify Public
  (published help content), Confidential (customer name/contact/account
  identifiers, ticket transcripts), Restricted (PCI payment data, health). EXCLUDE
  customer PII from `Docs/_working/retro/`, `/state-save`, and PreCompact summaries
  -- store an opaque ticket-ID / customer-ID, not the person. Special categories:
  payment data -> mask to last 4, keep on a PCI channel, NEVER write a full PAN or
  CVV into a transcript; health data -> Art.9 / possible HIPAA, minimize and
  isolate. Real customer PII never gets embedded in a deliverable or an example --
  use synthetic placeholders.
- **Destructive troubleshooting + public comms:** any troubleshooting step that can
  cause data loss or a factory reset carries a warning, a backup-first instruction,
  and an explicit customer confirmation. Crisis/outage public communications and
  any apology or compensation language ship DRAFT-only, marked "legal/PR review
  required before sending".
- **Breach vs outage:** a personal-data breach (customer data exposed) is NOT an
  availability SEV-1. Breach -> DPO/legal/security escalation, GDPR 72h-to-authority
  clock plus notify-affected clock, preserve evidence. Outage -> availability SEV-1
  protocol. DSAR/privacy requests (access/deletion/correction/opt-out) -> verify
  identity, route to the data-protection owner, honor statutory deadlines.
- **Enforcement:** grounding and the [PROPOSED]/identity-verification/safety checks
  are advisory-by-default and audited by cs-reviewer; the optional PreToolUse PII
  gate (below) can be upgraded to deterministic for environments handling real
  customer data. See Customization for the enforcement-strength knob.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) FAQ uses internal jargon -- answers reference product/team
  terminology instead of the words customers actually search for. Mitigation:
  faq-builder maps customer search language and synonyms before writing answers.
- [PATTERN] (pre-seeded) Scripts written word-for-word -- response-specialist produces
  rigid scripts agents read verbatim. Mitigation: frame scripts as frameworks on the
  Empathize -> Confirm -> Resolve -> Verify flow, not exact wording.
- [PATTERN] (pre-seeded) Doc drift across deliverables -- escalation triggers in the
  manual do not match the escalation policy, or SLA items are not measurable in the
  analytics framework. Mitigation: always run cs-reviewer cross-validation before
  declaring a package done.
- [PATTERN] (pre-seeded) Vanity metrics -- cs-analyst defines metrics with no owner or
  action. Mitigation: every metric needs a target, a benchmark, and a "So what?"
  action lever (low FCR -> strengthen FAQ; high AHT -> macros).
- [PATTERN] (pre-seeded) Thin service input -> over-generic output. Mitigation: when
  service type/channels/scale are missing, build from an industry template and tag
  sections "requires service customization" instead of guessing specifics.
- [PATTERN] (pre-seeded) Overwriting a user's existing FAQ/manual -- conservative
  default missed. Mitigation: route attached existing docs through /process-inbox and
  write revisions to Outbox/, never over the original.
- [PATTERN] (pre-seeded) Fabricated policy/product fact -- a refund window, fee, SLA,
  eligibility rule, or feature behavior asserted without a source. Mitigation: ground
  every customer-facing fact in a user-supplied policy/ToS/spec/KB; bracket unknowns
  [VERIFY]; never invent a plausible default.
- [PATTERN] (pre-seeded) Commitment stated as settled -- a refund ceiling, comp
  amount, SLA target, or benchmark written as a final value. Mitigation: render all
  such numbers as [PROPOSED -- requires owner approval]; never settle policy in copy.
- [PATTERN] (pre-seeded) Account-action / disclosure script with no identity check --
  a refund, cancellation, contact change, password reset, or data-disclosure flow
  written without a step-up verification step first. Mitigation: insert the
  identity-verification gate before disclosure/account-change; cs-reviewer fails it
  otherwise.
- [PATTERN] (pre-seeded) Real customer PII in a deliverable/example -- a real name,
  email, phone, card number, or transcript embedded in an FAQ, script, or sample.
  Mitigation: use synthetic placeholders; keep real PII out of deliverables and out
  of retro/state/PreCompact (opaque IDs only).
- [PATTERN] (pre-seeded) Regulated advice scripted for a regulated vertical --
  financial/health/insurance/utility/telecom/safety substance written as a customer
  script. Mitigation: stop at process + handoff copy; route the advice to a qualified
  human or a compliance-reviewed template.
- [PATTERN] (pre-seeded) Safety-critical message not routed to a human -- a self-harm,
  threat, CSAM, or medical-emergency signal handled by an SLA tier or self-service
  loop. Mitigation: row 0 safety class always goes to an immediate human (plus
  crisis-line / preserve-and-report as applicable), above every business tier.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve current deliverable, service
  facts, sources, and review findings before compaction; EXCLUDE customer PII
  (opaque ticket/customer-ID only). See `Docs/Templates/Optional/hooks-template.md`.
- **PreToolUse PII-content gate** (domain-unique, optional, advisory-by-default):
  on `scoped writes` to `Docs/**` and `Outbox/**`, scan content against
  `.codex/hooks/pii-patterns.conf` (email, phone, card_number, SSN/national ID,
  postal address). Warns when a real-looking PII string lands in a deliverable.
  Upgrade to deterministic (block, not warn) for environments that handle real
  customer data -- see Customization. Template in `hooks-template.md`.
- No Stop self-review hook (not code-producing); the cs-reviewer agent is the
  quality gate instead.

## Cost / Model Notes

GPT-5.5 for the reasoning/judgment roles -- escalation-manager (policy design),
cs-analyst (metric reasoning), cs-reviewer (cross-validation + safeguard audit).
medium-effort GPT-5.5 for the established-pattern drafting roles -- faq-builder,
response-specialist. Defaults: balanced (high-effort GPT-5.5 on reasoning, medium-effort GPT-5.5 on drafting;
compaction 95%; AGENTS.md ~200 lines). Cost-conscious override: all medium-effort GPT-5.5 except
cs-reviewer on GPT-5.5 (it owns the safeguard audit, so do not downgrade it),
compaction 85%, AGENTS.md ~150, brief `/cost` + RTK mention in GETTING_STARTED.
CS sessions are document-length, so subagent fan-out (full-system build) is the
main cost driver (~4x vs direct); a full package touches all five agents once.

## Customization Points

Service type + customer-base scale (drives FAQ depth and benchmark targets);
active channels (phone/chat/email/social -> per-channel SLA + tone rows); org size
(2-tier L1-L2 SMB vs 4-tier L1-L4 enterprise escalation); brand voice defined or
not (-> output-styles tone guide); existing FAQ/manual to extend (-> /process-inbox
+ MarkItDown); formatted .docx/.pdf delivery needed (-> Pandoc, otherwise
Markdown-only); regulated vertical(s) in scope (-> tighten the row-15 boundary and
name the compliance reviewer); **enforcement strength** (advisory cs-reviewer audit
vs deterministic PreToolUse PII gate -- ask "will this handle real customer data --
ticket transcripts, VOC exports, live tickets?"; if yes, turn on
`sensitive-data-rule.md` classification with the deterministic gate and a populated
`pii-patterns.conf`).

## Team-architecture pattern

Fan-out / Fan-in feeding a terminal Producer-Reviewer stage: faq-builder and
response-specialist run in parallel (no initial dependencies), then
escalation-manager and cs-analyst layer on their outputs serially, and cs-reviewer
fans everything in for cross-validation (rework loop up to 2 passes) -- it also owns
the safeguard audit (grounding, [PROPOSED] markers, identity-verification gates,
safety-critical routing). Subagents are the default and sufficient. Agent Teams
(with direct SendMessage) are only worth it for a true full-system build where the
two parallel builders benefit from exchanging the self-service boundary and
escalation triggers live -- otherwise the file-based `_workspace/` handoff through
the orchestrator is cheaper.

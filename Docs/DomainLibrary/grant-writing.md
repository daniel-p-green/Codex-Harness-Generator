# Bundled Domain: Grant Writing

Adapted from revfactory/harness-100 54-grant-writer. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim). A starting point the architect adapts -- it points at templates, it does
not inline them.

**Audience framing:** this seeds a tool FOR grant professionals (writers,
development officers, PIs) producing draft applications. Every applicant-asserted
fact of record (outcomes, metrics, credentials, prior awards, partner
commitments) originates with the applicant or is marked [APPLICANT TO VERIFY] --
fabricated facts in a submitted federal application carry grant-fraud and US
False Claims Act exposure (see Safeguards). The tool drafts; the applicant
attests.

## Profile Metadata

- **Target audience**: grant writers, development officers, founders, lab PIs,
  and consultants preparing competitive applications for government, foundation,
  and corporate funding programs
- **Primary tools**: Markdown deliverables, web research, Pandoc/MarkItDown for
  document I/O (no programming language)
- **Complexity**: Standard | **Memory tier**: Lite (solo) or Standard (2-5 team)
  | **Action default**: conservative (confirm before overwriting submission
  drafts; never assert eligibility/compliance without sourcing the rule) | **VCS**: None

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| solicitation-analyst | high-effort | Dissect the funding announcement: eligibility, scored criteria, keywords, deadlines | researcher.md (custom: web research + criteria extraction, read-only) |
| proposal-writer | medium-effort | Draft the narrative (need, approach, capability, outcomes) tuned to the rubric | drafter.md |
| budget-designer | medium-effort | Build line items, match/cost-share, ceilings, justification | analyst.md (custom: budget tables, no original-file edits) |
| compliance-checker | high-effort | Cross-validate narrative + budget against the announcement; score-gap analysis | reviewer.md |
| submission-verifier | high-effort | Final QA: completeness, format limits, cross-document consistency (read-only) | reviewer.md (custom: package QA, no edits) |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (conservative), context-management, self-learning, error-handling,
memory-management. No VCS rule (document-centric). **Required domain rules:**
(1) a representation-integrity rule (pinned) -- any applicant-asserted fact of
record originates with the applicant or is tagged [APPLICANT TO VERIFY]; never
fabricate (see Safeguards); (2) `data-handling-rule.md` -- **default-on** for this
domain (applications routinely carry org financials and key-personnel PII,
including SSN/DOB on US federal forms); opt-out only when the user confirms no
sensitive applicant data is involved.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/grant-pipeline` (custom:
orchestrate analyst -> writer/budget -> compliance -> verifier, deliverables to
`Docs/_working/applications/<grant>/`), `/budget-rules` (custom: category
ceilings, match ratios, rate tables, justification templates, **allowability
checklist + narrative-to-budget traceability** -- see routing row 4),
`/score-optimize` (custom: rubric point map, high-score patterns, disqualifier
and bonus checklists); plus `/process-inbox` (process-inbox.md) for converting
inbound solicitation PDFs/DOCX. A **grant-craft methodology reference** ships as
a loadable doc (store under `Docs/Areas/`, load on demand): needs-statement
structure, logic model / theory of change, SMART objectives, evaluation/
measurement plan, evidence and citation discipline, and rubric-section mapping.
Referenced from routing rows 3, 7, and 12.

## Domain Routing Table

The orchestrator NEVER invents an applicant fact of record (an outcome, metric,
credential, degree, prior award, past-performance item, partner commitment, or
organizational-capacity claim). Any such fact comes from the applicant or is
written as [APPLICANT TO VERIFY] -- see Safeguards.

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | Prepare a full application (analyze -> write -> budget -> verify) | /grant-pipeline (all 5 agents serial) | Provide announcement + applicant profile + project idea | clarify (if no announcement) |
| 2 | Analyze this announcement / NOFO / RFP | solicitation-analyst | Extract eligibility, scored criteria, keywords, deadline | answer directly (short, well-known program) |
| 3 | Write / draft the proposal narrative | solicitation-analyst -> proposal-writer | Apply grant-craft reference (needs statement, logic model, SMART objectives); reflect rubric + keywords; cite every claim; applicant facts come from the applicant or are tagged [APPLICANT TO VERIFY] | proposal-writer alone (analysis already on disk) |
| 4 | Build / fix the budget | budget-designer (+ /budget-rules) | Honor category ceilings and match ratios; run the allowability checklist (unallowable costs per 2 CFR 200 Subpart E for US federal awards) and narrative-to-budget traceability (each line item maps to a funded activity) | compliance-checker (if a ratio looks breached) |
| 5 | Will we qualify? / eligibility check | solicitation-analyst (requirements) -> compliance-checker | Mandatory vs. preferred; flag disqualifiers | answer directly (single obvious criterion) |
| 6 | Check compliance against the announcement | compliance-checker | Cross-read narrative + budget vs. rules | submission-verifier (if format-only) |
| 7 | Maximize our score / strengthen weak sections | compliance-checker (+ /score-optimize) -> proposal-writer | Improve highest-ROI scored items first; lean on the grant-craft reference (evaluation plan, evidence discipline) for under-scoring sections | proposal-writer alone (single section) |
| 8 | Final submission check / are we ready to submit | submission-verifier | Completeness, format limits, cross-doc consistency; for US federal, confirm SAM.gov registration is ACTIVE (UEI valid) and Grants.gov account exists, with lead time before the deadline | answer directly (one missing attachment) |
| 9 | Review an existing draft we wrote | compliance-checker -> submission-verifier | Reverse-map draft onto the rubric | answer directly (single paragraph) |
| 10 | Research the funder / past awardees / competition | solicitation-analyst | Prior selection rate, awardee profiles, policy direction | answer directly (one quick fact) |
| 11 | Match funds / cost-share plan | budget-designer (+ /budget-rules) | Cash vs. in-kind split, sourcing, evidence | answer directly (ratio already known) |
| 12 | Tailor / repurpose a prior application for a new program | solicitation-analyst -> proposal-writer | Re-map old narrative to new rubric (grant-craft reference: rubric-section mapping); diff requirements; re-confirm reused applicant facts still hold or re-tag [APPLICANT TO VERIFY] | proposal-writer alone (minor edits) |
| 13 | Build a submission checklist / required-docs list | submission-verifier | Forms, attachments, signatures, validity windows; for US federal include SAM.gov/UEI + Grants.gov readiness | solicitation-analyst (if requirements unread) |
| 14 | Convert / read the solicitation PDF or DOCX | /process-inbox (MarkItDown) -> solicitation-analyst | Inbound document conversion | answer directly (already plain text) |

Harness mode mapping: the source harness's Analysis Mode -> row 2
(solicitation-analyst only); Plan Mode -> row 3 (analyst -> writer ->
compliance); Budget Mode -> rows 4/11 (budget-designer + compliance-checker);
Review Mode -> row 9 (compliance-checker + submission-verifier); Full Pipeline
-> row 1.

Complexity scaling: Simple (1 agent or direct: one criterion, one quick fact,
single-section edit) | Standard (2-3 agents serial: analyze->write, analyze->
eligibility, score-optimize cycle) | Complex (full /grant-pipeline, all 5 agents
with up to 2 compliance revision rounds).

## Safeguards (representation integrity)

A grant application is an attested representation to a funder. Fabricated facts
are not a quality defect -- in a submitted US federal application they are
grant-fraud / False Claims Act exposure for the applicant. This is the domain's
one critical safeguard:

- **No invented facts of record (HARD rule, pinned):** any applicant-asserted
  fact -- a stated outcome, metric, KPI, credential, degree, prior award,
  past-performance item, partner/letter-of-commitment, or organizational-
  capacity claim -- must come from the applicant or be written as
  `[APPLICANT TO VERIFY]`. The assistant NEVER fabricates outcomes, metrics,
  credentials, data, dates, dollar figures, or citations to fill a gap. When a
  required fact is missing, it writes the placeholder and flags it, never a
  plausible-looking number. Market/impact figures cited as external evidence
  carry a source or are tagged `[CITATION NEEDED]` (distinct from applicant
  facts, which need applicant attestation, not a web source).
- **Why placeholders, not guesses:** a reviewer-pleasing invented metric that
  the applicant later cannot substantiate is worse than a visible gap -- it can
  void an award and trigger liability. The placeholder is the safe default.
- **Enforcement:** carried by the pinned representation-integrity rule and the
  pre-seeded PATTERN below; the PreCompact/Stop hooks preserve and re-check
  outstanding `[APPLICANT TO VERIFY]` / `[CITATION NEEDED]` tags so they are
  resolved before a draft is treated as submission-ready. Deterministic hook
  enforcement is available but optional for this domain (the integrity rule +
  verifier QA cover the common case); escalate to a PreToolUse gate only if the
  user wants hard blocking on export.

## Ecosystem Permissions

Base + Universal Deny only -- see `Docs/Templates/References/ecosystem-permissions.md`.
This domain has no language ecosystem; deny programming tools (`pip`, `npm`,
`node`, `python`) as in the knowledge-work pattern. Allow safe text utilities
(`wc`, `diff`, `sort`, `date`) and Pandoc for .docx/.pdf output when installed.
Add writable `Docs/_working/applications/**` so the pipeline writes deliverables
without prompts. Uses web search and browser/web retrieval (in Base) for funder research
and, on US federal submissions, to confirm SAM.gov registration status (UEI) and
Grants.gov readiness from the funder/registration portals. Use the MarkItDown MCP
server (verified) to read inbound PDF/DOCX solicitations without enabling Python.
Generate `local config profile` for machine-specific template or vault paths.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Applicant fact of record fabricated to fill a gap -- an
  outcome, metric, credential, prior award, or partner commitment is written as a
  plausible number/claim instead of sourced from the applicant. This is grant-fraud
  / False Claims Act exposure, not a style issue. Mitigation: any such fact comes
  from the applicant or is tagged [APPLICANT TO VERIFY]; never invent to fill a
  blank; verifier confirms no unresolved tags remain before submission-ready.
- [PATTERN] (pre-seeded) Budget line item has no narrative activity -- a cost
  appears with no funded activity it supports, or an activity in the narrative has
  no budget line. Mitigation: /budget-rules runs narrative-to-budget traceability
  (every line maps to a funded activity) and an allowability check (unallowable
  costs per 2 CFR 200 Subpart E for US federal awards) before the budget is done.
- [PATTERN] (pre-seeded) Narrative drifts from the scored rubric -- proposal-writer
  prose reads well but does not name the announcement's evaluation criteria.
  Mitigation: writer must map each section to a scored item before drafting.
- [PATTERN] (pre-seeded) Eligibility asserted without a sourced rule -- "we qualify"
  stated without citing the announcement clause. Mitigation: every eligibility
  verdict cites the exact requirement text and marks mandatory vs. preferred.
- [PATTERN] (pre-seeded) Budget breaches a category ceiling silently -- totals look
  fine but labor or indirect exceeds the allowed ratio. Mitigation: /budget-rules
  runs a ceiling-compliance check before the budget is considered done.
- [PATTERN] (pre-seeded) Cross-document numbers disagree -- total budget on the
  cover form differs from the budget table. Mitigation: submission-verifier
  cross-checks project name, total, and period across all deliverables.
- [PATTERN] (pre-seeded) Unsourced market/impact claims -- "the market is growing"
  with no figure. Mitigation: require a number plus source, or tag [CITATION NEEDED].
- [PATTERN] (pre-seeded) Deadline math missed -- attachment lead times not counted
  back from the due date. Mitigation: verifier computes a backward timeline from
  the submission deadline.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve announcement analysis,
  rubric map, current draft section, and any outstanding [APPLICANT TO VERIFY] /
  [CITATION NEEDED] tags before compaction. See
  `Docs/Templates/Optional/hooks-template.md`.
- Optional **Stop hook self-review** -- on a completed draft, prompt a quick
  rubric-coverage check plus a scan for unresolved [APPLICANT TO VERIFY] /
  [CITATION NEEDED] tags. Keep a re-entry guard. Not code-producing, so lighter
  than the software-dev variant.

## Cost / Model Notes

GPT-5.5 for solicitation-analyst, compliance-checker, submission-verifier (judgment:
criteria interpretation, score gaps, disqualifier risk); medium-effort GPT-5.5 for
proposal-writer and budget-designer (established-pattern drafting and table
construction). Defaults: balanced (GPT-5.5 on reasoning roles, medium-effort GPT-5.5 on
execution; compaction 95%; AGENTS.md ~200 lines). Cost-conscious override:
analyst stays GPT-5.5, everything else medium-effort GPT-5.5, compaction 85%. Subagents ~4x vs
direct; the full pipeline is the most expensive path -- reserve it for real
submissions, use single-agent modes for analysis or review.

## Customization Points

Funder type (US federal NOFO vs. foundation LOI vs. corporate -- drives rubric,
budget rules, allowability basis, and whether SAM.gov/UEI + Grants.gov
registration applies; the 2 CFR 200 Subpart E allowability checklist is
US-federal-specific, swap in the funder's own cost policy for non-federal
funders); single program vs. recurring portfolio (-> Standard memory, per-grant
folders); sensitive applicant data (financials/PII -> data-handling rule is
**default-on** here; opt out only if no sensitive data; conservative deny on raw
files); grant-craft methodology reference under Areas/ (US-federal logic-model /
SMART-objective framing by default -- re-ground for funders with a different
narrative shape); required output format (.docx/.pdf via Pandoc, page/word
limits); reusable boilerplate library (org capability, bios, past performance ->
Areas/; reused applicant facts still need attestation per Safeguards); team vs.
solo (team -> shared rubric and boilerplate, multi-role).

## Team-architecture pattern

Pipeline (analyze -> draft + budget -> compliance -> verify) with an embedded
Producer-Reviewer loop: compliance-checker reviews the writer/budget output and
can send up to two revision rounds before submission-verifier does final QA.
Subagents are the default and fit the strictly serial, single-application
workflow; Agent Teams are only worth the ~15x cost when one operator runs
several distinct applications in parallel with non-overlapping deadlines.

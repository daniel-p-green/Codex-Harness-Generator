# Bundled Domain: Hiring Pipeline

Adapted from revfactory/harness-100 90-hiring-pipeline. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim). A starting point the architect adapts -- it points at templates, it does
not inline them.

**Audience framing:** this seeds a decision-SUPPORT tool FOR hiring
professionals (recruiters, talent-acquisition leads, hiring managers, HR
business partners, founders) designing a structured hiring process. It produces
structured **DRAFTS** -- competency rubrics, question banks, scorecards, score
summaries -- that a named human hiring decision-maker must independently review,
correct, and OWN before any use. It NEVER makes a hire/no-hire decision, never
finalizes a rejection, never auto-screens-out a candidate, and does not provide
legal advice. Every adverse action (screen-out, no-hire, rejection) is a human
duty. This is the highest-regulation domain in the library; the Safeguards
section is not optional.

## Profile Metadata

- **Target audience**: recruiters, talent acquisition leads, hiring managers,
  HR business partners, and founders designing a structured hiring process for
  one or more open roles (JD through offer)
- **Primary tools**: Markdown deliverables, web research (market salary,
  competitor JDs, sourcing channels), Pandoc/MarkItDown for document I/O
  (no programming language)
- **Complexity**: Standard | **Memory tier**: Lite (single role) or Standard
  (recurring req portfolio / 2-5 team) | **Action default**: conservative
  (confirm before overwriting a JD or offer draft; never assert a salary band,
  legal-compliance point, or candidate verdict without sourcing it; never
  finalize an adverse action without a recorded human reviewer) | **VCS**: None

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| jd-writer | medium-effort | Job analysis, competency definition, internal JD + external posting, assessment-criteria plan (every criterion mapped to a bona fide job competency) | drafter.md |
| sourcing-specialist | medium-effort | Channel strategy, Boolean search, outreach templates, lawful sourcing-reach plan, sourcing KPIs | drafter.md (custom: channel + outreach drafting, web research) |
| screening-expert | high-effort | Resume/portfolio rubric, take-home design, phone-screen guide, scorecard -- redacts bias-correlated fields, fixes rubric + weights before any candidate, scores each candidate independently against anchored levels with a job-related rationale per score | analyst.md (custom: bias-controlled rubric + funnel design) |
| interview-designer | high-effort | Structured-interview design, STAR/BEI competency questions, interviewer guide, evaluation form, ADA-accommodating formats | planner.md (custom: interview structure + scorecards) |
| offer-coordinator | high-effort | Evidence SYNTHESIS to support a human decision (no verdict), comp package, offer-letter draft, negotiation guide, pipeline consistency QA (read-only) | reviewer.md (custom: decision-support synthesis + offer drafting) |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (conservative), context-management, self-learning, error-handling,
memory-management. No VCS rule (document-centric). **Required domain rules:**
(1) a pinned adverse-decision/fairness rule (template: `Optional/adverse-decision-rule.md`) -- the assistant produces decision-support drafts only,
never an automated adverse action, and prepends the disclaimer to every offer
letter, rejection note, and screening-criterion deliverable; (2)
`sensitive-data-rule.md` -- candidate material is Restricted by default (see
Safeguards). This REPLACES the generic data-handling rule.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/hiring-pipeline` (custom:
orchestrate jd-writer -> sourcing + screening (parallel) -> interview ->
offer, deliverables to `Docs/_working/reqs/<req-id>/`), `/competency-model`
(custom: 3-tier competency framework, L1-L5 proficiency levels, screening
matrix -- every criterion job-related; jd-writer + screening-expert extension),
`/interview-scorecard` (custom: structured-interview design, BEI/STAR question
banks, 4-point scorecard, full protected-inquiry checklist -- interview-designer
extension); plus `/process-inbox` (process-inbox.md) for converting inbound
resumes/JDs in PDF/DOCX with a mandatory redaction step (see below).

## Domain Routing Table

The orchestrator NEVER emits a hire/no-hire verdict, an ordinal candidate
ranking presented as a decision, or a finalized rejection -- those route to
human ownership. Agent output is decision-support only.

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | Design the full hiring process for a role (JD -> sourcing -> screening -> interview -> offer) | /hiring-pipeline (all 5 agents) | Provide role, level, team context, comp range, timeline | clarify (if role undefined) |
| 2 | Write / draft the job description | jd-writer (+ /competency-model) | Internal JD + external posting; tone differentiated; no protected-class proxies | answer directly (minor edit to existing JD) |
| 3 | Define the competencies / skill matrix for a role | jd-writer (+ /competency-model) | 3-tier model, L1-L5 indicators, 5-8 competencies; each a bona fide job requirement | answer directly (one competency) |
| 4 | Build a sourcing strategy / where do we find candidates | sourcing-specialist | Channel mix, cost-per-hire, lawful reach-broadening, KPIs; needs JD | answer directly (single known channel) |
| 5 | Write outreach / InMail / cold-email messages | sourcing-specialist | Personalize on job-relevant signals only; value prop; clear ask; 3-touch sequence | answer directly (one short message) |
| 6 | Design the screening process / resume rubric | screening-expert (+ /competency-model) | Bias-correlated fields redacted; rubric + weights fixed first; job-related rationale per score | answer directly (single criterion) |
| 7 | Create a take-home assignment / pre-interview task | screening-expert | Job-related + validated, <=4h time-boxed, accommodation offered, rubric fixed in advance, same task/rubric for all | interview-designer (if it is live technical) |
| 8 | Design the interview loop / structure the rounds | interview-designer (+ /interview-scorecard) | Stages, time, panel, competency-per-round; ADA-accommodating formats | answer directly (one round) |
| 9 | Write interview questions (behavioral / technical) | interview-designer (+ /interview-scorecard) | STAR/BEI; >=2 per competency; runs full protected-inquiry checklist | answer directly (a couple of questions) |
| 10 | Build an interviewer guide / evaluation form | interview-designer | 4-point anchored scorecard, anti-bias do/don't, debrief rules | answer directly (template tweak) |
| 11 | Score / compare candidates / reach a decision | offer-coordinator | Synthesize evidence to SUPPORT a human decision (no verdict; no automated screen-out); independent anchored scoring with per-score rationale | screening-expert (if only resume stage done) |
| 12 | Build the offer / comp package + negotiation plan | offer-coordinator | Market positioning, package, negotiation room; salary-history-ban aware | answer directly (single number) |
| 13 | Draft the offer letter or rejection note | offer-coordinator | Plain language; prepend disclaimer; rejection is a draft for a named human to own and send | answer directly (minor wording) |
| 14 | Research market salary / competitor JDs / candidates | sourcing-specialist | Web research; cite source + date for every figure | answer directly (one quick fact) |
| 15 | Review / audit an existing hiring process for gaps | offer-coordinator | Cross-check JD <-> rubric <-> interview <-> offer; flag any non-job-related criterion or adverse-impact risk | screening-expert (if only screening stage) |
| 16 | Convert / read an inbound resume, JD, or rubric (PDF/DOCX) | /process-inbox (MarkItDown) -> relevant agent | Redact/anonymize candidate name + contact to an opaque label before any summary; write to per-req dir, never Outbox | answer directly (already plain text) |
| 17 | References / background-check planning | clarify -> human duty | Out of scope as an action: requires candidate consent + (US) FCRA disclosure/authorization/adverse-action handling -- the assistant only drafts the process steps for a human to run | answer directly (process outline only) |

Complexity scaling: Simple (1 agent or direct: one competency, one quick
salary fact, a couple of questions, single message) | Standard (2-3 agents
serial: JD -> sourcing, JD -> screening, interview-loop design with scorecards)
| Complex (full /hiring-pipeline, all 5 agents with up to 2 consistency
revision rounds from offer-coordinator).

## Safeguards (employment law, anti-discrimination, candidate data)

Candidate material is the most sensitive data this library handles and hiring is
its most regulated activity. None of the following are optional for the domain.

- **AI-hiring law (verify current obligations with counsel; jurisdiction-
  specific):** NYC Local Law 144 requires a bias audit of automated employment
  decision tools plus candidate notice before use. The Illinois AI Video
  Interview Act requires consent and disclosure before AI analysis of video
  interviews. The EU AI Act classifies hiring/selection AI as high-risk --
  human oversight, logging, and transparency to candidates are mandatory. EEOC
  guidance applies ADA and Title VII to algorithmic selection tools. The
  assistant flags these obligations; it does not certify compliance.
- **Anti-discrimination / disparate impact:** every scored criterion and
  threshold must map to a bona fide job competency (job-related + consistent
  with business necessity). No proxies for protected classes (e.g., zip code,
  alma-mater prestige, names, graduation year). A facially-neutral rubric or
  cutoff can still cause adverse impact -- watch for pass-rate disparity across
  groups (the four-fifths / 80% rule is the common screen). The tool flags
  potential adverse impact; a human validates job-relatedness and reviews.
- **Human review of adverse decisions / NO automated rejection:** all agent
  output is decision-support. A named human (recruiter or hiring manager) must
  review and OWN every adverse action -- screen-out, no-hire, rejection. The
  assistant must not auto-screen-out a candidate and must not finalize or send
  a rejection.
- **ADA / accommodation:** assessments and interview formats must allow
  reasonable accommodation and must measure job ability, not disability. No
  pre-offer disability or medical inquiries.
- **Lawful inquiries / bans:** observe ban-the-box (no early criminal-history
  inquiry) and salary-history bans where they apply. The protected-inquiry
  checklist (below) is enforced in question design.
- **Diversity within the law:** diversity efforts mean broadening sourcing
  REACH and reducing evaluation bias ONLY. Selection never uses protected
  characteristics, quotas, or set-asides. Any "diversity ratio" KPI is reframed
  as pipeline/representation REACH (top-of-funnel), never a selection target.
- **References / background checks out of scope:** these require candidate
  consent and, in the US, FCRA disclosure, authorization, and adverse-action
  handling. The assistant may draft the process outline; running it is a human
  duty.
- **Protected-inquiry checklist** (seeded into /interview-scorecard and the
  anti-bias seed): age; family/marital status; pregnancy; religion;
  disability/health; national origin/citizenship; race/ethnicity; GINA/genetic
  information; criminal history. None may be asked or scored.
- **Enforcement:** the PreToolUse PII + adverse-action gate (below) defaults
  DETERMINISTIC for this domain.

### Candidate data handling (sensitive-data-rule.md)

- **Classification:** candidate material is **Restricted**. Hiring PII patterns
  include name, email, phone, postal address, date of birth, government ID,
  and compensation figures.
- **Exclusion from long-lived stores:** EXCLUDE candidate identifiers, scores,
  and rejection reasons from `/state-save`, `Docs/_working/retro/`, and
  PreCompact summaries. Reference each candidate by an opaque per-req label
  (e.g., `REQ-014-C03`), never by name or contact detail.
- **Defensible record (deliberate exception):** the per-req working dir
  (`Docs/_working/reqs/<req-id>/`) RETAINS the structured, job-related scoring
  rationale for each adverse decision -- this is the defensible record, kept
  per jurisdiction retention rules (commonly 1+ year). This is the one place
  scores and rationale persist; it is segregated, not commingled.
- **Retention + purpose limitation + consent:** apply storage-limitation
  (GDPR) / purpose-limitation (CCPA) thinking -- candidate data is used for the
  req it was collected for and deleted/archived per the retention window.
- **Per-req segregation:** no cross-req commingling of candidate data. Reusing a
  candidate from a prior req's talent pool requires a re-checked lawful basis
  (fresh consent / legitimate interest) before that data enters a new req.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) AI-hiring-law obligation missed -- an automated screening
  tool ships without flagging a required bias audit (NYC LL144) or candidate
  notice / consent (IL AI Video Act, EU AI Act). Mitigation: flag the applicable
  obligation in the deliverable and route compliance sign-off to HR/counsel.
- [PATTERN] (pre-seeded) Automated adverse action without human review -- a
  screen-out, no-hire, or rejection is finalized by the tool. Mitigation: all
  output is decision-support; a named human reviewer is recorded before any
  adverse action; the assistant never auto-screens-out or sends a rejection.
- [PATTERN] (pre-seeded) Bias-correlated field used in scoring -- name, photo,
  gender/pronoun marker, graduation year/age, school prestige alone, address, or
  marital/family status influences a score. Mitigation: screening-expert redacts/
  ignores these and scores only JD-derived competencies.
- [PATTERN] (pre-seeded) Disparate impact unchecked -- a criterion or cutoff has
  no job-relatedness note and no adverse-impact (four-fifths / pass-rate)
  consideration. Mitigation: every criterion maps to a bona fide competency;
  flag pass-rate disparity for human validation.
- [PATTERN] (pre-seeded) Candidate PII leaks into a shared / long-lived store --
  a resume name/email/score lands in retro, state, or a non-private file.
  Mitigation: reference candidates by opaque per-req label; keep PII and scores
  only in the per-req working dir.
- [PATTERN] (pre-seeded) Retention / purpose-limitation ignored -- candidate data
  kept indefinitely or reused across reqs without a re-checked lawful basis.
  Mitigation: per-req segregation, retention window applied, fresh basis before
  talent-pool reuse.
- [PATTERN] (pre-seeded) JD lists years-of-experience instead of competencies --
  "5+ years required" gatekeeps without measuring ability. Mitigation: jd-writer
  converts every requirement into a demonstrable competency at an L-level.
- [PATTERN] (pre-seeded) Salary band asserted without a sourced figure -- a comp
  range is stated with no market basis. Mitigation: every band cites a source +
  date, or proposes a 3-point (low/mid/high) range tagged [MARKET-RESEARCH].
- [PATTERN] (pre-seeded) Unstructured / biased interview phrasing -- a leading or
  protected-class question (age, family, status, etc.) slips into the guide.
  Mitigation: /interview-scorecard runs the full protected-inquiry checklist
  before sign-off.
- [PATTERN] (pre-seeded) Pipeline stages disagree -- JD competencies, screening
  rubric, interview loop, and offer criteria reference different skills.
  Mitigation: offer-coordinator cross-checks JD <-> rubric <-> interview <-> offer.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve the role definition,
  competency model, and current-stage deliverable before compaction; exclude
  candidate PII and per-candidate scores (reference by opaque label). See
  `Docs/Templates/Optional/hooks-template.md`.
- **PreToolUse PII + adverse-action gate** (recommended by default,
  DETERMINISTIC) -- pairs with `pii-patterns.conf` (resume emails, phone
  numbers, postal addresses, DOB, government IDs, comp figures). On scoped writes
  to any adverse-action or offer artifact, BLOCK if (a) the human-review /
  not-legal-advice disclaimer is absent, OR (b) the file contains a hire/no-hire
  verdict or an ordinal candidate ranking without a recorded human reviewer.
  May downgrade to advisory only if the user confirms all output is internal
  draft and a human reviewer is always recorded out-of-band.
- Optional **Stop hook self-review** -- on a completed deliverable, prompt a
  quick competency-coverage / consistency / protected-inquiry check. Keep a
  re-entry guard. Not code-producing, so lighter than the software-dev variant.

## Disclaimer

Every offer letter, rejection note, and screening-criterion deliverable
prepends:

> Draft for human review -- not legal advice; verify employment-law compliance
> (and any required bias audit / candidate notice) with HR/counsel.

## process-inbox redaction step

Before any summary is produced from an inbound resume/JD/rubric: strip and
replace the candidate's name and contact details with the opaque per-req label
(e.g., `REQ-014-C03`). Write the converted, anonymized file to the per-req
working dir (`Docs/_working/reqs/<req-id>/`), NEVER to Outbox. Never echo raw
PII into a summary, a retro entry, or state.

## Ecosystem Permissions

Base + Universal Deny only -- see `Docs/Templates/References/ecosystem-permissions.md`.
This domain has no language ecosystem; deny programming tools (`pip`, `npm`,
`node`, `python`) as in the knowledge-work pattern. Allow safe text utilities
(`wc`, `diff`, `sort`, `date`) and Pandoc for .docx/.pdf output when installed.
Add writable `Docs/_working/reqs/**` so the pipeline writes deliverables without
prompts. Use the MarkItDown MCP server (verified) to read inbound resume/JD
PDF/DOCX without enabling Python. Candidate data is Restricted PII -- keep the
Base deny on `secrets/`/`credentials` and add a deny on any raw applicant-data
directory the intake flags immutable. Generate `local config profile` for
machine-specific template, ATS-export, or vault paths.

## Cost / Model Notes

GPT-5.5 for screening-expert, interview-designer, offer-coordinator (judgment:
bias-controlled rubric calibration, structured-interview design, evidence
synthesis, consistency QA, negotiation risk); medium-effort GPT-5.5 for jd-writer and
sourcing-specialist (established-pattern drafting -- JD/posting/outreach
templates and channel tables). Defaults: balanced (GPT-5.5 on reasoning roles,
medium-effort GPT-5.5 on execution; compaction 95%; AGENTS.md ~200 lines). Cost-conscious
override: keep screening-expert and interview-designer GPT-5.5 (the
bias/adverse-impact judgment is load-bearing -- do not downgrade), move the
rest to medium-effort GPT-5.5, compaction 85%. Subagents ~4x vs direct; the full pipeline is
the most expensive path -- reserve it for a real open req, use single-agent
modes for a JD, a question set, or an offer.

## Customization Points

Single role vs. recurring req portfolio (-> Standard memory, per-req folders);
role family (eng vs. sales vs. ops -- drives competency model and channel mix);
seniority (IC vs. leadership -- changes interview loop depth and comp design);
jurisdiction + applicable AI-hiring law (NYC LL144 / IL AI Video Act / EU AI
Act / EEOC -- drives required notices, bias-audit obligations, ban-the-box and
salary-history-ban handling); enforcement strength (deterministic PreToolUse
gate by default vs advisory-only if the user confirms all output is internal
draft with a human reviewer always recorded); candidate-data sensitivity and
retention window (per-req segregation, retention per jurisdiction); ATS
integration (export/import format if the org uses Greenhouse/Lever/Workday ->
/process-inbox conversion + settings.local paths); required output format
(.docx posting, branded offer letter via Pandoc); team vs. solo (team ->
shared competency library and scorecards, multi-role).

## Team-architecture pattern

Pipeline (JD -> sourcing + screening in parallel -> interview -> offer) with an
embedded Producer-Reviewer loop: offer-coordinator cross-verifies the full
pipeline for consistency and job-relatedness and can send up to two revision
rounds back to the relevant specialist before the final package -- but it
synthesizes evidence to support a human decision, never issuing a verdict.
Sourcing and screening both depend only on the JD and run in parallel;
everything downstream is strictly serial. Subagents are the default and fit a
single open req; Agent Teams are only worth the ~15x cost when one operator
runs several distinct reqs in parallel with non-overlapping timelines.

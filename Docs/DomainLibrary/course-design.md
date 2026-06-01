# Bundled Domain: Course Design

Adapted from revfactory/harness-100 08-course-builder. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim) -- a starting point the architect adapts; it points at templates, it
does not inline them.

Domain: designing online courses end to end -- curriculum and learning
objectives, lesson plans and instructor notes, formative/summative quizzes, and
hands-on labs -- with a quality pass that checks objective alignment across every
deliverable. Out of scope (architect should set expectations): LMS setup, video
recording/editing, student enrollment, and certificate issuance.

**Audience framing:** this seeds a tool that produces DRAFT course materials. A
qualified instructor (subject-matter expert) verifies factual accuracy and
accessibility before the course is delivered to learners. The assistant never
invents a citation, URL, statistic, or quote, and flags any version-specific,
statistical, or factual claim as needing source/date verification.

## Profile Metadata

- **Target audience**: instructional designers, course creators, training leads,
  technical educators, bootcamp/curriculum authors
- **Primary tools**: Markdown deliverables; Pandoc for .docx/.pptx export;
  optional MarkItDown for inbound source material
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: conservative (confirm before overwriting an approved curriculum) | **VCS**: optional Git (course repos are document-centric)

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| curriculum-designer | opus | Set learning objectives (Bloom's/ABCD), structure modules -> lessons, map prerequisites, estimate time | planner.md |
| content-writer | sonnet | Write lesson plans, slide outlines, instructor notes, learner handouts from the curriculum; apply UDL (multiple means of representation/engagement/expression), write alt text for every image, caption notes for media, readable heading structure; use inclusive, non-biased examples; use original or CC/public-domain media and cite third-party sources (no copyrighted reproduction) | drafter.md |
| quiz-maker | sonnet | Author formative + summative items mapped to objectives, with distractors and feedback | drafter.md (custom: assessment authoring) |
| lab-designer | sonnet | Design labs, mini projects, capstone, rubrics, scaffolding/starter code | drafter.md (custom: lab authoring) |
| course-reviewer | opus | Cross-validate objective alignment, difficulty curve, coverage gaps; check verb-level constructive alignment (each assessment's cognitive demand matches its objective's Bloom level); enforce the accessibility target (alt text, captions, readable structure, UDL) and the accuracy guardrail (flag unverified factual/statistical/version claims) (read-only QA) | reviewer.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (conservative), context-management, self-learning, error-handling,
memory-management; conditional `vcs-git.md` only if the course lives in a repo.
**Required domain rule:** a pinned integrity rule (see Safeguards) -- materials
ship as DRAFT for instructor verification, the assistant never fabricates a
citation/URL/statistic/quote, and every deliverable meets the accessibility
target before it is marked review-ready.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/build-course` (pipeline
orchestrator), and three knowledge skills surfaced via `/build` template style:
`/learning-design` (Bloom's, Backward Design, Gagne, cognitive load),
`/assessment-engineering` (item types, distractor psychology, rubrics, feedback),
`/lab-scaffolding` (5-level pyramid, starter code, capstone, hint systems).

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | "Create an online course" / full build | /build-course (curriculum-designer -> content-writer + quiz-maker + lab-designer -> course-reviewer) | Capture topic, learner level, total hours, lab tools first | intake (if topic/level unclear) |
| 2 | "Design just the curriculum" | curriculum-designer -> course-reviewer | Bloom's-based objectives, modules of 3-7 lessons, 15-30 min each | answer directly (one-module outline) |
| 3 | Define / refine learning objectives | curriculum-designer (+ /learning-design) | Use ABCD formula; state as "learner will be able to..." | answer directly (single objective reword) |
| 4 | Write lesson plans for an existing curriculum | content-writer | Requires `01_curriculum`; apply EEPS + Gagne's 9 events | curriculum-designer first (if no curriculum) |
| 5 | Slide outline / instructor notes / handout | content-writer | One key message per slide; define terms on first use | answer directly (single slide) |
| 6 | "Just make quizzes" | quiz-maker (+ /assessment-engineering) | Map every item to an objective; each item's cognitive demand matches that objective's Bloom verb (constructive alignment); Bloom's + difficulty distribution; do not invent a statistic or quote in a stem | content-writer first (need lesson concepts) |
| 7 | Distractors / wrong-answer feedback | quiz-maker | Base distractors on common misconceptions; EEC feedback | answer directly (rework one item) |
| 8 | "Design the labs / projects" | lab-designer (+ /lab-scaffolding) | 5-level pyramid; real-world scenario; rubric + sample solution | curriculum-designer first (if no objectives) |
| 9 | Capstone / final project design | lab-designer | Portfolio-worthy, 4-8 hr, integrates all core skills | answer directly (scope a milestone) |
| 10 | Rubric construction | lab-designer or quiz-maker (+ /assessment-engineering) | 3-5 observable criteria, clear level distinctions | answer directly (single criterion) |
| 11 | Review the course / QA pass | course-reviewer | Builds objective coverage matrix; checks verb-level constructive alignment (assessment Bloom level == objective Bloom level), accessibility target (alt text, captions, readable structure, UDL), and unverified factual/statistical/version claims; RED/YELLOW/GREEN findings | answer directly (spot-check one lesson) |
| 12 | "Is difficulty consistent?" / coverage gap / alignment check | course-reviewer | Check Lesson -> Quiz -> Lab curve; flag unmapped objectives and any assessment whose cognitive demand mismatches its objective's verb | answer directly (one module) |
| 13 | Adapt course to a new learner level | curriculum-designer -> course-reviewer | Re-tier objectives; split excluded scope into "advanced track" | content-writer (if only wording changes) |
| 14 | Export deliverable to .docx / slides | answer directly (Pandoc on the Markdown) | Pandoc renders `01`-`05`; falls back to Markdown if absent | content-writer (if content not yet written) |
| 15 | Import an existing syllabus / source doc | MarkItDown -> curriculum-designer (map to objectives) | Converts Word/PDF/PPTX inbound to Markdown | answer directly (already plain text) |
| 16 | "Explain Bloom's / Backward Design / scaffolding" | answer directly (+ relevant knowledge skill) | Cite the framework; keep learner-facing language plain | curriculum-designer (if applying to this course) |

Complexity scaling: Simple (direct answer / one item / one slide / Pandoc
export) | Standard (1-2 agents: lesson plans, quiz set, lab set, single review) |
Complex (full /build-course pipeline: all 5 agents with a review-rework cycle).

## Safeguards (accuracy, accessibility, media)

Courses teach learners directly, so two failure modes carry real cost --
teaching something wrong and excluding learners. These are first-class for the
domain, applied proportionately (a pinned rule + reviewer enforcement + seeds),
not heavy regulatory machinery:

- **Accuracy guardrail:** the assistant NEVER invents a citation, URL,
  statistic, or quote. Any version-specific (tool/API/library version),
  statistical, or factual claim is FLAGGED inline as needing source/date
  verification, with the search date noted when web search is used. Materials
  ship as DRAFT; a qualified instructor verifies factual accuracy before
  delivery. On a knowledge gap, report it -- do not fill it from general
  recall as if authoritative.
- **Accessibility target:** every deliverable meets the project's accessibility
  target (WCAG 2.2 AA / Section 508 / institutional policy -- set in
  Customization) before course-reviewer marks it review-ready. Concretely: alt
  text for every image/diagram, caption/transcript notes for audio/video,
  readable heading structure and link text, and UDL coverage (multiple means of
  representation, engagement, and expression). Honor any declared learner
  accommodations. course-reviewer enforces this; it is a RED finding when missing.
- **Media licensing:** use original media or CC / public-domain assets; cite
  the source and license for any third-party material; never reproduce
  copyrighted text, images, or media. When a needed asset is unavailable,
  describe it as a placeholder for the instructor to source rather than
  fabricating attribution.
- **Inclusive examples:** examples, names, and scenarios are inclusive and
  non-biased; avoid stereotypes and culturally narrow assumptions.

## Ecosystem Permissions

Base + Universal Deny (always) -- see
`Docs/Templates/References/ecosystem-permissions.md`. This domain is
document-centric: keep broad `Read(./**)`, restrict `Write/Edit` to `./Docs/**`,
`./_workspace/**`, and `./Outbox/**`. Add Git only when the course lives in a
repo. Domain-specific (not in the reference): allow `Bash(pandoc *)` for
deliverable export; if MarkItDown is used for inbound docs, prefer its MCP server
over enabling Python broadly, or allow `Bash(markitdown *)` narrowly. Deny
programming-language toolchains unless the course teaches code AND the labs are
run/verified locally. Generate `settings.local.json` for machine-specific
Pandoc/MarkItDown paths.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Objective-deliverable drift -- a lesson/quiz/lab ships
  without mapping to a stated learning objective. Mitigation: every deliverable
  cites the objective ID; course-reviewer's coverage matrix is the gate.
- [PATTERN] (pre-seeded) Learner level unspecified -- agents default to "beginner"
  silently and over/under-shoot. Mitigation: orchestrator confirms learner level
  and prior knowledge before /build-course; record it in 00_input.
- [PATTERN] (pre-seeded) Quiz/lab scope overlap -- quiz-maker and lab-designer
  assess the same concept twice. Mitigation: share assessment scope between the
  two; reviewer flags duplicate coverage.
- [PATTERN] (pre-seeded) Cognitive overload per lesson -- more than 3 new concepts
  packed into one 15-30 min lesson. Mitigation: chunking check in content-writer;
  split or move concepts to the next lesson.
- [PATTERN] (pre-seeded) Lab has no scaffolding -- "build X" with no hints/starter
  code, high abandonment. Mitigation: lab-designer applies the 5-level pyramid and
  a tiered hint system to every lab.
- [PATTERN] (pre-seeded) Unrealistic time estimates -- module hours ignore lab +
  quiz time. Mitigation: estimate video + hands-on + quiz separately; reviewer
  validates totals.
- [PATTERN] (pre-seeded) Fabricated or unverified fact/stat/cite -- a statistic,
  quote, citation, URL, or version-specific claim is asserted as settled.
  Mitigation: never invent these; flag every factual/statistical/version claim
  for instructor source/date verification; note web-search date when used.
- [PATTERN] (pre-seeded) Accessibility skipped -- images without alt text, media
  without captions/transcripts, single-mode delivery, poor structure. Mitigation:
  apply UDL + alt text + captions + readable structure to every deliverable;
  course-reviewer treats a miss as a RED finding against the accessibility target.
- [PATTERN] (pre-seeded) Verb-level alignment drift -- an objective says "analyze"
  but the quiz only tests recall (or a lab demands "create" with no matching
  objective). Mitigation: match each assessment's cognitive demand to its
  objective's Bloom verb; reviewer flags mismatches in the coverage matrix.
- [PATTERN] (pre-seeded) Copyrighted media reproduced or uncited -- third-party
  text/images pasted in without license or attribution. Mitigation: original or
  CC/public-domain only; cite source + license; placeholder when unavailable.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve curriculum decisions, the
  objective map, and current deliverable in progress before compaction.
  See `Docs/Templates/Optional/hooks-template.md`.
- Optional **Stop hook coverage check** -- on session stop after a build, remind
  if `05_review_report` is missing or has open RED findings, including unresolved
  accessibility misses or unverified factual/statistical/version claims still
  awaiting instructor verification (advisory, with a re-entry guard). Not a code
  self-review; this domain produces documents.

## Cost / Model Notes

Opus for the reasoning/QA roles (curriculum-designer, course-reviewer); Sonnet
for the established-pattern authoring roles (content-writer, quiz-maker,
lab-designer). Defaults: balanced (Opus on design + review, Sonnet on authoring;
compaction 95%; CLAUDE.md ~200 lines). Cost-conscious override: all-Sonnet except
course-reviewer stays Opus for the alignment pass; compaction 85%; CLAUDE.md ~150;
mention Pandoc-batch over per-file export. The three authoring agents run in
parallel after curriculum, so a full build is ~4x a direct chat per agent --
budget accordingly. Quality-first: keep Opus on curriculum-designer and
course-reviewer; do not downgrade the coverage matrix step.

## Customization Points

- Subject area + does the course teach code? (drives lab environment, whether any
  language toolchain permission is needed, predict-output/find-the-bug item types)
- Learner level and prior knowledge (single track vs beginner/intermediate/advanced
  branching)
- Course scale (total hours, module count) and theory:practice ratio (default 60:40)
- Accessibility target + learner accommodations: which standard governs (WCAG 2.2
  AA / Section 508 / institutional policy) and any declared accommodations (screen
  reader, captioning, dyslexia-friendly, extended time) -- drives reviewer
  enforcement and the UDL coverage the authoring agents apply
- Assessment stakes: graded/high-stakes (summative, certification) vs self-check/
  formative -- drives item rigor, distractor care, feedback depth, and how strictly
  constructive alignment is enforced
- Deliverable format (Markdown only, or Pandoc export to .docx/.pptx/.pdf) and any
  brand/template requirements
- Lab environment (browser IDE / Colab / Codespaces / Docker) and dataset needs
- Solo author vs team (team -> multi-role; Git if the course is repo-tracked)

## Team-architecture pattern

Fan-out / fan-in inside a Pipeline with a Producer-Reviewer gate: curriculum-
designer produces the spine, then content-writer + quiz-maker + lab-designer
fan out in parallel off that single dependency, and course-reviewer fans the
results back in and drives a bounded rework cycle. Because the three authoring
agents genuinely work non-overlapping deliverables in parallel and benefit from
direct hand-offs, this is the one phase that justifies Agent Teams over the
subagent default; smaller single-deliverable requests (one quiz set, one review)
stay on plain subagents.

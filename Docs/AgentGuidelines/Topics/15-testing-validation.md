# 15. Testing, Validation, and QA Boundary-Crossing

This topic covers how generated environments verify their own correctness:
grading methodology, verification commands, self-validation loops, the
QA-agent discipline of checking connections (not just existence), and how to
test skill triggering with A/B evaluation.

## Table of contents

- 15.1 Three-Tier Grading (Code > LLM > Human) [ALL]
- 15.2 Edge Cases [ALL]
- 15.3 Verification Commands [ALL]
- 15.4 Investigate-Before-Answering [ALL]
- 15.5 Stop Hook Self-Review [ALL]
- 15.6 Self-Learning Execution Loop [ALL]
- 15.7 State File Growth Bounds [ALL]
- 15.8 Context Discipline Enforcement [ALL]
- 15.9 QA Boundary-Crossing Validation [ALL]
- 15.10 Skill Triggering Tests and A/B Evaluation [ALL]

---

## 15.1 Three-Tier Grading (Code > LLM > Human) [ALL]

- **Established**: Baseline
- **Source**: test-and-evaluate.md | Tier 1
- **Recommendation**: Use grading methods in order of preference:
  1. **Code-based grading**: Fastest, most reliable, extremely scalable. Use for structural
     checks: file exists, JSON valid, cross-references resolve, string matches, exact output.
  2. **LLM-based grading**: Fast, flexible, scalable, good for complex judgment. Use for
     semantic checks: routing completeness, no contradictions, quality assessment. Best
     practice: use a different model for evaluation than generation.
  3. **Human grading**: Most flexible but slow and expensive. Use only for functional testing
     that cannot be automated: "Does the environment feel right? Can I accomplish real
     tasks?"

  Prioritize volume over quality: more automated checks with slightly lower signal beats
  fewer high-quality human checks.
- **Anti-pattern**: Relying only on human grading. It does not scale and is too slow for
  iterative development. Automate everything that can be automated.

## 15.2 Edge Cases [ALL]

- **Established**: Baseline
- **Source**: test-and-evaluate.md | Tier 1
- **Recommendation**: ALWAYS include edge cases in evaluations:
  - Irrelevant or nonexistent input data
  - Overly long input data
  - Poor, harmful, or irrelevant user input
  - Ambiguous cases where even humans would struggle to agree
  - Sarcasm, typos, mixed signals

  For skill evaluations: test 3 obvious triggers + 2 paraphrased triggers + 2 non-trigger
  phrases per skill. This validates both positive and negative triggering. (For a more
  rigorous near-miss protocol and A/B grading, see 15.10.)
- **Anti-pattern**: Testing only happy-path scenarios. Edge cases are where environments fail
  in practice, and they are easy to miss during development.

## 15.3 Verification Commands [ALL]

- **Established**: Baseline
- **Source**: claude-code-best-practices.md | Tier 1
- **Recommendation**: This is the #1 highest-leverage intervention. Every generated
  environment must include domain-specific verification commands:
  - Software (Node): `npm test`, `npm run lint`, `npx tsc --noEmit`
  - Software (Python): `python -m pytest`, `ruff check`, `mypy`
  - Software (Rust): `cargo test`, `cargo clippy`
  - Infrastructure: `terraform plan`, `terraform validate`
  - Documentation: style guide compliance script

  Include in CLAUDE.md: "After making changes, always run [verification command] to verify
  your work. Fix any failures before proceeding."

  Claude performs dramatically better with self-verification. Without it, the user becomes
  the only feedback loop.
- **Anti-pattern**: Generated environments without verification commands. The user must
  manually verify every change, which is slow and error-prone.

## 15.4 Investigate-Before-Answering [ALL]

- **Established**: Baseline
- **Source**: guardrails.md, platform-agent-patterns.md | Tier 1
- **Recommendation**: Include this pattern in all generated agent prompts:
  ```xml
  <investigate_before_answering>
  Never speculate about code you have not opened. If the user references a specific
  file, you MUST read the file before answering. Make sure to investigate and read
  relevant files BEFORE answering questions about the codebase.
  </investigate_before_answering>
  ```

  This is the primary pattern for reducing hallucinations in agentic coding. It forces the
  agent to ground responses in actual file content rather than speculation.
- **Anti-pattern**: Agents answering questions about code they have not read. This produces
  plausible but often incorrect responses.

## 15.5 Stop Hook Self-Review [ALL]

- **Established**: 2026-03
- **Source**: Claude Code hooks docs, Trail of Bits config, Addy Osmani blog, community patterns | Tier 2
- **Recommendation**: Every generated environment for code-producing projects SHOULD include
  a Stop hook that spawns an independent reviewer before work is presented to the user:

  ```json
  {
    "hooks": {
      "Stop": [{
        "type": "agent",
        "description": "Review modified files for correctness before presenting to user",
        "timeout": 60
      }]
    }
  }
  ```

  The reviewer agent:
  - Reads all files modified in the current turn (from git diff or tool history)
  - Checks for: compilation errors, style violations, incomplete implementations,
    introduced bugs, security issues
  - Returns clean status (exit 0) or rejection with specific issues (exit 2)
  - Exit 2 feeds stderr to Claude, forcing self-correction before presenting to user

  production game project lesson: The environment had a /validate skill but no automatic self-review.
  Validation only happened when explicitly invoked. A Stop hook catches issues
  automatically on every turn.

  **When to include**: Software development, game development, data pipelines -- any
  environment that produces code or configuration files.
  **When to skip**: Knowledge work, research, document drafting (review is subjective).
  **Cost**: ~1.5-2x token overhead per turn. Document this trade-off.

- **Anti-pattern**: Relying solely on the main agent to review its own work in the same
  context. A separate reviewer in a fresh context provides cognitive diversity.

## 15.6 Self-Learning Execution Loop [ALL]

- **Established**: 2026-03
- **Source**: production game project production analysis, SICA (ICLR 2025), Addy Osmani blog | Tier 2
- **Recommendation**: Self-learning needs both a logging mechanism AND an execution trigger.
  production game project demonstrated the failure mode: observations logged but never acted on.

  Required components:
  1. **Logging** (retro/ friction logs): Already standard. Log observations with categories.
  2. **Trigger threshold**: After N observations (default 5, configurable), the environment
     should prompt the user: "5 new observations logged. Run /update to review and apply?"
  3. **Execution** (/update skill): Analyzes observations, proposes environment changes,
     applies after user approval.
  4. **Feedback**: VERSION.md changelog updated with each /update run.

  The trigger can be implemented as:
  - A SessionStart hook that counts retro/ entries since last /update run
  - A note in the self-learning rule: "After 5+ unprocessed observations, recommend /update"
  - An auto-reminder in /state-load output

  The key insight from production: logging without execution is worse than no logging,
  because it creates a false sense that learning is happening.

- **Anti-pattern**: Self-learning systems that only log. Also: auto-applying changes without
  user approval (changes should be reviewed, not silently applied).

## 15.7 State File Growth Bounds [ALL]

- **Established**: 2026-03
- **Source**: production game project production analysis | Tier 2
- **Recommendation**: State and session files need explicit growth bounds:

  | File | Max Size | Pruning Strategy |
  |------|----------|-----------------|
  | SESSION_CONTEXT.md | 100 lines | Keep last 5 compaction timestamps; archive older |
  | SESSION_SNAPSHOT.json | N/A (single snapshot) | Overwrite on each save |
  | Retro logs (per month) | 50 entries | Archive to retro/archive/ after /update processes them |
  | Validation artifacts | 3 most recent per topic | Auto-archive older to sessions/archive/ |
  | Compaction log | 20 entries | Separate file from SESSION_CONTEXT; rotate monthly |

  production game project lesson: SESSION_CONTEXT.md grew to 272 lines (210 were PreCompact auto-save
  messages). The file became noise rather than signal.

  Implementation: /state-save skill should check file sizes and prune before appending.
  Include pruning logic in the skill template.
- **Anti-pattern**: Unbounded append-only state files. They defeat the purpose of state
  management by making it impossible to find the actual state.

## 15.8 Context Discipline Enforcement [ALL]

- **Established**: 2026-03
- **Source**: production game project production analysis | Tier 2
- **Recommendation**: When the orchestrator rule says "do not read source files directly,"
  enforce it technically where possible:

  - Add deny patterns in settings.json for the orchestrator's direct file access
    to source directories (may not be technically feasible in all cases)
  - Use a PreToolUse hook that checks Read tool calls against an allowlist
  - At minimum, include a prominent warning in the orchestrator rule with the
    specific directories that should only be accessed by subagents

  production game project lesson: The orchestrator rule stated "MUST NOT Read Source/, Plugins/**/Source/"
  but had no technical enforcement. Honor-system rules fail under context pressure -- when
  the model is running low on context, it takes shortcuts.
- **Anti-pattern**: Relying solely on prompt instructions for critical constraints.
  If a constraint matters enough to state, it matters enough to enforce.

## 15.9 QA Boundary-Crossing Validation [ALL]

- **Established**: 2026-05
- **Source**: Harness qa-agent-guide.md (SatangSlide production bug analysis) | Tier 2
- **Recommendation**: When generating a QA or validation agent, make it verify
  *connections between components*, not just the existence of each component. The most
  common runtime failures occur where two pieces of code are each individually correct
  but their contract at the boundary does not match.

  **Existence checks vs. connection checks.** "Does the API endpoint exist?" is an
  existence check; "Does the API endpoint's response shape match what the calling hook
  expects?" is a connection (boundary-crossing) check. A QA agent that only does existence
  checks will pass code that crashes at runtime.

  ### Why static review and a passing build miss these

  - **Type-generic casting hides mismatches**: `fetchJson<SlideProject[]>()` compiles even
    when the runtime response is actually `{ projects: [...] }`. The compiler trusts the
    generic.
  - **A passing `npm run build` is not proof of correct behavior**: when casts, `any`, or
    generics are involved, the build succeeds but the code fails at runtime.
  - **Individually-correct components**: each side validates in isolation; nobody compares
    them against each other.

  ### Boundary-crossing checks to put in generated QA agents

  Frame each as a *cross-comparison* that reads both sides at once:

  1. **API response <-> frontend hook type shape.** Compare the object shape passed to each
     API route's response serializer (e.g. `NextResponse.json()`) against the generic type
     parameter the corresponding hook expects (e.g. `fetchJson<T>`). Verify:
     - Wrapped responses (`{ items: [...] }`, `{ data: [...] }`, `{ projects: [...] }`) are
       unwrapped on the hook side rather than treated as a bare array.
     - Pagination envelopes (`{ items, total, page }`) versus a frontend that expects a
       plain array.
     - snake_case DB field -> API response -> frontend type definition stay consistent (a
       `thumbnailUrl` vs `thumbnail_url` mismatch is invisible to the type checker once a
       cast is involved).
     - Immediate/async responses: a `202 Accepted` immediate response (`{ status }`) versus
       a final result the frontend reads as `data.failedIndices`. Distinguish synchronous
       acknowledgements from eventual results, not just types.
  2. **File path <-> link / router href routing.** Extract the URL pattern from every page
     file under the app routing tree, then collect every `href=`, `router.push(...)`, and
     `redirect(...)` value in the code and confirm each points at a real page path. Account
     for route groups (`(group)` segments are stripped from the URL) and dynamic segments
     (`[param]` / `[id]` filled with the correct parameter). A missing path prefix (a link
     to `/create` when the page lives at `/dashboard/create`) yields silent 404s.
  3. **State-transition completeness.** Extract the allowed transitions from the state map
     (e.g. `STATE_TRANSITIONS`), then find every `status:` update in the code
     (`.update({ status: "..." })`) and confirm:
     - Every code transition is defined in the map (no unauthorized transitions).
     - Every map transition is actually executed somewhere (no dead transitions).
     - The intermediate-to-final transition is not missing (e.g.
       `generating_template -> template_approved`), which otherwise leaves a flow waiting
       forever.
     - Any frontend `if (status === "X")` branch references a status that is actually
       reachable.
  4. **Endpoint <-> hook 1:1 mapping.** List every API route (by HTTP method) and every
     frontend data hook's fetch URL, then map them 1:1. Flag any endpoint with no calling
     hook as "unused", and judge whether that is intentional (e.g. an admin-only API) or a
     missing call. Flag any hook that calls a nonexistent endpoint.

  ### Design principles for the generated QA agent

  - **Use a general-purpose (read + grep + script-run) agent type, not read-only.** An
    effective QA agent greps for patterns (extract all response-serializer calls), runs
    scripts to auto-cross-check (API shape vs hook type), and can propose fixes. A purely
    read-only "explorer" type cannot do the cross-comparison work.
  - **Prefer cross-comparison checklist items over existence items.** Weak: "Does the
    endpoint exist?" Strong: "Does the endpoint's response shape match the hook's type?"
    Weak: "Is the state map defined?" Strong: "Does every status update match a defined
    transition?" Weak: "Does the page file exist?" Strong: "Does every link point at a
    real page?" Weak: "Is TypeScript strict mode on?" Strong: "Is type safety bypassed
    anywhere by generic casting?"
  - **"Read both sides at once" principle.** To catch a boundary bug the agent must open
    *both* sides together: the API route AND its hook; the state map AND the real update
    code; the file structure AND the link paths. State this explicitly in the agent
    definition.

  ### Incremental (per-module) QA timing

  Do NOT place QA only as a final "Phase 4: after everything is built" step. Doing so lets
  bugs accumulate (raising fix cost) and lets early boundary mismatches propagate into
  later modules. Recommended pattern: run the cross-check as each backend API is finished,
  immediately validating that API together with its corresponding hook (incremental QA).

  ### Web-app integration-coherence checklist (template for generated QA agents)

  ```markdown
  ### Integration coherence (web app)

  #### API <-> frontend wiring
  - [ ] Every API route's response shape matches the corresponding hook's generic type
  - [ ] Wrapped responses ({ items: [...] }) are unwrapped on the hook side
  - [ ] snake_case <-> camelCase conversion is applied consistently
  - [ ] Immediate (202) vs final-result shapes are distinguished on the frontend
  - [ ] Every API endpoint has a corresponding frontend hook that actually calls it

  #### Routing coherence
  - [ ] Every href / router.push value matches a real page file path
  - [ ] Path checks account for route groups ((group)) being stripped from the URL
  - [ ] Dynamic segments ([id]) are filled with the correct parameter

  #### State-machine coherence
  - [ ] Every defined transition is executed somewhere in code (no dead transitions)
  - [ ] Every status update in code is defined in the transition map (no rogue transitions)
  - [ ] Intermediate-to-final transitions are not missing
  - [ ] Each frontend status-branch (if status === "X") references a reachable X

  #### Data-flow coherence
  - [ ] DB schema field names map consistently to API response field names
  - [ ] Frontend type definitions match API response field names
  - [ ] Optional-field null/undefined handling is consistent on both sides
  ```

  ### QA agent definition skeleton

  ```markdown
  ---
  name: qa-inspector
  description: "QA verification specialist. Checks spec compliance, integration
  coherence, and design quality."
  ---

  # QA Inspector

  ## Core role
  Verify implementation quality against spec AND cross-module integration coherence.

  ## Verification priority
  1. Integration coherence (highest) -- boundary mismatches are the main source of
     runtime errors
  2. Functional spec compliance -- API / state machine / data model
  3. Design quality -- color / typography / responsiveness
  4. Code quality -- unused code, naming conventions

  ## Method: "read both sides at once"
  Boundary checks always open BOTH sides together and compare:

  | Target           | Left (producer)              | Right (consumer)        |
  |------------------|------------------------------|-------------------------|
  | API response shape | route response serializer  | hook fetchJson<T>       |
  | Routing          | page file path               | href, router.push value |
  | State transition | STATE_TRANSITIONS map        | .update({ status }) code|
  | DB -> API -> UI  | table column names           | API field -> type def   |

  ## Team communication protocol
  - On finding an issue, send a specific fix request (file:line + how to fix) to the
    owning agent
  - For boundary issues, notify BOTH agents on either side
  - To the lead: a verification report distinguishing pass / fail / not-verified items
  ```

  ### Worked examples (the bug -> the boundary -> the root cause)

  | Bug | Boundary | Root cause |
  |-----|----------|------------|
  | `projects?.filter is not a function` | API -> hook | API returned `{projects:[]}`, hook expected an array |
  | All dashboard links 404 | file path -> href | missing `/dashboard/` prefix |
  | Theme image not showing | API -> component | `thumbnailUrl` vs `thumbnail_url` |
  | Theme selection not saved | API -> hook | select-theme API existed, no hook |
  | Create page waits forever | state transition -> code | missing `template_approved` transition |
  | `data.failedIndices` crash | immediate response -> frontend | background result accessed from immediate response |
  | "View slides" 404 after completion | file path -> href | `/projects/` should be `/dashboard/projects/` |

- **Anti-pattern**: A QA agent whose checklist only asks "does X exist?" -- it passes code
  that compiles and builds but crashes at the seams. Also: deferring all QA to a single
  end-of-build phase, which lets boundary mismatches accumulate and propagate.

## 15.10 Skill Triggering Tests and A/B Evaluation [ALL]

- **Established**: 2026-05
- **Source**: Harness skill-testing-guide.md | Tier 2
- **Recommendation**: Validating a generated skill has two halves: does it *trigger* on the
  right requests (and not the wrong ones), and does it *improve* the output when it does
  trigger. Test both.

  ### Trigger eval: near-miss negatives

  Write ~20 eval queries: 8-10 should-trigger plus 8-10 should-NOT-trigger. Query quality
  bar:
  - Concrete, natural sentences a real user would type (file paths, personal context,
    column names, company names).
  - Mixed length, tone, and format.
  - Focus on **boundary/edge cases**, not obviously-correct queries.

  **Should-trigger queries (8-10):**
  - The same intent phrased many ways (formal / casual).
  - Cases that do not name the skill or file type explicitly but clearly need it.
  - Non-mainstream but valid use cases.
  - Cases that compete with another skill but where this skill should win.

  **Should-NOT-trigger queries (8-10):**
  - **Near-misses are the point** -- queries whose keywords look similar but where a
    different tool/skill is the right fit.
  - Adjacent domains, ambiguous phrasing, keyword overlap but different context.
  - Obviously-unrelated queries ("write a Fibonacci function") have no test value -- a
    boundary-ambiguous near-miss is far more informative.

  **Conflict check against existing skills:** collect the descriptions of the existing skill
  roster, confirm the new skill's should-trigger queries do not wrongly fire an existing
  skill, and if a conflict is found, tighten the boundary conditions in the description.

  ### With-skill vs without-skill A/B grading

  For each test prompt, spawn two subagents at once:
  - **With-skill run**: the prompt with the skill available; outputs to
    `iteration-N/eval-{id}/with_skill/outputs/`.
  - **Baseline run**: the identical prompt with no skill; outputs to
    `iteration-N/eval-{id}/without_skill/outputs/`.

  Baseline choice: for a brand-new skill, baseline is "same prompt, no skill"; for improving
  an existing skill, baseline is the pre-edit snapshot of the skill.

  **Capture timing immediately.** `total_tokens` and `duration_ms` from the subagent
  completion notification are only available at notification time and cannot be recovered
  later:
  ```json
  { "total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3 }
  ```

  **Test-prompt design.** Use concrete, natural prompts (not "process the PDF" but
  "extract the table on page 3 of this PDF into CSV; the header is two rows, first is the
  category and second is the real column name"). Mix formal/casual tone, explicit/implicit
  intent, simple/complex tasks; include some abbreviations and typos. Start with 2-3
  prompts covering one core use case, one edge case, and optionally one compound task.

  **Assertion-based scoring.** Where output is objectively checkable, define assertions and
  script them. A good assertion is objectively true/false, descriptively named, and tests
  the skill's core value. A bad assertion always passes regardless of the skill (e.g.
  "output exists") or needs subjective judgement ("well written"). Watch for
  **non-discriminating assertions** that pass at 100% in *both* configurations -- they do
  not measure the skill's differential value; remove or replace them with harder ones.
  Scoring schema:
  ```json
  {
    "expectations": [
      { "text": "profit-margin column added", "passed": true,
        "evidence": "column 'profit_margin_pct' present in column E" },
      { "text": "sorted descending by profit margin", "passed": false,
        "evidence": "no sort applied; original order preserved" }
    ],
    "summary": { "passed": 1, "failed": 1, "total": 2, "pass_rate": 0.50 }
  }
  ```

  **Reporting precision and recall.** From the trigger eval, report:
  - **Precision** = should-NOT-trigger queries correctly held (true negatives / all queries
    the skill fired on). Low precision = the skill is greedy and steals other work.
  - **Recall** = should-trigger queries correctly fired (true positives / all queries that
    should have fired). Low recall = the skill is too narrow and is missed when needed.

  From the A/B grading, report with-skill vs baseline pass-rate so the skill's differential
  value is explicit.

  ### Specialist evaluator agents (optional)

  - **Grader**: performs assertion-based scoring with evidence, extracts factual claims from
    the output and cross-checks them, and gives feedback on the eval itself (flags
    assertions that are too easy or ambiguous).
  - **Comparator (blind A/B)**: anonymizes the two outputs and judges quality without knowing
    which used the skill. Use when rigorously confirming "is the new version actually
    better?"; can be skipped in routine iteration. Judges on content (accuracy,
    completeness), structure (organization, formatting, usability), and an overall score.
  - **Analyzer**: finds statistical patterns across the benchmark -- non-discriminating
    assertions (pass in both configs), high-variance evals (results swing run-to-run =
    unstable), and time/token trade-offs (skill raises quality but also cost).

  ### Iterative improvement loop

  Core loop: **write -> run tests -> evaluate -> improve -> re-test.**
  1. Edit the skill.
  2. Re-run all test cases into a fresh `iteration-N+1/` directory.
  3. Present results to the user, compared against the previous iteration.
  4. Collect feedback (empty feedback = "no issues").
  5. Edit again and repeat.

  Improvement principles:
  - **Generalize the feedback** -- a narrow fix that only matches the test example is
    overfitting; fix at the principle level.
  - **Remove what does not earn its weight** -- read the transcript; if the skill makes the
    agent do unproductive work, delete that part.
  - **Explain the why** -- even when user feedback is terse, understand why it matters and
    fold that understanding into the skill.
  - **Bundle repeated work** -- if every test run regenerates the same helper script,
    pre-include it under `scripts/`.
  - **Draft-then-reread** -- after editing the skill, reread it with fresh eyes and improve;
    do not try to write it perfectly in one pass.

  Stop conditions: user is satisfied, all feedback is empty, or no meaningful improvement
  remains.

  ### Automated description optimization (optional, advanced)

  When a description needs tuning:
  1. Split the 20 eval queries Train (60%) / Test (40%).
  2. Measure trigger accuracy with the current description.
  3. Analyze failure cases and generate an improved description.
  4. Select the best description on the **Test** set, not the Train set (avoid overfitting).
  5. Iterate up to 5 times.

  This runs as an automation script (e.g. via `claude -p`). Token cost is high, so run it
  as a final step only after the skill is otherwise stable.

  ### Workspace structure

  Keep test/eval results in a structured directory:
  ```
  {skill-name}-workspace/
  |-- iteration-1/
  |   |-- eval-descriptive-name-1/
  |   |   |-- eval_metadata.json
  |   |   |-- with_skill/
  |   |   |   |-- outputs/
  |   |   |   |-- timing.json
  |   |   |   `-- grading.json
  |   |   `-- without_skill/
  |   |       |-- outputs/
  |   |       |-- timing.json
  |   |       `-- grading.json
  |   |-- eval-descriptive-name-2/
  |   |   `-- ...
  |   `-- benchmark.json
  |-- iteration-2/
  |   `-- ...
  `-- evals/
      `-- evals.json
  ```
  Rules: name eval directories descriptively (e.g. `eval-multi-page-table-extraction`), not
  by number; keep each iteration in its own directory (never overwrite a prior iteration);
  do not delete `_workspace/` -- it is the post-hoc verification and audit trail.

- **Anti-pattern**: Testing only that a skill triggers and never measuring whether it
  improves output (or vice versa). Also: should-NOT-trigger queries that are obviously
  unrelated -- they inflate precision without testing the real boundary. Also: keeping
  non-discriminating assertions that pass in both configs and pretending they validate the
  skill.

---

# Template: Self-Learning Rule (03-self-learning.md)

<!-- TEMPLATE ANNOTATION
  This template defines how the generated environment learns from use.
  It establishes friction categories, detection heuristics, cold-start seeding,
  and the evaluation-driven development methodology for self-improvement.

  QUALITY CRITERIA:
  - Under 120 lines in generated output
  - Friction categories fully enumerated with examples
  - Detection heuristics for automatic logging
  - Cold-start seeding with 3-5 domain patterns
  - Bootstrapping thresholds (lower early, normal later)
  - Evaluation-driven methodology
  - Premature victory prevention
  - First-week review trigger

  WHY THIS EXISTS:
  Generated environments are untested. They will have routing mistakes, missing
  permissions, threshold errors, and workflow gaps. The self-learning system
  detects these problems from actual usage patterns and proposes targeted fixes.
  Without it, the same friction repeats forever.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: FastAPI + React web application
============================================================ -->

# Self-learning

<!-- CORE PRINCIPLE
  WHY: Sets expectations that this is an evolving system, not a fixed one.
-->
This environment improves with use. Friction is logged, patterns are detected,
and improvements are proposed through `/update`.

## Friction categories

<!-- FRICTION CATEGORIES
  WHY: Categorizing friction enables pattern detection. "FRICTION" alone is too
  broad -- you cannot distinguish routing problems from permission problems.
  Each category has a specific remediation path.
-->
Log observations to `Docs/_working/retro/YYYY-MM.md` using these categories:

| Category | When to log | Example |
|---|---|---|
| FRICTION | A workflow step caused notable delay or required workaround | "Had to manually find the test file because explorer returned wrong directory" |
| WIN | Something worked surprisingly well | "Debugger correctly identified the N+1 query on first attempt" |
| CORRECTION | User corrected Claude's behavior or output | "User said 'do not add type hints to test files' -- not in rules" |
| PATTERN | Same friction observed 2+ times | "Third time explorer missed the middleware directory" |
| SKILL_UNDERTRIGGER | A skill should have triggered but did not | "/state-save not triggered when user said 'save my progress'" |
| SKILL_OVERTRIGGER | A skill triggered when it should not have | "/health-check triggered when user said 'check this code'" |
| ROUTING_CORRECTION | User redirected to a different agent | "Routed to debugger but user wanted performance analysis" |

Format: `- YYYY-MM-DD [CATEGORY] observation (context)`

Keep entries to one line. Do not log routine successful operations.

## Detection heuristics

<!-- DETECTION HEURISTICS
  WHY: Relying on Claude to remember to log friction is unreliable.
  These heuristics trigger automatic logging based on observable signals.
-->
Automatically log when detecting:

- **Negation words after Claude output**: "No, that's wrong", "Not what I meant", "Don't do that"
  -> Log as CORRECTION with the user's correction
- **Repeated request**: User asks the same thing a second time with different wording
  -> Log as FRICTION with "user had to rephrase"
- **Explicit instruction**: "Remember this", "Always do X", "Never do Y"
  -> Log as CORRECTION with the new rule
- **Skill invocation mismatch**: User types `/skill-name` manually after Claude did not auto-invoke
  -> Log as SKILL_UNDERTRIGGER
- **Agent redirect**: "No, use the researcher for this" or "Don't use debugger, just look at the code"
  -> Log as ROUTING_CORRECTION

## Cold-start seeding

<!-- COLD-START SEEDING
  WHY: A new environment has no friction data. Without seed entries, the self-learning
  system cannot detect patterns until many sessions have passed. Pre-seeding with
  known patterns from the starter profile bootstraps the system immediately.
-->
The following patterns are pre-seeded from the starter profile. They trigger on
their first real occurrence (threshold = 1 instead of the normal 3):

```
- [PATTERN] (pre-seeded) Context exhaustion during large refactors -- consider splitting by module
- [PATTERN] (pre-seeded) Routing ambiguity between "fix" and "refactor" -- check user intent
- [PATTERN] (pre-seeded) Permission prompts for new file paths outside Docs/ -- update settings.json
- [PATTERN] (pre-seeded) Agent produces code mismatching project conventions -- add convention to rules
- [PATTERN] (pre-seeded) State-load missing recently added files -- update state-save categories
```

## Bootstrapping thresholds

<!-- BOOTSTRAPPING THRESHOLDS
  WHY: Early in the environment's life, fewer observations should trigger
  improvement proposals. After 30 days, require more evidence to avoid
  over-reacting to isolated incidents.
-->

| Time period | Entries needed to trigger proposal | Pre-seeded pattern threshold |
|---|---|---|
| First 30 days | 2 entries in same category | 1 real entry (matches seed) |
| After 30 days | 3 entries in same category | 2 real entries |

At 5+ friction entries in an uncovered category, suggest creating a new
agent, rule, or skill to address the gap.

## Evaluation-driven methodology

<!-- EVALUATION-DRIVEN DEVELOPMENT
  WHY: Changing rules or routing without evidence makes things worse.
  The evaluation loop ensures changes actually help before committing them.
  "Build evaluations FIRST to ensure you solve real problems."
-->
When `/update` proposes an improvement:

1. **Identify gap**: Find the friction entries that reveal the problem
2. **Build test scenario**: Create a concrete scenario that would trigger the friction
3. **Establish baseline**: How does the current environment handle this scenario?
4. **Write minimal change**: The smallest rule/routing/threshold edit that addresses the gap
5. **Evaluate**: Does the change improve the scenario without degrading other behavior?
6. **Iterate**: If not improved, try a different approach. If improved, commit the change.

## Premature victory prevention

<!-- PREMATURE VICTORY
  WHY: Agents tend to mark improvements as "done" before verifying they work.
  This requires explicit verification before closing out an improvement.
-->
Before marking any improvement as complete:
- Verify the change actually addresses the original friction
- Check that the change does not contradict existing rules
- Confirm no new friction was introduced by the change
- Log the outcome in `Docs/Environment/EVOLUTION.md`

Do not mark improvements complete based on "this should fix it." Verify.

## Iteration signals for skills

<!-- SKILL ITERATION
  WHY: Skill descriptions are the primary discovery mechanism. Undertriggering
  means the description is missing keywords. Overtriggering means the description
  is too broad or missing negative triggers.
-->
- **Undertriggering** (SKILL_UNDERTRIGGER logged): Add trigger phrases to the skill description
- **Overtriggering** (SKILL_OVERTRIGGER logged): Add negative triggers ("Do NOT use for...")
- Rewriting skill descriptions has ~40% evidence of improving behavior

## First-week review

<!-- FIRST-WEEK REVIEW
  WHY: The first 5-7 sessions surface the most obvious friction. An early review
  catches configuration errors before they become habits.
-->
After 5 sessions or 7 calendar days (whichever comes first), automatically
produce a brief status report:
- Count of entries per friction category
- Top 3 friction items by frequency
- Any pre-seeded patterns that were confirmed
- Recommended first `/update` focus areas

Write this report to `Docs/_working/retro/first-week-review.md`.

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  SOFTWARE DEVELOPMENT (this example):
  - Seed patterns: context exhaustion, routing ambiguity, convention mismatch
  - Technical detection heuristics (build failures, test failures as friction signals)

  KNOWLEDGE WORK:
  - Seed patterns: jargon overuse, citation gaps, context loss between sessions
  - Detection: "too technical", "simplify", "cite your sources" as correction signals
  - Lower thresholds (fewer sessions expected per week)

  GAME DEVELOPMENT:
  - Seed patterns: playtest gate skipped, binary asset confusion, build failures
  - Additional category: PLAYTEST_FRICTION for playtest-related issues
  - Detection: build failure after implementation as automatic FRICTION

  CONSERVATIVE DOMAINS:
  - Seed patterns: unsourced claims, overconfident assertions, missing disclaimers
  - Additional category: SAFETY_CONCERN for guardrail-related friction
  - Tighter bootstrapping (1 entry triggers in first 60 days)
-->

<!-- ANTI-PATTERNS

  1. NO COLD-START SEEDING
     Problem: Environment has zero learning for weeks. Same friction repeats.
     Fix: Pre-seed 3-5 known patterns from the starter profile.

  2. LOGGING EVERYTHING
     Problem: Routine operations logged as friction. Signal drowned in noise.
     Fix: "Do not log routine successful operations." Only log notable events.

  3. CHANGING RULES WITHOUT EVIDENCE
     Problem: After one friction event, rewriting the routing table.
     Fix: Require 2-3 entries before proposing changes. Use evaluation-driven methodology.

  4. NO VERIFICATION STEP
     Problem: Improvement proposed, applied, marked done without checking.
     Fix: Premature victory prevention -- verify changes actually help.

  5. GENERIC FRICTION CATEGORIES
     Problem: Everything logged as "FRICTION" -- cannot distinguish routing from permission issues.
     Fix: Use the 7 specific categories. Each has a different remediation path.

  6. NO FIRST-WEEK REVIEW
     Problem: Obvious configuration errors persist for months.
     Fix: Auto-produce status report after 5 sessions or 7 days.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 120 lines in generated output
  [ ] All 7 friction categories listed with examples
  [ ] Detection heuristics present (at least 4 signals)
  [ ] Cold-start seeding with 3-5 domain-specific patterns
  [ ] Bootstrapping thresholds table (first 30 days vs after)
  [ ] Evaluation-driven methodology (6 steps)
  [ ] Premature victory prevention section
  [ ] Skill iteration signals (undertrigger/overtrigger)
  [ ] First-week review trigger defined
  [ ] Log format specified (date, category, observation, context)
  [ ] "Keep entries to one line" constraint present
  [ ] References /update skill and Docs/_working/retro/ structure
  [ ] ASCII-only
-->

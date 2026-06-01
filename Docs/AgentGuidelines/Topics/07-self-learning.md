# 7. Self-Learning

### 7.1 Evaluation-Driven Development

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md, test-and-evaluate.md | Tier 1
- **Recommendation**: Self-improvement should follow a rigorous cycle:
  1. **Identify gap** from friction log (FRICTION, CORRECTION entries)
  2. **Build test scenario** targeting the gap (3 scenarios minimum)
  3. **Establish baseline** -- measure current performance
  4. **Write minimal change** -- just enough to address the gap
  5. **Evaluate against baseline** -- verify improvement
  6. **Iterate** until verified improvement

  This prevents premature victory: explicitly verify that changes actually improve behavior
  before marking them complete. "Writing extensive documentation before evaluations" is an
  explicit anti-pattern -- build evaluations FIRST.
- **Anti-pattern**: Making prompt changes based on intuition without measuring impact. Changes
  that seem helpful may have no effect or may degrade other behaviors. Always measure.

### 7.2 Self-Improvement via Description Rewriting

- **Established**: 2025-09
- **Source**: multi-agent-research-system.md | Tier 1
- **Recommendation**: Claude 4 models can diagnose failures and suggest improvements to their
  own tool descriptions and prompts. In Anthropic's research system, a tool-testing agent
  rewrote MCP tool descriptions after dozens of attempts, yielding a "40% decrease in task
  completion time for future agents."

  Apply this to self-learning: when friction logs show consistent tool misuse or routing
  errors, propose description rewrites. Track before/after performance.
- **Anti-pattern**: Treating tool descriptions and routing rules as static. They should evolve
  based on observed agent behavior and friction patterns.

### 7.3 Iteration Signals for Skills

- **Established**: Baseline
- **Source**: agent-skills-best-practices.md | Tier 1
- **Recommendation**: Track two specific skill performance signals:
  - **Undertriggering**: Skill should have fired but did not. Fix: add keywords or trigger
    phrases to the description. Log as SKILL_UNDERTRIGGER.
  - **Overtriggering**: Skill fired when it should not have. Fix: add negative triggers or
    narrow the description. Log as SKILL_OVERTRIGGER.

  Both signals should be captured in the self-learning friction log with the skill name and
  the triggering (or non-triggering) phrase.
- **Anti-pattern**: Not tracking skill triggering accuracy. Without data, you cannot know
  whether descriptions need tuning.

### 7.4 Cold Start Seeding

- **Established**: Baseline
- **Source**: Derived from multi-agent-research-system.md, claude-code-best-practices.md | Tier 1
- **Recommendation**: New environments have no friction history, so self-learning cannot
  function until patterns accumulate. Seed 3-5 known patterns from the starter profile,
  marked as `[PATTERN] (pre-seeded)`:

  Example seeds for software development:
  - PATTERN: Context exhaustion on large refactors
  - PATTERN: Routing ambiguity between fix and refactor
  - PATTERN: Permission prompts for new file paths
  - PATTERN: Agent producing code mismatching project conventions
  - PATTERN: State-load missing recently added files

  Bootstrapping thresholds: require only 2 friction entries (instead of 3) during first
  30 days. Pre-seeded patterns trigger improvement proposals on 1 real entry instead of 3.

  Schedule first-week review: after 5 sessions or 7 days, auto-produce brief status report
  on environment health.
- **Anti-pattern**: Leaving self-learning empty at creation. Without seed patterns, the system
  cannot propose improvements until users have accumulated enough friction entries, which may
  take weeks.

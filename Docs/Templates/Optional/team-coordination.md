# Team Coordination Rule (Template)

<!-- ANNOTATION: Generate this rule when the environment uses Agent Teams
     (experimental) or heavy subagent delegation. This rule helps the
     orchestrator decide WHEN to use teams vs subagents and HOW to
     coordinate parallel work. Only include if the user's project
     complexity justifies multi-agent coordination. -->

<!-- QUALITY: Must include Teams vs Subagents decision matrix. Must include
     task sizing guidance. Must include file ownership rules. Must include
     scaling recommendations. Under 120 lines. -->

## Example: Team Coordination Rule (`.claude/rules/team-coordination.md`)

```markdown
# Team coordination

Guidelines for deciding between sequential subagents and parallel Agent Teams,
and for coordinating multi-agent work.

## Teams vs Subagents decision matrix

<!-- ANNOTATION: This is the core decision framework. The key insight is
     that teams are expensive (15x chat cost) and only justified when
     parallel exploration provides genuine value. Most work is serial. -->

| Criteria | Use Subagents | Use Agent Teams |
|----------|--------------|-----------------|
| Work structure | Serial (plan -> implement -> review) | 2+ independent areas in parallel |
| File overlap | Files may overlap | Non-overlapping file ownership |
| Communication | Result only (report back) | Teammates need to discuss/challenge |
| Complexity | Single-focus tasks | Competing hypotheses, cross-layer work |
| Cost sensitivity | Budget-conscious | Speed over cost |
| Default | YES (default to this) | Only when clearly beneficial |

When in doubt, use subagents. Teams add coordination overhead that is only
worthwhile for genuinely parallel work.

<!-- ANTI-PATTERN: Do not use teams for simple tasks. A team of 3 agents
     costs roughly 15x a single chat interaction. Do not create a team
     just because a task has multiple steps -- that is what sequential
     subagents are for. -->

## When teams help vs hurt

Teams HELP when:
- Research + code exploration can happen simultaneously
- Debugging competing hypotheses (each teammate tests one theory)
- Large feature spans non-overlapping areas (frontend + backend + tests)
- Multiple independent investigations with shared conclusions

Teams HURT when:
- Work is naturally sequential (output of step N feeds step N+1)
- Files overlap between workers (merge conflicts, stomped changes)
- The task is simple enough for one focused agent
- Budget is constrained

## Task sizing

<!-- ANNOTATION: Task sizing prevents both over-splitting (too many tiny
     tasks with coordination overhead) and under-splitting (one massive
     task that exhausts context). -->

When creating tasks for teammates:
- Target 5-6 tasks per teammate (enough to stay busy, not so many they lose focus)
- Each task should be independently completable
- Each task should have clear success criteria
- Include dependencies between tasks when ordering matters

## File ownership

<!-- ANNOTATION: File ownership prevents concurrent edits to the same
     file, which cause data loss in multi-agent scenarios. This is the
     single most important coordination rule. -->

Each file should have exactly one owner at any time:
- Assign files to teammates at task creation time
- If two tasks need the same file, make them sequential (not parallel)
- Use a shared document or task list to track who owns what
- Owner must complete and release files before another agent edits them

<!-- VARIATION: For Git-based projects, git worktrees provide natural
     file isolation. Each teammate can work in a separate worktree.
     For Perforce, file-level locking is built into the system. -->

## Subagent scaling by complexity

<!-- ANNOTATION: This table provides a quick reference for how many
     subagents to use based on task complexity. It prevents both
     over-delegation (spawning 5 agents for a typo fix) and
     under-delegation (trying to do a complex feature in one context). -->

| Complexity | Subagents | Tool calls each | Example |
|------------|-----------|-----------------|---------|
| Simple | 1 | <5 | Fix a typo, update a config value |
| Standard | 2-3 | 10-15 | Bug fix with investigation and review |
| Complex | 3-5 | 15-25 | Feature with planning, implementation, review |
| Large | 5-10 | 20-30+ | Multi-area refactor with testing |

## Parallel execution patterns

<!-- VARIATION: Include the patterns relevant to the project's VCS
     and development environment. -->

### Fan-out pattern
For tasks that can be investigated independently:
1. Orchestrator defines N investigation tasks
2. Each subagent/teammate works independently
3. Results collected and synthesized by orchestrator
4. Best approach selected for implementation

### Task locking
When multiple agents share a workspace:
- Use file-based locks or VCS locking to prevent conflicts
- Each agent claims a task before starting
- Task is released only after completion or explicit abandonment

## Fast test mode

<!-- ANNOTATION: During parallel work, running full test suites on every
     change is wasteful. This section defines a lightweight validation
     that agents can run during development, with full testing reserved
     for integration. -->

During parallel development, use fast validation:
- Run only tests related to the changed files
- Save full test suite for after integration
- Each agent verifies their own changes independently
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] Teams vs Subagents matrix present with clear criteria
     - [ ] Default recommendation is subagents (teams are opt-in)
     - [ ] Task sizing guidance (5-6 per teammate)
     - [ ] File ownership rule (one owner per file at a time)
     - [ ] Complexity scaling table present
     - [ ] Cost awareness mentioned (teams are 15x)
     - [ ] Under 120 lines
-->

# 4. Agent Teams, Parallelism, and Team-Architecture Patterns

This topic covers three related areas: when to use agent teams versus
subagents (and what they cost), the mechanics of parallel and background
execution, and a shared vocabulary of named team-architecture patterns the
environment-architect records in ARCHITECTURE.md.

**Cost-safety default (resolves teams-vs-parallel guidance):** Subagents are
the cost-safe default. Agent teams sit behind an experimental flag, cost
roughly 15x a single chat, and are opt-in *per phase* where real-time
peer collaboration adds value that exceeds the cost. The pattern catalogue
below names several patterns whose "natural" implementation is an agent team;
that is a description of where teams shine, not a recommendation to switch
the default. Only reach for a team on a phase that genuinely benefits from
inter-agent communication.

## Table of contents

- 4.1 Decision Matrix: Teams vs. Subagents [ALL]
- 4.2 Token Economics [ALL]
- 4.3 Task Sizing [ALL]
- 4.4 File Ownership [ALL]
- 4.5 Quality Gate Hooks [ALL]
- 4.6 Task Locking via Filesystem [ALL]
- 4.7 Fan-Out Pattern (headless) [ALL]
- 4.8 Stakeholder Review Team Pattern [ALL]
- 4.9 Human Review Gate Pattern [ALL]
- 4.10 Git Worktree Isolation [ALL]
- 4.11 Parallelism Helps/Hurts Matrix [ALL]
- 4.12 Parallel Tool Use Prompting [ALL / 4.7+ note]
- 4.13 Git Worktrees for Parallel Sessions [ALL]
- 4.14 Container-Based Parallel Execution [ALL]
- 4.15 Dynamic Workflows (Opus 4.8, research preview) [4.8]
- 4.16 Team-Architecture Patterns (design vocabulary) [ALL]

---

### 4.1 Decision Matrix: Teams vs. Subagents [ALL]

- **Established**: Baseline
- **Source**: agent-teams.md, multi-agent-research-system.md | Tier 1
- **Recommendation**:

  | Criteria | Use Subagents | Use Agent Teams |
  |----------|--------------|-----------------|
  | Work pattern | Serial (plan->implement->review) | Parallel, independent areas |
  | Communication | Report back to main only | Peer-to-peer discussion needed |
  | File ownership | Same files across phases | Non-overlapping file ownership |
  | Complexity | Single focused task | Complex work requiring collaboration |
  | Token budget | Lower (~4x chat) | Higher (~15x chat) |
  | Coordination | Main agent manages all | Shared task list, self-coordination |
  | Best for | Focused tasks where only result matters | Competing hypotheses, cross-layer work |

  Default to subagents unless the task clearly benefits from parallelism and inter-agent
  communication.
- **Anti-pattern**: Using Agent Teams for simple serial workflows. The coordination overhead
  and token cost (15x) make teams wasteful for tasks that do not benefit from parallelism.

### 4.2 Token Economics [ALL]

- **Established**: 2025-09
- **Source**: multi-agent-research-system.md, agent-teams.md | Tier 1
- **Recommendation**: Understand the cost multipliers before choosing architecture:
  - Single chat: 1x baseline
  - Subagent invocation: ~4x baseline (separate context window)
  - Agent Teams: ~15x baseline (each teammate is a separate Claude instance)

  Token usage alone explains 80% of performance variance in research tasks. More tokens
  (more exploration, more tool calls) improves results, but with diminishing returns. Budget
  accordingly: use teams only when parallelism provides clear value exceeding the 15x cost.

  Rough cost guide: parallel Claude sessions averaged ~$10/session in the C compiler project
  ($20K over ~2,000 sessions, 2B input + 140M output tokens).
- **Anti-pattern**: Ignoring token costs when designing multi-agent architectures. A 5-teammate
  team costs ~75x a single chat. Without clear parallel value, this is wasteful.

### 4.3 Task Sizing [ALL]

- **Established**: Baseline
- **Source**: agent-teams.md | Tier 1
- **Recommendation**: Aim for 5-6 tasks per teammate. Tasks should be:
  - Self-contained units that produce clear deliverables (a function, a test file, a review)
  - Large enough to justify the coordination overhead
  - Small enough that teammates do not work too long without check-ins

  Too-small tasks: coordination overhead exceeds benefit. Too-large tasks: teammates work
  too long, increasing wasted effort risk on wrong approaches.
- **Anti-pattern**: Assigning one monolithic task per teammate (loses parallelism benefit) or
  dozens of micro-tasks (coordination overhead dominates).

### 4.4 File Ownership [ALL]

- **Established**: Baseline
- **Source**: agent-teams.md | Tier 1
- **Recommendation**: Break work so each teammate owns different files. Two teammates editing
  the same file leads to overwrites. Use task descriptions to explicitly assign file
  ownership: "You own all files in src/auth/. Do not modify files outside this directory."

  Task claiming uses file locking to prevent race conditions, but file-level conflicts
  within a task are not automatically prevented.
- **Anti-pattern**: Multiple teammates modifying the same file concurrently. File-level
  conflicts cause silent data loss since teammates do not see each other's changes in real time.

### 4.5 Quality Gate Hooks [ALL]

- **Established**: Baseline
- **Source**: agent-teams.md, claude-code-docs.md | Tier 1
- **Recommendation**: Use team-specific hooks for quality control:
  - `TeammateIdle`: Runs when a teammate is about to go idle. Exit code 2 sends feedback
    and keeps the teammate working. Use for: "Run tests before going idle."
  - `TaskCompleted`: Runs when a task is being marked complete. Exit code 2 prevents
    completion and sends feedback. Use for: "Verify all tests pass before marking complete."

  These hooks are the primary mechanism for preventing premature completion -- a major
  failure mode in autonomous agents.
- **Anti-pattern**: Running teams without quality gate hooks. Agents frequently declare
  tasks complete without proper verification (premature victory declaration).

### 4.6 Task Locking via Filesystem [ALL]

- **Established**: Baseline
- **Source**: parallel-claudes-c-compiler.md | Tier 1
- **Recommendation**: For parallel agents working on a shared codebase, use simple file-based
  locking. Agents write text files to a `current_tasks/` directory (e.g.,
  `parse_if_statement.txt`) to signal what they are working on. Other agents check this
  directory before claiming tasks. Remove lock files when work completes.

  This pattern requires no external infrastructure -- just filesystem coordination.
- **Anti-pattern**: No coordination mechanism between parallel agents. Without locking,
  multiple agents may work on the same problem simultaneously, wasting tokens on duplicate
  effort.

### 4.7 Fan-Out Pattern (headless) [ALL]

- **Established**: Baseline
- **Source**: claude-code-best-practices.md | Tier 1
- **Recommendation**: For repetitive tasks across many files:
  1. Have Claude list all files needing the operation
  2. Script the operation: `for file in $(cat files.txt); do claude -p "Migrate $file..." done`
  3. Test on 2-3 files first, refine the prompt, then run at scale

  This is simpler than Agent Teams and appropriate when each file's transformation is
  independent and follows the same pattern. (For the team-architecture meaning of fan-out
  with result integration, see pattern 2 in 4.16.)
- **Anti-pattern**: Using Agent Teams for embarrassingly parallel tasks that do not require
  inter-agent communication. Fan-out with headless mode is cheaper and simpler.

### 4.8 Stakeholder Review Team Pattern [ALL]

- **Established**: 2026-02
- **Source**: production compliance project production environment | Tier 2
- **Recommendation**: For domains requiring multi-perspective review (legal, compliance,
  consulting, policy), use Agent Teams with perspective-specific agents. Each agent
  reviews from a different stakeholder viewpoint:

  Example (regulatory compliance):
  - Technical Accuracy Reviewer: verifies technical claims against standards
  - Compliance Reviewer: checks regulatory alignment
  - Risk Reviewer: identifies operational risks
  - Business Impact Reviewer: assesses practical implications
  - Language Reviewer: ensures professional tone and clarity

  A consensus-builder agent then resolves conflicts between perspectives using a
  priority hierarchy (e.g., compliance > accuracy > risk > business > language).

  This pattern uses Agent Teams for parallel review (all 5 perspectives simultaneously),
  making it faster than sequential review while ensuring comprehensive coverage. It is a
  concrete instance of the Fan-out/Fan-in pattern (4.16, pattern 2).
- **Anti-pattern**: Sequential single-perspective review for compliance documents.
  This takes 5x longer and still misses cross-perspective conflicts. The parallel
  pattern catches issues that no single perspective would identify.

### 4.9 Human Review Gate Pattern [ALL]

- **Established**: 2026-02
- **Source**: production compliance project production environment | Tier 2
- **Recommendation**: For domains where output goes to external audiences (clients,
  regulators, courts), implement a mandatory human review gate. Use a structured
  marker in output to signal the stop point:

  ```
  <pause id="PT-01">NEEDS_REVIEW</pause>
  ```

  The assistant MUST stop and wait for human approval before proceeding past the
  gate. This is enforced in the routing table -- certain routes include an explicit
  "-> STOP for human review" step.

  Combine with: deny rules preventing Write to original/client documents (only write
  to working copies), and audit trail hooks logging all review decisions.
- **Anti-pattern**: Relying on CLAUDE.md instructions alone to stop for review.
  Instructions are advisory. Use deny rules + structured markers + routing table
  enforcement for guaranteed human review gates.

### 4.10 Git Worktree Isolation [ALL]

- **Established**: 2026-02
- **Source**: claude-code-docs.md | Tier 1
- **Recommendation**: For parallel agent work on Git-based projects, use Claude Code's
  built-in worktree support (`--worktree` flag) instead of Agent Teams. Each agent gets
  its own git worktree -- a separate working directory with its own branch -- preventing
  file conflicts entirely.

  ```bash
  # Launch Claude in an isolated worktree
  claude --worktree feature-auth
  claude -w bugfix-login
  ```

  Worktrees are lighter than Agent Teams (~4x cost vs ~15x) and provide true filesystem
  isolation. Subagents can also use worktree isolation automatically.

  **When to use worktrees vs Agent Teams:**
  - Worktrees: 2-3 parallel tasks on the same repo, each touching different files
  - Agent Teams: Complex coordination requiring peer-to-peer communication
  - Neither: Sequential work where tasks depend on each other

  Worktrees are automatically cleaned up when the agent finishes without changes.
- **Anti-pattern**: Running multiple agents on the same working directory without isolation.
  Concurrent file edits cause silent data loss and merge conflicts.

### 4.11 Parallelism Helps/Hurts Matrix [ALL]

- **Established**: 2025-09
- **Source**: multi-agent-research-system.md, parallel-claudes-c-compiler.md | Tier 1
- **Recommendation**:

  | Scenario | Parallelism Helps | Parallelism Hurts |
  |----------|------------------|-------------------|
  | Independent file operations | Yes | - |
  | Research across multiple sources | Yes | - |
  | Non-overlapping code areas | Yes | - |
  | Competing debugging hypotheses | Yes | - |
  | Shared context needed across tasks | - | Yes |
  | High interdependency between tasks | - | Yes |
  | Sequential logic (plan->implement) | - | Yes |
  | Single bottleneck (all agents hit same bug) | - | Yes |

  Multi-agent underperforms for: tasks requiring shared context, high interdependencies
  (most coding tasks), real-time coordination. Multi-agent excels at: heavy parallelization,
  information exceeding single context windows, numerous complex tools.
- **Anti-pattern**: Forcing parallelism on inherently sequential or interdependent tasks.
  When all agents hit the same bottleneck, they all stall simultaneously.

### 4.12 Parallel Tool Use Prompting [ALL / 4.7+ note]

- **Established**: 2025-09
- **Source**: platform-agent-patterns.md | Tier 1
- **Recommendation**: Parallel tool use is default behavior in Claude. For explicit
  encouragement when needed:
  ```xml
  <use_parallel_tool_calls>
  For maximum efficiency, whenever you perform multiple independent operations,
  invoke all relevant tools simultaneously rather than sequentially. Prioritize
  calling tools in parallel whenever possible.
  </use_parallel_tool_calls>
  ```

  All tool results must be in a SINGLE user message (not separate messages) for parallel
  tool use. Tool_result blocks must come FIRST in the content array, text AFTER.
- **Anti-pattern**: Violating the single-message constraint for tool results.
  Over-prompting for parallelism on Opus 4.6 (handles this well natively). For Opus 4.7+,
  which is more conservative by default, some explicit guidance IS useful if you want
  aggressive parallelism -- see topic 13.12 and 13.16.

### 4.13 Git Worktrees for Parallel Sessions [ALL]

- **Established**: Baseline
- **Source**: common-workflows.md | Tier 1
- **Recommendation**: Use git worktrees for parallel Claude sessions without Agent Teams:
  ```bash
  git worktree add ../project-feature-a -b feature-a
  git worktree add ../project-bugfix bugfix-123
  cd ../project-feature-a && claude
  cd ../project-bugfix && claude
  ```

  Each worktree has independent file state but shares git history and remotes. Must
  initialize the dev environment in each worktree (npm install, etc.).

  The `/resume` picker shows sessions from the same git repo including worktrees.

  This is simpler and cheaper than Agent Teams for work that does not require inter-agent
  communication.
- **Anti-pattern**: Using Agent Teams when simple parallel sessions via worktrees would
  suffice. Worktrees have zero coordination overhead.

### 4.14 Container-Based Parallel Execution [ALL]

- **Established**: Baseline
- **Source**: parallel-claudes-c-compiler.md | Tier 1
- **Recommendation**: For fully autonomous parallel execution, use Docker containers:
  - Mount repo to `/upstream` in the container
  - Clone locally to `/workspace` for isolated work
  - Each container gets a fresh environment
  - Use file-based locking (`current_tasks/` directory) for coordination
  - Continuous loop harness:
    ```bash
    while true; do
      COMMIT=$(git rev-parse --short=6 HEAD)
      claude --dangerously-skip-permissions -p "$(cat AGENT_PROMPT.md)" \
             &> "agent_logs/agent_${COMMIT}.log"
    done
    ```

  This pattern was used to build a 100,000-line C compiler across ~2,000 sessions.
- **Anti-pattern**: Running parallel autonomous agents without container isolation. Without
  filesystem isolation, agents can interfere with each other's work.

### 4.15 Dynamic Workflows (Opus 4.8, research preview) [4.8]

- **Established**: 2026-05-31
- **Source**: anthropic.com/news/claude-opus-4-8, code.claude.com/docs/en/changelog
  (v2.1.154) | Tier 1
- **Recommendation**: Opus 4.8 + Claude Code can plan a task and then run tens-to-hundreds
  of parallel subagents in the background within a single session, verifying their output
  before reporting. View runs with `/workflows`; a live agent count shows in the status row.
  Available on Enterprise, Team, and Max plans only.

  This is a higher-level, model-managed alternative to the manual worktree (4.13) and
  container (4.14) patterns for large-scale work -- the model decides the decomposition.
  When recommending it in a generated environment, gate on plan tier and note it is a
  research preview (behavior may change).

  **Keyword collision**: the literal word "workflow" in a prompt can trigger dynamic
  workflows. Environments that use "workflow" as domain vocabulary (e.g., a CI/CD or
  business-process project) should set the `Workflow keyword trigger` setting (v2.1.157)
  to suppress accidental activation, and GETTING_STARTED.md should mention this.
- **Anti-pattern**: Recommending dynamic workflows for small/medium tasks where a handful of
  subagents or worktrees suffice -- the orchestration overhead is only justified at scale.

---

### 4.16 Team-Architecture Patterns (design vocabulary) [ALL]

- **Established**: Baseline
- **Source**: agent-design-patterns.md | Tier 1
- **Recommendation**: These six named patterns are design vocabulary the
  environment-architect should record in ARCHITECTURE.md when laying out a
  multi-agent environment. Naming the pattern makes the topology, the
  agent-team-vs-subagent decision, and the failure mode explicit and reviewable.

  Reminder on execution mode: per 4.1-4.2, **subagents are the cost-safe default**;
  agent teams (experimental flag, ~15x cost) are opt-in per phase where real-time
  peer collaboration adds value. The "team-mode suitability" notes below describe
  where a team's peer communication genuinely helps -- treat them as the signal for
  when the team premium is worth paying, not as a blanket recommendation to switch
  away from subagents.

  Quick reference:

  | Pattern | Shape | Default execution mode |
  |---------|-------|------------------------|
  | 1. Pipeline | sequential dependent | Subagents (team only if a stage is internally parallel) |
  | 2. Fan-out/Fan-in | parallel independent + merge | Agent team (where peer sharing helps); subagents acceptable if pure result hand-off |
  | 3. Expert Pool | context-dependent selective | Subagents |
  | 4. Producer-Reviewer | generate then review loop | Subagents default; agent team where tight real-time feedback cuts rework |
  | 5. Supervisor | central dynamic distribution | Agent team's shared task list maps naturally; subagents with a managing main also work |
  | 6. Hierarchical Delegation | recursive top-down | Subagents (teams cannot nest); flatten to a single team if needed |

#### Pattern 1 -- Pipeline (sequential dependent)

Sequential flow where each agent's output is the next agent's input:
`[Analyze] -> [Design] -> [Implement] -> [Verify]`.

- **When to use**: Each stage depends strongly on the prior stage's deliverable.
- **Example**: Novel writing -- worldbuilding -> characters -> plot -> drafting -> editing.
- **Agent-team vs subagent suitability**: Strong sequential dependency limits the
  benefit of team mode, so **subagents are the natural fit**. Reach for a team only
  if a stage has an internally parallel segment that benefits from peer communication.
- **Anti-pattern**: A bottleneck stage stalls the whole pipeline. Design each stage to
  be as independent as possible so a slow or blocked stage does not freeze everything.

#### Pattern 2 -- Fan-out/Fan-in (parallel independent)

Parallel processing followed by integration -- independent work done concurrently,
then merged:
`[Distribute] -> {Expert A | Expert B | Expert C} -> [Integrate]`.

- **When to use**: The same input needs analysis from several different
  perspectives or domains at once.
- **Example**: Comprehensive research -- official sources / media / community /
  background investigated simultaneously, then merged into one report. (The
  Stakeholder Review Team in 4.8 is a production instance of this.)
- **Agent-team vs subagent suitability**: This is the most natural agent-team
  pattern -- it is where the team premium most clearly earns its cost. Teammates
  share findings and challenge each other, and one agent's discovery can redirect
  another's investigation in real time, raising quality well above isolated
  parallel runs. Use subagents only when the work is pure independent result
  hand-off with no benefit from cross-talk.
- **Anti-pattern**: A weak integration stage. The merge step's quality determines
  overall quality; treating fan-in as an afterthought wastes the parallel work.

#### Pattern 3 -- Expert Pool (context-dependent selective)

A router selectively calls the appropriate specialist:
`[Router] -> { Expert A | Expert B | Expert C }`.

- **When to use**: Different input types require different handling, and only the
  relevant specialist should run.
- **Example**: Code review -- invoke only the security, performance, or architecture
  specialist whose domain the change touches.
- **Agent-team vs subagent suitability**: **Subagents are the better fit.** Because
  only the needed specialist is called per input, a standing team is unnecessary
  overhead.
- **Anti-pattern**: A misclassifying router. The router's classification accuracy is
  the linchpin; a wrong route sends work to the wrong specialist and the pattern fails.

#### Pattern 4 -- Producer-Reviewer (generate then review)

A producer agent and a reviewer agent operate as a pair, looping on failure:
`[Produce] -> [Review] -> (on issue) -> [Produce] again`.

- **When to use**: Output quality matters and an objective review criterion exists.
- **Example**: Webcomic generation -- artist produces panels -> reviewer inspects ->
  problem panels are regenerated.
- **Agent-team vs subagent suitability**: Subagents are a safe, cheap default
  (orchestrator runs producer, then reviewer, then loops). An **agent team is useful
  where tight real-time producer<->reviewer feedback via direct messaging meaningfully
  cuts rework** -- pay the team premium only when that loop is the bottleneck.
- **Anti-pattern**: No retry cap, leading to an infinite regenerate/review loop. Always
  set a maximum retry count (2-3) so the loop terminates.

#### Pattern 5 -- Supervisor (central dynamic distribution)

A central agent tracks task state and dynamically distributes work to workers:
`[Supervisor] -> {Worker A | Worker B | Worker C}`, assigning based on live progress.

- **When to use**: Workload is variable or the distribution must be decided at runtime
  rather than fixed up front.
- **Example**: Large-scale code migration -- the supervisor analyzes the file list and
  assigns batches to workers as they free up.
- **Difference from Fan-out**: Fan-out fixes the work split in advance; the Supervisor
  adjusts distribution dynamically while watching progress.
- **Agent-team vs subagent suitability**: An agent team's **shared task list maps
  naturally** to the supervisor pattern -- register work with TaskCreate and let
  teammates self-request tasks. A managing main agent dispatching subagents also works
  where peer communication is not needed.
- **Anti-pattern**: The supervisor becomes the bottleneck. Set delegation units large
  enough that the supervisor is not re-planning on every tiny step.

#### Pattern 6 -- Hierarchical Delegation (recursive top-down)

A higher-level agent recursively delegates to lower-level agents, decomposing a
complex problem in stages:
`[Lead] -> [Manager A] -> [IC A1, IC A2]; [Lead] -> [Manager B] -> [IC B1]`.

- **When to use**: The problem decomposes naturally into a hierarchy.
- **Example**: Full-stack app development -- lead -> frontend manager (UI / logic /
  tests) + backend manager (API / DB / tests).
- **Agent-team vs subagent suitability**: Agent teams **cannot nest** (a teammate
  cannot create its own team). Implement level 1 as a team and level 2 as subagents,
  or flatten the hierarchy into a single team. **Subagents are the natural recursive
  vehicle.**
- **Anti-pattern**: Going three or more levels deep -- latency and context loss grow
  sharply. Keep delegation to two levels or fewer.

#### Composite patterns

Real work often combines these rather than using one in isolation:

| Composite | Composition | Example |
|-----------|-------------|---------|
| Fan-out + Producer-Reviewer | Parallel generation, then review each | Multi-language translation -- 4 languages translated in parallel, each checked by a native-speaker reviewer |
| Pipeline + Fan-out | Parallelize one stage of a sequence | Analysis (sequential) -> implementation (parallel) -> integration test (sequential) |
| Supervisor + Expert Pool | Supervisor dynamically invokes specialists | Customer-inquiry handling -- supervisor classifies the inquiry, then assigns the right specialist |

  Execution mode for composites: the source guidance favors agent teams for composite
  patterns because active teammate communication drives result quality (research+analysis,
  design+implement+verify, supervisor+worker, produce+review). Reconciled with the
  Harness Generator's cost-safe default: keep subagents as the baseline and adopt a team only on the
  specific composite phase where peer communication is the quality driver and the ~15x
  premium is justified. Pure isolated one-shot work stays on subagents.

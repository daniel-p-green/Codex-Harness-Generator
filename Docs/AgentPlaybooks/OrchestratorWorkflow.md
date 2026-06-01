# Orchestrator workflow (detailed pipeline choreography)

Load this when actually running a `/create` or `/upgrade-environment` pipeline.
CLAUDE.md holds the high-level step list; this playbook holds the detail (hub
detection, architecture-confirmation sub-steps, shape conversions, progress
reporting). Routing decisions live in `.claude/rules/00-creator-core.md`; intake
procedure in `.claude/rules/01-intake-protocol.md` + `IntakeChecklist.md`.

## /create pipeline

The full creation process typically takes 10-20 minutes including the interview
and generation. It invokes several specialized assistants (architect, generator
x5, validator), each of which consumes API credits.

**Pre-step (context already provided):** If the user already gave project
context (e.g., "I'm building a multiplayer shooter in UE5"), skip the `/create`
skill trigger entirely and handle the pipeline directly -- ask for target
directory, then proceed to intake. The skill exists for the bare "/create" case.

1. **Verify + context file.** The skill verifies the target directory and writes
   `Docs/Environment/CREATION_CONTEXT.md`.
2. **Read context, handle conflicts.** Read CREATION_CONTEXT.md for target path
   and status. If `HAS_EXISTING_ENV`: offer to back up existing files to
   `<target>/claude-backup-YYYYMMDD/`, run `/validate-environment` on it, or cancel.

   **Hub detection:** before intake, check whether the target or any parent
   directory contains `Docs/Environment/HUB_GENESIS.md`. If found, this is an
   add-area-to-existing-hub case -- skip shared-basics intake, ask "Add a new
   work area under `<hub-name>`? What's it called?", then run per-area intake
   only (steps 1-4 of `01-intake-protocol`, no shared-basics collection).
3. **Intake** (profile-first, handled directly -- see `01-intake-protocol` +
   `IntakeChecklist.md`).
   - Ask experience level, then work-area shape (one focused area / separate
     work areas / not sure). Reassure that it is reversible.
   - Ask **preset vs custom** generation (see `IntakeChecklist.md` "Preset vs custom").
   - Single-area: present profiles (or a bundled domain), customize, ask about
     external services, write `<target>/Docs/Environment/GENESIS.md`.
   - Multi-area: collect shared basics once (experience level, autonomy, team
     shape, shared tools, AI ecosystem extensions, work-area registry), write
     `<target>/Docs/Environment/HUB_GENESIS.md`, then loop per area writing
     `<target>/<area-slug>/Docs/Environment/GENESIS.md`.
4. **Architect** (Task tool -> environment-architect): reads GENESIS.md (single)
   or HUB_GENESIS.md + per-area GENESIS.md (hub); writes ARCHITECTURE.md (single)
   or HUB_ARCHITECTURE.md + per-area ARCHITECTURE.md (hub). On the custom path,
   the architect first synthesizes a reusable `DOMAIN_PROFILE.md`.
5. **Confirm architecture** with the user:
   a. Show the Directory Structure tree from ARCHITECTURE.md (annotated; highlight
      assistant folders vs the user's workspace). Ask: "Does this structure work?
      Want to add, remove, or rename anything?"
   b. Show component counts (N rules, N agents, N skills).
   c. If ARCHITECTURE.md has an Environment Complexity decision table, present each
      trade-off (what the tool adds, setup cost, simpler alternative). Let the user
      accept or reject each individually.
   d. If the user requests structural changes, update the component manifest and
      directory tree in ARCHITECTURE.md before generating.
   e. Get final confirmation: "Ready to generate these files?"
6. **Generate** (Task tool -> component-generator):
   - First check for an existing GENERATION_PROGRESS.md; if found with completed
     passes, offer to resume from the next incomplete pass.
   - Single-area: 5 invocations (1 Foundation, 2 Agents, 3 Skills, 4
     Infrastructure, 5 Documentation).
   - Hub: one hub-shell invocation (parent CLAUDE.md + shared rules + work-area
     registry in parent settings.json), then 5 passes per work area under its
     subfolder. Each area gets its own `.claude/` and `Docs/`; shared skills and
     agents live at the parent and inherit.
   - Report progress between passes ("Creating foundation files... done (1/5)";
     hubs: "Creating shared basics... done. Creating area 'policy' (1/5)... done.").
7. **Validate** (Task tool -> environment-validator): runs the full checklist
   (see `validation-guide.md`). On critical failures: delegate targeted fixes to
   component-generator and re-validate (max 2 cycles).
8. **Summary:** what was generated, how to get started, smoke-test instructions.

## /upgrade-environment pipeline

Audits an existing environment against best practices, interviews the user about
pain points, and implements approved improvements. Unlike `/validate-environment`
(structural correctness), this answers "is this optimal?"

1. The skill inventories the target environment and writes UPGRADE_CONTEXT.md.
2. Read UPGRADE_CONTEXT.md for the inventory and status.
3. Structural pre-check: delegate to environment-validator for a baseline. If
   critical structural failures, offer to fix those first.
4. **User interview** (handle directly, 2-3 rounds):
   - Round 1: "How long have you used this? What works? What frustrates you?"
   - Round 2: context-aware questions based on inventory (detected gaps).
   - Round 3: confirm analysis scope. Append answers to UPGRADE_CONTEXT.md.
5. Delegate to upgrade-analyzer: reads topic files + UpgradeChecklist +
   environment; writes UPGRADE_RECOMMENDATIONS.md.
6. Present recommendations grouped by effort (quick wins / medium / large). User
   selects which to implement.
7. Delegate to component-generator for approved changes. **Shape conversions are
   handled first:**
   - *Convert to hub:* ask for an area slug for the current contents (default:
     directory name); move `<target>/.claude/`, `<target>/CLAUDE.md`, and
     `<target>/Docs/` under `<target>/<area-slug>/` (keep
     `claude-backup-YYYYMMDD/` at the parent); run hub intake for shared basics
     (one round); delegate to environment-architect in hub mode; delegate to
     component-generator for the shell pass only.
   - *Collapse hub to single:* confirm exactly one area remains; move
     `<target>/<only-area>/*` up to `<target>/`; delete HUB_GENESIS.md,
     HUB_ARCHITECTURE.md, and the parent `.claude/` / `CLAUDE.md`; no generator
     pass needed.
   - *Declare hub structure* (HUB_LIKE_UNDECLARED): collect shared-basics intake
     (one round); run the hub architect to design the parent shell from a
     deduplication analysis of existing siblings; delegate to component-generator
     for the shell pass only; leave each existing area in place.
8. Delegate to environment-validator for a post-implementation check.
9. Present summary: changes applied, items deferred, next steps.

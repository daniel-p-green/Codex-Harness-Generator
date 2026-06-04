# Hub Pipeline Integration Tests

Manual walkthrough scenarios for verifying the multi-area hub feature.
Each scenario is end-to-end: start with a given input state, run the
Harness Generator, and verify the specified output. Run after any change to the
intake protocol, architect, component-generator, or validator that
touches hub mode.

These are not automated -- run them by launching `codex` in a scratch
directory and following the steps. Each scenario notes what to verify
after each step so regressions surface immediately rather than at the end.

## Test harness setup

Create a dedicated scratch folder:
```
mkdir ~/ccc-test && cd ~/ccc-test
```

Keep the Harness Generator project path handy (e.g., `C:\ai\Codex-Harness-Generator`).
When running `/create` inside the scratch folder, the Harness Generator uses the
Harness Generator project as its engine and writes the generated environment into
the scratch folder subdirectory.

## Scenario 1: Fresh hub creation (happy path)

**Goal**: create a hub with three work areas from scratch.

**Setup**: empty scratch folder.

**Steps**:
1. Run `/create` with no context.
2. Provide target: `~/ccc-test/governance-hub/`.
3. Experience level: intermediate.
4. Work-area shape: choose *"A set of separate work areas that share some basics"*.
5. Collect shared basics: solo, git, OpenAI API, cost-conscious.
6. Work-area registry: list three areas -- `policy`, `training`, `audit-tool`.
7. Per-area intake round for `policy` (Knowledge Work profile), `training` (Knowledge Work), `audit-tool` (Software Development, Python).
8. Confirm architecture (shared + per-area).
9. Let generation run: 1 shell pass + 3 x 5 area passes = 16 passes total.

**Verify**:
- `governance-hub/Docs/Environment/HUB_GENESIS.md` exists and has `HUB_STATUS: COMPLETE`.
- `governance-hub/Docs/Environment/HUB_ARCHITECTURE.md` exists with a work-area registry matching the three area names.
- `governance-hub/AGENTS.md` exists, is under 80 lines, includes a "Work areas in this setup" section.
- `governance-hub/policy/`, `governance-hub/training/`, `governance-hub/audit-tool/` each contain `.codex/`, `AGENTS.md`, `Docs/Environment/GENESIS.md`, and `Docs/Environment/ARCHITECTURE.md`.
- Parent AGENTS.md + longest per-area AGENTS.md is under 250 lines.
- `governance-hub/Docs/Environment/GENERATION_PROGRESS.md` shows shell + every per-area pass COMPLETE.
- `governance-hub/Docs/Environment/VALIDATION_REPORT.md` verdict is PASS or WARN (no FAIL).

**Common failures to watch for**:
- Generator writes a rule file at both parent and an area without an override declaration (check #48 should FAIL).
- Parent AGENTS.md over 80 lines (check #47 should WARN).
- Work-area registry lists an area that has no subfolder (check #46 should FAIL).

## Scenario 2: Add a new area to an existing hub

**Goal**: add a fourth area to the hub from Scenario 1.

**Setup**: completed Scenario 1.

**Steps**:
1. Run `/create` inside `~/ccc-test/governance-hub/`.
2. Expect: the Harness Generator detects `HUB_GENESIS.md` and prompts *"Add a new work area under `governance-hub`? What's it called?"* -- not shared-basics intake.
3. Name the area: `stakeholder-comms`.
4. Per-area intake (Knowledge Work profile).
5. Confirm and let generation run (5 passes, no shell pass this time).

**Verify**:
- `governance-hub/stakeholder-comms/` is fully populated.
- `HUB_GENESIS.md` work-area registry has been updated to include the new area.
- `HUB_ARCHITECTURE.md` registry has been updated.
- Parent AGENTS.md "Work areas in this setup" section now lists 4 areas.
- Validator passes all hub checks including registry-matches-disk.

**Common failures**:
- the Harness Generator runs full shared-basics intake instead of add-area intake (hub detection broken).
- `HUB_GENESIS.md` not updated to include the new slug.
- Parent AGENTS.md not updated with the new area entry.

## Scenario 3: Convert single environment to hub

**Goal**: take an existing single environment and restructure it as a hub.

**Setup**: generate a plain single environment at `~/ccc-test/single-env/` (run `/create` without hub). Then let the user "accumulate" by adding a second project to the same environment in messy fashion.

**Steps**:
1. Run `/upgrade-environment` on `~/ccc-test/single-env/`.
2. During interview, mention: "I'm actually working on two separate things from this setup -- the original X and a new Y. I wish Codex would keep them apart."
3. Expect analyzer to recommend `[L*] Convert to multi-area hub`.
4. Approve that recommendation.
5. Orchestrator asks for slug for the current contents -- accept `main` or override.
6. Orchestrator runs hub-intake-for-shared-basics (one round only -- autonomy, team, shared tools).
7. Architect runs hub mode, generator runs shell pass only.

**Verify**:
- `single-env/.codex/` and `single-env/AGENTS.md` have MOVED into `single-env/main/` (or whatever slug).
- `single-env/codex-backup-YYYYMMDD/` contains the original structure as safety net.
- New `single-env/AGENTS.md` is the thin parent (under 80 lines).
- `single-env/Docs/Environment/HUB_GENESIS.md` exists.
- `single-env/main/Docs/Environment/GENESIS.md` still exists with original content intact.
- Per-area ARCHITECTURE.md was NOT regenerated (still original).
- Validator passes.

**Common failures**:
- Generator regenerates per-area files (should only run shell pass after conversion).
- Original rule files get duplicated at both parent and area without override declarations.
- Backup not created.

## Scenario 4: Collapse hub to single area

**Goal**: reverse Scenario 3 -- a hub with only one remaining area collapses.

**Setup**: start from Scenario 3 output. Then delete `single-env/main/` content to simulate the last area being archived, OR start from Scenario 1 and delete `training/` and `audit-tool/` to leave only `policy/`.

**Steps** (easier variant: start from Scenario 1, delete two areas manually first):
1. `rm -rf governance-hub/training governance-hub/audit-tool`.
2. Edit `HUB_GENESIS.md` to remove those two from the registry. (This simulates the user cleaning up.)
3. Run `/upgrade-environment` on `governance-hub/`.
4. Expect analyzer to detect `SHAPE: HUB` with exactly one area remaining and recommend `[M*] Collapse hub back to single area`.
5. Approve.

**Verify**:
- `governance-hub/policy/*` contents are moved up to `governance-hub/`.
- `governance-hub/HUB_GENESIS.md` and `HUB_ARCHITECTURE.md` are deleted.
- The thin parent `governance-hub/AGENTS.md` is deleted and replaced by `policy/`'s AGENTS.md.
- `governance-hub/.codex/` (the parent `.codex/`) is gone; `policy/`'s `.codex/` is now at the root.
- Validator passes in single-environment mode.

**Common failures**:
- Contents not moved up (area still lives in subfolder).
- Parent AGENTS.md overwrites the area's AGENTS.md (should replace parent with area's version).
- Validator still thinks it's a hub because `HUB_GENESIS.md` wasn't removed.

## Scenario 5: Declare hub on undeclared sibling environments

**Goal**: the user built a hub-like structure by hand (sibling environments without a parent) -- the Harness Generator detects and helps declare.

**Setup**: create a parent folder with two plain single environments as siblings.

```
~/ccc-test/declared-hub/
  game-shooter/
    .codex/
    AGENTS.md
    Docs/
  game-racing/
    .codex/
    AGENTS.md
    Docs/
```

Each sibling was generated via plain `/create` earlier.

**Steps**:
1. Run `/upgrade-environment` on `~/ccc-test/declared-hub/` (the parent folder, not a sibling).
2. Expect upgrade-environment skill to detect `Shape: HUB_LIKE_UNDECLARED`.
3. Analyzer recommends `[L*] Declare hub structure`.
4. Approve.
5. Collect shared-basics intake (one round).
6. Architect runs hub mode against the existing siblings (reads their AGENTS.md / rules for deduplication analysis).
7. Generator runs shell pass only.

**Verify**:
- `declared-hub/Docs/Environment/HUB_GENESIS.md` exists.
- `declared-hub/AGENTS.md` is the thin parent.
- Rules duplicated across siblings have been deduplicated: a shared version at parent, and the sibling versions have `overrides: <parent-name>` frontmatter where they differ, or are removed where they match.
- Siblings' content not otherwise touched.
- Validator passes.

**Common failures**:
- Siblings' AGENTS.md duplicated the parent without override declaration.
- Shared rules not actually deduplicated.
- Parent's AGENTS.md picks up content that should have stayed per-area.

## Scenario 6: Hub AGENTS.md budget overflow

**Goal**: verify that an attempt to push cumulative AGENTS.md over 250 lines is blocked or warned.

**Setup**: manually edit a per-area AGENTS.md to push it to 180 lines (parent is 80 -> cumulative 260).

**Steps**:
1. Run `/validate-environment` on the hub.

**Verify**:
- Check #47 (cumulative budget) returns FAIL with specifics on which area exceeded.
- Report points the user to trim the parent or the area's rules.

**Common failures**:
- Validator computes parent+child as sum of every area (should be parent + deepest, not sum).
- Validator only checks parent and not cumulative.

## Scenario 7: Cross-area routing discipline

**Goal**: verify that a per-area routing table cannot reference a sibling's internal file paths.

**Setup**: from Scenario 1, manually edit `policy/.codex/rules/00-orchestrator.md` and add a routing entry like:
```
| Check audit tool config | Read ../audit-tool/.agents/skills/foo/SKILL.md | ... |
```

**Steps**:
1. Run `/validate-environment`.

**Verify**:
- Check #49 (cross-area routing discipline) returns FAIL with the specific offending entry quoted.
- Report explains that cross-area handoffs must go through the parent routing table.

## Scenario 8: Resume after interrupted hub generation

**Goal**: verify resume-from-pass works correctly in hub mode.

**Setup**: start Scenario 1 but interrupt (Ctrl+C) after the shell pass and the first area's Pass 2.

**Steps**:
1. Re-run `/create` on `governance-hub/`.
2. Skill reads `GENERATION_PROGRESS.md` and offers to resume.

**Verify**:
- Resume picks up at `policy:3` (next incomplete pass).
- Other areas and the shell pass are not re-run.
- Final output identical to an uninterrupted run.

## Edge case checklist (short)

- Work-area slug with hyphens and multiple words (e.g., `audit-tool-v2`).
- Work-area registry with a single area (valid but unusual -- should suggest collapse in upgrade).
- Adding an area whose slug collides with an existing area (must reject).
- Shared skill with same name as an area-specific skill but no `overrides` frontmatter (must FAIL validation).
- Ship build excludes `HUB_GENESIS.md` and `HUB_ARCHITECTURE.md`? (They're development artifacts, not product. Update `ship-config.json` if needed.)

## What to do if a scenario fails

1. Capture the full transcript of the Harness Generator's output.
2. Note which step failed and the exact error/unexpected behavior.
3. Check `GENERATION_PROGRESS.md` in the test target for what was completed.
4. Check `VALIDATION_REPORT.md` for validator diagnostics.
5. File a note in `Docs/_working/retro/` describing the failure and your hypothesis.
6. Fix the upstream file (intake protocol, architect, generator, or validator) and re-run the scenario from scratch -- do not patch around a bug that will recur.

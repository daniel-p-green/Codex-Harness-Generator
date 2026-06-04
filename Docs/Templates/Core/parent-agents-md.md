# Template: Generated parent AGENTS.md (hub mode)

<!-- TEMPLATE ANNOTATION
  Used ONLY for hub-mode generation. The component-generator's "shell" pass
  writes this file to <target>/AGENTS.md. Per-area AGENTS.md files are
  generated separately under <target>/<area-slug>/AGENTS.md using the
  standard agents-md.md template.

  QUALITY CRITERIA:
  - Strict 80-line cap. The cumulative budget is 250 lines (parent + deepest
    child). Every extra parent line comes out of child budgets.
  - Contents: purpose, work-area registry, shared vocabulary, cross-area
    routing, compaction hint. Nothing else.
  - Do NOT list child file paths -- Codex walks the tree automatically.
  - Do NOT duplicate area-specific constraints (those belong in per-area
    AGENTS.md).
  - ASCII-only.

  WHY THIS STRUCTURE:
  Codex loads both the parent AGENTS.md and the area's AGENTS.md when
  a user works inside an area subfolder. Anything in the parent is paid for
  every turn in every area. Keep it ruthlessly shared.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION BEGINS
  Scenario: AI governance consultant -- three work areas
  Adapt vocabulary and area descriptions per HUB_GENESIS.md
============================================================ -->

# Hub: AI Governance Practice

This repository is a Codex hub -- one shared configuration layer
covering three related but distinct work areas. Codex loads this
file plus the AGENTS.md of whichever work area subfolder you are in.
Other areas are NOT loaded, keeping context focused.

## Work areas in this setup

- **policy/** -- Policy framework drafting, stakeholder review, and
  stakeholder communications.
- **training/** -- Internal training curriculum and employee quizzes.
- **audit-tool/** -- Python CLI that audits client configurations against
  policy. Separate from policy because it has different stakeholders and
  a codebase rather than deliverable documents.

Switch work areas by `cd`-ing into a subfolder and starting a fresh
Codex session there. Do not try to work across two areas in a
single session -- use separate sessions.

## Shared vocabulary

- "Stakeholder" means the client's governance lead (not the engineering team)
- "Control" refers to a specific rule from NIST AI RMF
- "Draft" means an internal working version; "release" means stakeholder-approved

## Cross-area routing

If a user request clearly belongs to another area (e.g., you are in
`policy/` and the user asks for code changes to the audit tool), do not
attempt the work from the current area. Say so plainly and suggest:
"This belongs in the audit-tool area. Open a session under
`audit-tool/` to continue."

If a request legitimately spans areas (e.g., "make sure the audit tool
matches the latest policy"), open separate sessions per area and copy
artifacts between them explicitly. Do not reach across areas from one
session.

## Shared autonomy

All local file operations within this repository are pre-approved for
every area. External actions (publishing, sending emails, network
changes) require explicit approval every time, in every area.

## Compaction preservation

If context pressure rises, preserve: the current work area name, the
active task summary, and any stakeholder-facing artifact names. Discard
transient investigation notes first.

## Per-area instructions

Each area has its own AGENTS.md with domain constraints, routing tables,
and verification commands. Treat this file as the shared frame; the
area's file is the operating manual.

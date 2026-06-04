# Roadmap

This roadmap defines what would make Codex Harness Generator more useful as the
Codex-native equivalent of the earlier harness-generator architecture. It is
intentionally evidence-based: do not claim a milestone is done until the linked
proof exists in this repository.

## Current State

Status: Codex-equivalent beta with checked-in self-dogfood proof.

Already proven:

- Codex-native structure and generated-harness contracts.
- 20 deterministic starter profiles.
- Brief-driven `codex-harness init --brief`.
- Verified first-run `codex-harness quickstart`.
- Metadata-based project inspection for starter profile selection.
- Metadata-inspected `codex-harness init --from-project`.
- Non-destructive `codex-harness adoption-plan` previews for existing projects,
  with optional persistent blueprints and add-only copy scripts.
- Non-editable install smoke for the public CLI.
- Generated harness eval plans with smoke, acceptance, reviewer, and regression
  checks.
- Generated harness improvement logs that convert repeated friction and user
  corrections into evidence-backed harness updates, plus local summaries that
  flag incomplete proposed or applied updates.
- Generated harness task-trial logs and summaries that capture task outcomes,
  verification, privacy review, and limitations after copied-harness use.
- Generated harness local eval reports that run copied-harness smoke checks and
  task-trial and improvement-backlog summaries without depending on this
  generator repo.
- Generated harness onboarding guides with a first useful task loop,
  verification menu, evidence commands, and privacy-safe reporting guidance.
- Checked-in Codex equivalence matrix covering command, artifact, and proof
  surfaces.
- Public-safe evidence packets that summarize copied-harness local eval and
  task-trial evidence before converting it into checked-in usage records.
- External pilot packs that give prospective reporters a one-task checklist,
  public-safe evidence boundary, maintainer commands, and optional issue-body
  draft before external usage conversion.
- Checked-in deterministic, create-acceptance, brief-acceptance, and live-create
  examples.
- Privacy-checked usage-record validation.
- Copied-harness evidence conversion into privacy-checked usage records.
- External usage-report intake and issue-body conversion.
- Beta-exit usage-gap reporting, suggested pilot targets, and a shareable
  campaign packet through `codex-harness usage-gaps` and
  `codex-harness pilot-campaign`.
- Short deterministic demo capture through `codex-harness demo-capture`.

Still unproven:

- Broad external adoption.
- Longitudinal performance across private repos.
- Quality across every future live model-mediated `/create` run.
- Organization-level compliance, policy enforcement, or production security.

## Beta Exit Criteria

The project can stop calling itself a beta only when all of these are true:

- At least 5 non-synthetic usage records are checked in.
- At least 3 records are from external or multi-project usage, not self-dogfood.
- At least 4 different domains are represented across those records.
- At least 2 records used installed brief-based generation:
  `codex-harness quickstart` or `codex-harness init --brief`.
- `python scripts/codex_harness.py proof-status --beta-exit` passes.
- `python scripts/codex_harness.py gate` passes on CI and locally.
- `python scripts/codex_harness.py source-freshness` and
  `python scripts/codex_harness.py semantic-alignment` have current PASS reports
  or documented review notes.

## Near-Term Work

1. Add external usage records.
   Use `.github/ISSUE_TEMPLATE/external-usage-report.yml` and
   `Docs/Environment/EXTERNAL_USAGE_EVIDENCE.md`. Use
   `codex-harness prepare-pilot` to create the next generated pilot harness,
   one-task checklist, and optional issue-body draft in one command. When an
   existing generated harness already has local task trials, use
   `codex-harness pilot-pack` to give the reporter a one-task checklist and
   optional issue-body draft, then use
   `codex-harness usage-from-harness` to draft the privacy-checked record from
   copied-harness evidence. When an external report arrives as a GitHub issue,
   use `codex-harness usage-from-issue` to convert the issue body into the
   checked-in usage record. Run `codex-harness usage-gaps` after each record to
   pick the next pilot profile, source type, and generation path by the largest
   remaining beta-exit gap, then run `codex-harness pilot-campaign` when a
   shareable outreach packet is useful.

2. Add more public-safe live examples.
   Prioritize domains where the generated harness has high-risk boundaries:
   security audit, legal research, financial modeling, hiring pipeline, and
   customer support.

3. Record and maintain the short demo capture.
  Keep `examples/demo-capture/rag-quality` current as the public-safe walkthrough
  for brief-based generation, profile selection, eval, local check, and
  `AGENTS.md` inspection.

4. Deepen source drift checks.
   Move beyond concept presence when official Codex docs expose stable
   machine-readable metadata.

## Issue Intake

- Bugs: use the **Bug report** issue template.
- Feature requests: use the **Feature request** issue template.
- External proof: use the **External usage report** issue template.

All public reports must avoid secrets, personal data, proprietary source,
private repository names, local machine paths, and raw private logs.

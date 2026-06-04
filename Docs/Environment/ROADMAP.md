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
- Metadata-based project inspection for starter profile selection.
- Metadata-inspected `codex-harness init --from-project`.
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
- Checked-in deterministic, create-acceptance, brief-acceptance, and live-create
  examples.
- Privacy-checked usage-record validation.
- Copied-harness evidence conversion into privacy-checked usage records.
- External usage-report intake and issue-body conversion.
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
- At least 2 records used the installed `codex-harness init --brief` path.
- `python scripts/codex_harness.py proof-status --min-usage-records 5` passes.
- `python scripts/codex_harness.py gate` passes on CI and locally.
- `python scripts/codex_harness.py source-freshness` and
  `python scripts/codex_harness.py semantic-alignment` have current PASS reports
  or documented review notes.

## Near-Term Work

1. Add external usage records.
   Use `.github/ISSUE_TEMPLATE/external-usage-report.yml` and
   `Docs/Environment/EXTERNAL_USAGE_EVIDENCE.md`. When a generated harness has
   local task trials, use `codex-harness usage-from-harness` to draft the
   privacy-checked record from copied-harness evidence. When an external report
   arrives as a GitHub issue, use `codex-harness usage-from-issue` to convert the
   issue body into the checked-in usage record.

2. Add more public-safe live examples.
   Prioritize domains where the generated harness has high-risk boundaries:
   security audit, legal research, financial modeling, hiring pipeline, and
   customer support.

3. Record and maintain the short demo capture.
   Keep `examples/demo-capture/rag-quality` current as the public-safe walkthrough
   for `codex-harness init --brief`, profile selection, eval, local check, and
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

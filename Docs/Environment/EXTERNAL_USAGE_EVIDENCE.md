# External Usage Evidence

This repo is still a Codex-equivalent beta because the checked-in proof is
mostly local, synthetic, or self-dogfood evidence. External usage reports are
the path from "useful in this repo" toward "useful across projects."

## What To Submit

Open an **External usage report** issue when you have used a generated Codex
harness on a real or public-safe task.

Good reports include:

- The domain or project type.
- The generated harness profile or public-safe label, if known.
- The source type: `external`, `multi-project`, or `self-dogfood`.
- The generation path, such as `installed-quickstart`, `installed-init-brief`,
  `installed-init-from-project`, `adoption-plan`, `manual-migration`,
  `live-create`, `repo-dogfood`, or `unknown`.
- A public-safe task summary.
- At least two evidence bullets.
- At least two verification bullets.
- A privacy review.
- At least one limitation.

## What Not To Submit

Do not include:

- Secrets, tokens, API keys, passwords, private keys, or credentials.
- Customer data, candidate data, health data, payment data, or personal data.
- Proprietary source code, private repository names, or raw private logs.
- Local machine paths such as `/Users/name/...`.
- Email addresses or direct contact details.
- Raw transcripts from private meetings or support tickets.

Use `private-summary` when the raw evidence cannot be public. A summary can
still be useful if it explains the task, outcome, verification, privacy review,
and limits.

## Maintainer Conversion

Before asking someone outside this repo to report a trial, prepare a pilot
harness and evidence kit. This creates the generated harness, runs quickstart
validation, and writes a one-task pilot pack plus issue-body draft:

```bash
python scripts/codex_harness.py prepare-pilot /tmp/codex-llm-app-pilot \
  --brief "LLM-powered app, RAG, agent, prompt, and eval workflow development with one privacy-safe task" \
  --domain "LLM app" \
  --slug external-example \
  --title "External example" \
  --source-type external \
  --generation-path installed-quickstart \
  --force \
  --json
```

When a copied generated harness already exists, create a pilot pack from that
harness. The pack gives the reporter a one-task loop, safe evidence boundaries,
maintainer commands, and an optional issue-body draft:

```bash
python scripts/codex_harness.py pilot-pack /path/to/generated-harness \
  --domain "LLM app" \
  --slug external-example \
  --title "External example" \
  --harness-label "private-summary: external reporter" \
  --source-type external \
  --generation-path installed-quickstart \
  --prefill-from-trials \
  --issue-out /tmp/EXTERNAL_USAGE_ISSUE_DRAFT.md
```

Use `--prefill-from-trials` after the copied harness has at least one complete
task-trial entry. It fills the issue draft from the latest trial and local eval
status, but the reporter or maintainer must still review and redact it before
sharing.

When the reporter can share a copied generated harness directory privately, ask
them to record task trials and export a public-safe packet first:

```bash
python scripts/codex_harness.py local-eval /path/to/generated-harness
python scripts/codex_harness.py evidence-packet /path/to/generated-harness \
  --harness-label "public-safe harness label" \
  --out /tmp/HARNESS_EVIDENCE_PACKET.md
```

Review the packet for concrete evidence, verification, privacy boundaries, and
limitations before turning it into a checked-in usage record.

Maintainers can convert a usable public issue into a checked-in usage record by
saving the issue body to a local Markdown file. Preview and privacy-check the
normalized record before writing files:

```bash
python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md \
  --slug external-example \
  --title "External example" \
  --no-write \
  --json
```

If the preview is complete and public-safe, rerun without `--no-write` to write
the usage-record JSON file and update `Docs/Environment/USAGE_RECORDS.md`.
When the issue corresponds to a prepared pilot with the same slug, add the
pilot-board directory so the importer also marks that pilot `converted`,
validates the usage-record reference, and refreshes the pilot board:

```bash
python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md \
  --slug external-example \
  --title "External example" \
  --pilot-record-dir Docs/Environment/pilot-records \
  --pilot-board-report Docs/Environment/PILOT_BOARD.md \
  --json
```

The importer reads the GitHub issue-form headings and applies the same
required-field and sensitive-text checks as `usage-record` in both preview and
write modes.

For manual conversion or cleanup, use:

```bash
python scripts/codex_harness.py usage-record \
  --slug external-example \
  --title "External example" \
  --domain "LLM app" \
  --harness-path "private-summary: external reporter" \
  --task-summary "Public-safe summary from issue." \
  --outcome success \
  --evidence-type private-summary \
  --source-type external \
  --generation-path installed-quickstart \
  --evidence "Evidence bullet from issue." \
  --evidence "Second evidence bullet from issue." \
  --verification "Verification bullet from issue." \
  --verification "Second verification bullet from issue." \
  --privacy-review "Reporter confirmed no secrets, personal data, proprietary source, private paths, or raw logs were included." \
  --limitation "External report covers one task and one generated harness."
```

Then verify:

```bash
python scripts/codex_harness.py equivalence
python scripts/codex_harness.py usage-gaps
python scripts/codex_harness.py proof-next
python scripts/codex_harness.py pilot-campaign
python scripts/codex_harness.py usage-validate \
  --min-records 3 \
  --require-non-synthetic \
  --require-success \
  --min-external-or-multi-project 1
python scripts/codex_harness.py proof-status \
  --min-usage-records 3 \
  --min-external-or-multi-project 1
```

To test the full beta-exit usage threshold, use:

```bash
python scripts/codex_harness.py usage-validate \
  --min-records 5 \
  --require-non-synthetic \
  --require-success \
  --min-external-or-multi-project 3 \
  --min-domains 4 \
  --min-installed-init-brief 2
```

The threshold flag name is kept for older scripts; it counts installed
brief-based generation through either `codex-harness quickstart` or
`codex-harness init --brief`.

## Claim Discipline

One external report is evidence, not a guarantee. Do not claim broad adoption,
production readiness, compliance, or long-term reliability until the checked-in
record set supports that scope.

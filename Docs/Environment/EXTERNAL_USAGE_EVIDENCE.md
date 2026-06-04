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

Maintainers can convert a usable public issue into a checked-in usage record by
saving the issue body to a local Markdown file and running:

```bash
python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md \
  --slug external-example \
  --title "External example" \
  --json
```

The importer reads the GitHub issue-form headings, writes a usage-record JSON
file, updates `Docs/Environment/USAGE_RECORDS.md`, and applies the same
required-field and sensitive-text checks as `usage-record`.

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
  --evidence "Evidence bullet from issue." \
  --evidence "Second evidence bullet from issue." \
  --verification "Verification bullet from issue." \
  --verification "Second verification bullet from issue." \
  --privacy-review "Reporter confirmed no secrets, personal data, proprietary source, private paths, or raw logs were included." \
  --limitation "External report covers one task and one generated harness."
```

Then verify:

```bash
python scripts/codex_harness.py usage-validate \
  --min-records 3 \
  --require-non-synthetic \
  --require-success
python scripts/codex_harness.py proof-status --min-usage-records 3
```

## Claim Discipline

One external report is evidence, not a guarantee. Do not claim broad adoption,
production readiness, compliance, or long-term reliability until the checked-in
record set supports that scope.

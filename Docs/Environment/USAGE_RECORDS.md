# Usage Records

This report indexes sanitized generated-harness usage evidence recorded by
`python scripts/record_usage_case.py`. It is intentionally conservative:
records may summarize private work, but public artifacts must not include
secrets, personal data, proprietary source, or local machine paths.

## Summary

| Total | Non-Synthetic | Success | External/Multi-Project | Distinct Domains | Installed Brief Generation |
|---:|---:|---:|---:|---:|---:|
| 2 | 2 | 2 | 0 | 1 | 0 |

Product-proof status: non-synthetic usage evidence present

## Records

| Generated | Slug | Domain | Source | Generation Path | Outcome | Evidence Type | Verification Count |
|---|---|---|---|---|---|---|---:|
| 2026-06-04T07:00:16Z | `dogfood-brief-fast-path` | Codex harness generation | self-dogfood | repo-dogfood | success | sanitized | 2 |
| 2026-06-04T06:12:20Z | `dogfood-high-risk-proof-suite` | Codex harness generation | self-dogfood | repo-dogfood | success | sanitized | 2 |

## Scope

- `synthetic`: public-safe generated or fake inputs.
- `sanitized`: real workflow evidence stripped of secrets, personal data,
  proprietary source, and local machine paths.
- `private-summary`: public-safe summary of private work where raw evidence
  cannot be published.
- `source_type`: whether the record is repo self-dogfood, external usage,
  or multi-project usage.
- `generation_path`: how the harness entered the workflow.
- A record is evidence of one harness use, not proof that every generated
  harness will perform well.

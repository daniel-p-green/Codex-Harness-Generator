---
name: write-cleanup-summary
description: Use when the user wants a concise cleanup report, public-safe demo summary, wording pass, or verification that generated TODO summaries are grounded and privacy-safe.
---

# Write Cleanup Summary

Use this skill when shaping scan results into report text.

## Workflow

1. Read the scan result or generated summary file.
2. Confirm every claim is grounded in an observed TODO item or count.
3. Group output into stale, current, and needs-review items when those buckets exist.
4. Keep wording short and practical.
5. Redact secrets, credentials, tokens, private URLs, and absolute local paths.

## Output Standard

The final summary should be useful in public examples, easy to scan, and honest about limits or ambiguous items.

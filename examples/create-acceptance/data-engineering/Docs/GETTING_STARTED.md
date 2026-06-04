# Getting Started

Open Codex in this project and ask for a small verified task. This
harness expects the assistant to inspect files before editing, avoid secrets, and
verify work with the narrowest meaningful check.

## First Checks

1. Run `/health-check` to verify the harness structure.
2. Ask Codex to map datasets, schemas, and pipeline entry points.
3. Ask for a small data-contract or validation check.
4. Ask the reviewer to inspect data quality and backfill risk.

The permission profile allows workspace edits while denying secrets, tokens,
credentials, private keys, and `.env` files.

Generated: 2026-06-04

# Live Create Capture

Status: PASS.
Captured: 2026-06-04T03:49:26Z

## Scenario

- Capture name: synthetic-python-cli
- Flow: live model-mediated `/create` capture
- Source target: temporary synthetic target
- Project brief: Synthetic Python CLI utility that scans local Markdown files, reports stale TODO items, and writes a concise cleanup summary. Public-safe fake data only.

## Codex Run

- Mode: codex exec
- Codex exit code: 0
- Codex stdout sha256: `bda3247fc808c4365a941eff1e14bcbe74123d35bfa2cd44f2a6984d81d23d5d`
- Codex stderr sha256: `2cd9844d5276bb683832b332eaa50ae7ea662086624cb6e98ce19846b167f17e`

## Verification

- Generated harness eval: PASS score=100 failures=0 warnings=0
- Offline smoke: PASS

## Sanitization

- Excluded local caches, virtual environments, dependency folders, transient
  `_working` state, logs, SQLite files, private key material, and `.env*` files.
- Do not add live credentials, customer data, proprietary source, or local
  machine-specific paths to checked-in live-create captures.

## Scope

This proves one inspectable `/create` output can pass the generated-harness
contract. It does not prove that every future live `/create` run will be ideal.

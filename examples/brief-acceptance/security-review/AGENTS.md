# Security Review Harness Codex Harness

This Codex harness supports defensive security audit, vulnerability review, threat model, and remediation work. Verify live file state before
editing, run the narrowest meaningful check, and report any skipped verification.

## Defaults

- Prefer simple, maintainable code with clear names.
- Do not read secrets, tokens, private keys, credential files, or `.env` files.
- Treat security and privacy issues as high priority.
- Ask for clarification when correctness, data loss, or privacy depends on
  missing context.
- Run tests when they exist; otherwise use source checks, dry runs, or the
  narrowest runnable command.
- Use the reviewer for non-trivial changes before calling work done.

## Verification

- Verify findings against files, dependencies, configs, or command output.
- Ask for authorization before active testing, exploit reproduction, scanners, or destructive work.
- Prioritize secret, token, credential, private key, privacy, and permission risks.

## Domain Guidance

- Treat secrets, tokens, credentials, private keys, and authorization boundaries as first-class concerns.
- Do not run exploit code, penetration test actions, active testing, scanners, or destructive work without explicit approval.
- Keep security audit outputs defensive: cite evidence, affected paths, severity, safe remediation, and verification limits.

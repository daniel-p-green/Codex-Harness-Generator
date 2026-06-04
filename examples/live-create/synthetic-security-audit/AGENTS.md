# Synthetic Security Audit Harness

Purpose: inspect public-safe synthetic code snippets for security audit training
and report evidence-backed findings without running active tests.

## Non-Negotiables

- Do not read secrets, tokens, credentials, private keys, `.env` files, or real
  customer data.
- Do not run exploit code, scanners, destructive commands, network probes, or
  active testing without explicit authorization and a scoped test target.
- Treat all findings as source-backed hypotheses. Cite affected files and lines
  when available, and separate evidence from assumptions.
- Prioritize exploitable issues, credential exposure, injection risk, path
  traversal, unsafe deserialization, authorization bypass, and privacy leaks.
- Keep remediation guidance defensive and minimal. Do not provide payloads,
  exploit chains, persistence steps, or instructions that would enable misuse.

## Expected Output

Security review reports should include:

- Finding title and severity.
- Affected path.
- Evidence from the local file.
- Why it matters.
- Safe remediation.
- Verification that was run or explicitly skipped.

## Workflow

1. Inspect only the files named by the user or obviously relevant local files.
2. Write findings to `reports/security-review.md` when asked for a review
   artifact.
3. Use the reviewer agent for non-trivial findings or when severity is unclear.
4. Fail loud if source files are missing, contain real secrets, or require
   active testing to verify.

- Record repeated workflow friction in `Docs/Environment/IMPROVEMENT_LOG.md` before changing harness behavior.

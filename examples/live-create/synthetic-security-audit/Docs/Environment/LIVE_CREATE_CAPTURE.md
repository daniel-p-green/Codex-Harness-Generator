# High-Risk Example Capture

Status: PASS.

## Scope

This public-safe high-risk example is a curated task-trial fixture. It is
included beside live-create examples so the same eval, smoke, and live task
trial runners can exercise security-audit behavior without publishing real
security work or secrets.

## Verification

- Generated harness eval: PASS.
- Offline smoke: PASS.
- High-risk domain guardrail checks: PASS.
- Representative live task trial:
  `security-review-synthetic-code`.

## Limits

- Not evidence of real-world production security review usage.
- Not a penetration-testing harness.
- Does not authorize active testing, scanning, exploit execution, or destructive
  commands.

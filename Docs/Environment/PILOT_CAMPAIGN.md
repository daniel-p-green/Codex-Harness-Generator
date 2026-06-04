# External Pilot Campaign

Generated: 2026-06-04T11:18:24Z
Status: PASS
Readiness: missing-beta-exit-evidence

This campaign packet turns the current beta-exit evidence gaps into
concrete external or multi-project pilot asks. It is an evidence
collection plan, not adoption proof.

## Current Evidence Gap

- Valid usage records: 2
- External or multi-project records: 0
- Distinct domains: 1
- Installed `init --brief` records: 0

## Remaining Targets

- Usage records to add: 3
- External or multi-project records to add: 3
- Distinct domains to add: 3
- Installed `init --brief` records to add: 2

## Pilot Slots

### 1. LLM app (`llm-app`)

- Source type: `external`
- Generation path: `installed-init-brief`
- Pilot ask: try one privacy-safe task, run local eval, then submit a public-safe issue-body report.

```bash
codex-harness init /tmp/codex-llm-app-pilot --brief "LLM-powered app, RAG, agent, prompt, and eval workflow development with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "LLM App Workspace Pilot" --force
codex-harness pilot-pack /tmp/codex-llm-app-pilot --slug llm-app-pilot --title "LLM app pilot" --domain "LLM app" --source-type external --generation-path installed-init-brief --prefill-from-trials
```

Reporter evidence checklist:

- One concrete task summary.
- At least two evidence bullets.
- At least two verification bullets.
- A privacy review confirming no secrets, personal data, private paths, proprietary source, or raw private logs.
- One limitation that keeps the claim scoped to this pilot.

### 2. security audit (`security-audit`)

- Source type: `external`
- Generation path: `installed-init-brief`
- Pilot ask: try one privacy-safe task, run local eval, then submit a public-safe issue-body report.

```bash
codex-harness init /tmp/codex-security-audit-pilot --brief "defensive security audit, vulnerability review, threat model, and remediation work with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "Security Audit Workspace Pilot" --force
codex-harness pilot-pack /tmp/codex-security-audit-pilot --slug security-audit-pilot --title "security audit pilot" --domain "security audit" --source-type external --generation-path installed-init-brief --prefill-from-trials
```

Reporter evidence checklist:

- One concrete task summary.
- At least two evidence bullets.
- At least two verification bullets.
- A privacy review confirming no secrets, personal data, private paths, proprietary source, or raw private logs.
- One limitation that keeps the claim scoped to this pilot.

### 3. customer support (`customer-support`)

- Source type: `external`
- Generation path: `installed-init-from-project`
- Pilot ask: try one privacy-safe task, run local eval, then submit a public-safe issue-body report.

```bash
codex-harness init /tmp/codex-customer-support-pilot --brief "customer-support documentation, FAQ, response, escalation, and support-ops work with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "Customer Support Workspace Pilot" --force
codex-harness pilot-pack /tmp/codex-customer-support-pilot --slug customer-support-pilot --title "customer support pilot" --domain "customer support" --source-type external --generation-path installed-init-from-project --prefill-from-trials
```

Reporter evidence checklist:

- One concrete task summary.
- At least two evidence bullets.
- At least two verification bullets.
- A privacy review confirming no secrets, personal data, private paths, proprietary source, or raw private logs.
- One limitation that keeps the claim scoped to this pilot.

## Maintainer Follow-Up

After each pilot:

1. Review the pilot pack and issue draft for privacy-sensitive text.
2. Convert acceptable evidence with `codex-harness usage-from-harness` or `codex-harness usage-from-issue`.
3. Re-run `codex-harness usage-gaps` and refresh this campaign only if gaps remain.
4. Do not drop the beta label until `codex-harness proof-status` passes with the beta-exit thresholds.

## Claim Boundary

These pilots can support narrow usage evidence. They do not prove broad external adoption, longitudinal private-repo performance, production security, compliance, or every future live `/create` run.

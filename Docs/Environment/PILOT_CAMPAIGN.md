# External Pilot Campaign

Generated: 2026-06-04T16:58:27Z
Status: PASS
Readiness: missing-beta-exit-evidence

This campaign packet turns the current beta-exit evidence gaps into
concrete external or multi-project pilot asks. It is an evidence
collection plan, not adoption proof.
Use `codex-harness prepare-next-pilot <target> --pilot-record-dir Docs/Environment/pilot-records`
to prepare the first suggested pilot directly from the current gaps and
track it with `codex-harness pilot-board`.

## Current Evidence Gap

- Valid usage records: 2
- External or multi-project records: 0
- Distinct domains: 1
- Installed brief-based generation records: 0

## Remaining Targets

- Usage records to add: 3
- External or multi-project records to add: 3
- Distinct domains to add: 3
- Installed brief-based generation records to add: 2

## Listed Pilot Coverage Projection

Projection assumes every suggested pilot is completed and converted into valid non-synthetic evidence; it is not usage proof.

- Listed pilots in projection: 3
- Would satisfy beta-exit usage thresholds: true
- Projected usage records: 5
- Projected external or multi-project records: 3
- Projected distinct domains: 4
- Projected installed brief-based generation records: 3

Projected remaining gaps after listed pilots:

- Usage records: 0
- External or multi-project records: 0
- Distinct domains: 0
- Installed brief-based generation records: 0

## Pilot Slots

### 1. LLM app (`llm-app`)

- Source type: `external`
- Generation path: `installed-quickstart`
- Pilot ask: try one privacy-safe task, run local eval, then submit a public-safe issue-body report.

```bash
codex-harness prepare-pilot /tmp/codex-llm-app-pilot --brief "LLM-powered app, RAG, agent, prompt, and eval workflow development with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "LLM App Workspace Pilot" --domain "LLM app" --slug llm-app-pilot --title "LLM app pilot" --source-type external --generation-path installed-quickstart --pilot-record-dir Docs/Environment/pilot-records --force
```

Reporter evidence checklist:

- One concrete task summary.
- At least two evidence bullets.
- At least two verification bullets.
- A privacy review confirming no secrets, personal data, private paths, proprietary source, or raw private logs.
- One limitation that keeps the claim scoped to this pilot.

### 2. security audit (`security-audit`)

- Source type: `external`
- Generation path: `installed-quickstart`
- Pilot ask: try one privacy-safe task, run local eval, then submit a public-safe issue-body report.

```bash
codex-harness prepare-pilot /tmp/codex-security-audit-pilot --brief "defensive security audit, vulnerability review, threat model, and remediation work with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "Security Audit Workspace Pilot" --domain "security audit" --slug security-audit-pilot --title "security audit pilot" --source-type external --generation-path installed-quickstart --pilot-record-dir Docs/Environment/pilot-records --force
```

Reporter evidence checklist:

- One concrete task summary.
- At least two evidence bullets.
- At least two verification bullets.
- A privacy review confirming no secrets, personal data, private paths, proprietary source, or raw private logs.
- One limitation that keeps the claim scoped to this pilot.

### 3. customer support (`customer-support`)

- Source type: `external`
- Generation path: `installed-quickstart`
- Pilot ask: try one privacy-safe task, run local eval, then submit a public-safe issue-body report.

```bash
codex-harness prepare-pilot /tmp/codex-customer-support-pilot --brief "customer-support documentation, FAQ, response, escalation, and support-ops work with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "Customer Support Workspace Pilot" --domain "customer support" --slug customer-support-pilot --title "customer support pilot" --source-type external --generation-path installed-quickstart --pilot-record-dir Docs/Environment/pilot-records --force
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
3. Update status with `codex-harness pilot-update`, then review `codex-harness pilot-board` so completed pilots do not stay stuck as outreach.
4. Re-run `codex-harness usage-gaps` and refresh this campaign only if gaps remain.
5. Do not drop the beta label until `codex-harness proof-status` passes with the beta-exit thresholds.

## Claim Boundary

These pilots can support narrow usage evidence. They do not prove broad external adoption, longitudinal private-repo performance, production security, compliance, or every future live `/create` run.

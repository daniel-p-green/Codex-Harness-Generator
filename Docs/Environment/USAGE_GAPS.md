# Usage Evidence Gaps

Generated: 2026-06-04T13:23:30Z
Status: PASS
Readiness: missing-beta-exit-evidence

This report shows what usage evidence is still missing before the repo can
honestly stop calling itself a beta.

## Targets

- Total usage records: 5
- External or multi-project records: 3
- Distinct domains: 4
- Installed brief-based generation records: 2

## Current Summary

- Total usage records: 2
- Non-synthetic records: 2
- Successful records: 2
- External or multi-project records: 0
- Distinct domains: 1
- Installed brief-based generation records: 0

## Remaining Gaps

- Usage records: 3
- External or multi-project records: 3
- Distinct domains: 3
- Installed brief-based generation records: 2

## Represented Domains

- Codex harness generation

## Suggested Pilot Targets

### 1. LLM app (`llm-app`)

- Source type: `external`
- Generation path: `installed-quickstart`
- Brief: LLM-powered app, RAG, agent, prompt, and eval workflow development with one privacy-safe task, local eval, and public-safe usage evidence

```bash
codex-harness prepare-pilot /tmp/codex-llm-app-pilot --brief "LLM-powered app, RAG, agent, prompt, and eval workflow development with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "LLM App Workspace Pilot" --domain "LLM app" --slug llm-app-pilot --title "LLM app pilot" --source-type external --generation-path installed-quickstart --force
```

### 2. security audit (`security-audit`)

- Source type: `external`
- Generation path: `installed-quickstart`
- Brief: defensive security audit, vulnerability review, threat model, and remediation work with one privacy-safe task, local eval, and public-safe usage evidence

```bash
codex-harness prepare-pilot /tmp/codex-security-audit-pilot --brief "defensive security audit, vulnerability review, threat model, and remediation work with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "Security Audit Workspace Pilot" --domain "security audit" --slug security-audit-pilot --title "security audit pilot" --source-type external --generation-path installed-quickstart --force
```

### 3. customer support (`customer-support`)

- Source type: `external`
- Generation path: `installed-quickstart`
- Brief: customer-support documentation, FAQ, response, escalation, and support-ops work with one privacy-safe task, local eval, and public-safe usage evidence

```bash
codex-harness prepare-pilot /tmp/codex-customer-support-pilot --brief "customer-support documentation, FAQ, response, escalation, and support-ops work with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "Customer Support Workspace Pilot" --domain "customer support" --slug customer-support-pilot --title "customer support pilot" --source-type external --generation-path installed-quickstart --force
```


## Recommended Next Moves

- Collect 3 more external or multi-project usage record(s).
- Make at least 2 of the next record(s) use installed brief-based generation (`codex-harness prepare-next-pilot`, `codex-harness prepare-pilot`, `codex-harness quickstart`, or `codex-harness init --brief`).
- Cover 3 more distinct usage domain(s) instead of adding more same-domain proof.
- Add 3 more valid non-synthetic usage record(s).
- For the next suggested pilot, run `codex-harness prepare-next-pilot <target> --pilot-record-dir Docs/Environment/pilot-records` or copy the `codex-harness prepare-pilot <target>` command, review the generated pack, track it with `codex-harness pilot-board`, update status with `codex-harness pilot-update`, then convert completed evidence with `usage-from-harness` or `usage-from-issue`.

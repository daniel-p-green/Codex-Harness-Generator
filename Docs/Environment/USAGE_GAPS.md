# Usage Evidence Gaps

Generated: 2026-06-04T11:13:04Z
Status: PASS
Readiness: missing-beta-exit-evidence

This report shows what usage evidence is still missing before the repo can
honestly stop calling itself a beta.

## Targets

- Total usage records: 5
- External or multi-project records: 3
- Distinct domains: 4
- Installed `codex-harness init --brief` records: 2

## Current Summary

- Total usage records: 2
- Non-synthetic records: 2
- Successful records: 2
- External or multi-project records: 0
- Distinct domains: 1
- Installed `init --brief` records: 0

## Remaining Gaps

- Usage records: 3
- External or multi-project records: 3
- Distinct domains: 3
- Installed `init --brief` records: 2

## Represented Domains

- Codex harness generation

## Suggested Pilot Targets

### 1. LLM app (`llm-app`)

- Source type: `external`
- Generation path: `installed-init-brief`
- Brief: LLM-powered app, RAG, agent, prompt, and eval workflow development with one privacy-safe task, local eval, and public-safe usage evidence

```bash
codex-harness init /tmp/codex-llm-app-pilot --brief "LLM-powered app, RAG, agent, prompt, and eval workflow development with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "LLM App Workspace Pilot" --force
codex-harness pilot-pack /tmp/codex-llm-app-pilot --slug llm-app-pilot --title "LLM app pilot" --domain "LLM app" --source-type external --generation-path installed-init-brief --prefill-from-trials
```

### 2. security audit (`security-audit`)

- Source type: `external`
- Generation path: `installed-init-brief`
- Brief: defensive security audit, vulnerability review, threat model, and remediation work with one privacy-safe task, local eval, and public-safe usage evidence

```bash
codex-harness init /tmp/codex-security-audit-pilot --brief "defensive security audit, vulnerability review, threat model, and remediation work with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "Security Audit Workspace Pilot" --force
codex-harness pilot-pack /tmp/codex-security-audit-pilot --slug security-audit-pilot --title "security audit pilot" --domain "security audit" --source-type external --generation-path installed-init-brief --prefill-from-trials
```

### 3. customer support (`customer-support`)

- Source type: `external`
- Generation path: `installed-init-from-project`
- Brief: customer-support documentation, FAQ, response, escalation, and support-ops work with one privacy-safe task, local eval, and public-safe usage evidence

```bash
codex-harness init /tmp/codex-customer-support-pilot --brief "customer-support documentation, FAQ, response, escalation, and support-ops work with one privacy-safe task, local eval, and public-safe usage evidence" --project-name "Customer Support Workspace Pilot" --force
codex-harness pilot-pack /tmp/codex-customer-support-pilot --slug customer-support-pilot --title "customer support pilot" --domain "customer support" --source-type external --generation-path installed-init-from-project --prefill-from-trials
```


## Recommended Next Moves

- Collect 3 more external or multi-project usage record(s).
- Make at least 2 of the next record(s) use the installed `codex-harness init --brief` path.
- Cover 3 more distinct usage domain(s) instead of adding more same-domain proof.
- Add 3 more valid non-synthetic usage record(s).
- For each pilot, run `codex-harness pilot-pack <generated-harness> --prefill-from-trials`, review the draft, then convert it with `usage-from-harness` or `usage-from-issue`.

# Starter Profile: DevOps & Infrastructure

Follows `Docs/StarterProfiles/PROFILE_FORMAT.md` (slim). A starting point the
architect adapts -- it points at templates, it does not inline them.

## Profile Metadata

- **Target audience**: DevOps engineers, SRE/platform teams, cloud infra teams
  (IaC, CI/CD, container orchestration, monitoring, incident response)
- **Tools**: Terraform/OpenTofu/Pulumi/CloudFormation, Kubernetes, Docker,
  Ansible; AWS/GCP/Azure CLIs (pick per intake)
- **Complexity**: Extended | **Memory tier**: Standard | **Action default**:
  proactive for read-only, gated for mutations (plan-before-apply) | **VCS**: Git

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| researcher | opus | Cloud services, IaC patterns, provider/version caveats, security benchmarks | researcher.md |
| planner | opus | Plan infra changes with blast-radius analysis + rollback strategy, checkpointed | planner.md |
| implementer | sonnet | Implement one checkpoint of IaC; validate/fmt/dry-run | implementer.md |
| reviewer | opus | Review for security misconfig, cost, blast radius (read-only) | reviewer.md |
| incident-responder | opus | Triage, gather signals, hypothesize, rollback or fix outages | debugger.md (adapt for ops triage) |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy, context-management, self-learning, error-handling (with diagnostic
discipline), memory-management, `vcs-git.md`, and a domain
`infrastructure-safety` rule (plan-before-apply mutation gate + change log;
see Special Patterns below).

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/deploy` (plan/dry-run ->
pause -> apply on approval; per-tool rollback) and `/incident` (incident record,
triage guidance, post-incident runbook update). No `deploy.md`/`incident.md`
template exists -- generate from the `build.md` shape plus the safety pattern.

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | New IaC module / resource (clear scope) | planner -> implementer -> reviewer -> /deploy | One checkpoint at a time; plan review gate before apply | researcher (unfamiliar provider/resource) |
| 2 | New IaC module (vague / broad) | clarify -> planner -> implementer -> reviewer | Gather: provider, region, compliance, cost constraints | researcher (architecture guidance) |
| 3 | Terraform plan shows unexpected changes / drift | incident-responder (diagnose drift) -> implementer (reconcile) | Include plan output, expected vs actual state | reviewer (verify reconciliation safe) |
| 4 | CI/CD pipeline failure | incident-responder (logs, failing stage) | Include pipeline URL/logs + recent commits | researcher (unfamiliar build tool/provider error) |
| 5 | Deployment failed / rollback needed | incident-responder (blast radius, execute rollback) | Include deployment logs + affected environment | planner (if rollback strategy must be created) |
| 6 | Service is down / alerts firing | incident-responder (triage, signals, investigate) | Include alert details, affected services, timeline | researcher (unfamiliar failure mode) |
| 7 | Kubernetes pod crash / restart loop | incident-responder (events, logs, resources, probes) | Include pod, namespace, kubectl describe output | researcher (unfamiliar K8s resource type) |
| 8 | Security misconfiguration / vulnerability | reviewer (audit) -> implementer (fix) | Specify resource, exposure, compliance framework | researcher (CIS benchmarks, best practices) |
| 9 | Cost optimization / right-sizing | researcher (pricing, reserved/savings) -> planner -> implementer | Include current spend / cost-explorer output | reviewer (verify no perf regression) |
| 10 | Capacity planning / scaling | researcher (limits, scaling patterns) -> planner -> implementer | Specify expected load, growth, SLO targets | reviewer (verify autoscaling config) |
| 11 | Monitoring / alerting setup | planner -> implementer -> reviewer | Specify metrics, thresholds, channels, SLOs | researcher (unfamiliar monitoring tool) |
| 12 | Secret / credential rotation | planner (zero-downtime rotation) -> implementer -> reviewer | Identify all consumers before rotating | incident-responder (if rotation causes outage) |
| 13 | Infra migration (cloud/region/account) | researcher (target) -> planner (phased) -> implementer | Phases: prepare, migrate, verify, cutover, cleanup | reviewer (verify each phase) |
| 14 | Refactor IaC modules / restructure | planner -> implementer -> reviewer | Plan state moves; verify no resource recreation | researcher (module pattern updates) |
| 15 | "Where is X" / find resource handling Y | answer directly (search HCL/YAML) | Search by resource type, name, tag, output | researcher (resource in another repo/account) |
| 16 | "How does X work" / cloud service question | researcher | Provider docs + existing research first | answer directly (well-documented feature) |
| 17 | Review my changes / PR review | reviewer (infra rubric) | Read git diff: security, cost, blast radius | answer directly (single file) |
| 18 | Update runbook / documentation | answer directly (draft/update runbook) | Follow format in Docs/Areas/runbooks/ | researcher (procedure needs verification) |
| 19 | DNS / certificate / domain issue | incident-responder (propagation, expiry, config) | Include domain, expected vs actual, cert details | researcher (unfamiliar DNS provider API) |
| 20 | Networking issue (VPC, peering, firewall) | incident-responder (trace routes/rules) -> implementer | Include source/dest, ports, error messages | researcher (unfamiliar networking model) |

Complexity scaling: Simple (1 agent: status checks, doc lookups, small config) |
Standard (2-3 agents: single-resource changes, pipeline fixes, alert setup) |
Complex (4-5 agents serial: multi-resource deploys, migrations, incident-with-remediation).

## Ecosystem Permissions

Base + Universal Deny + Git + **Infrastructure** (Terraform/K8s/cloud-CLI read +
mutation gates) + Docker -- all in
`Docs/Templates/References/ecosystem-permissions.md`. The infrastructure safety
gates there are load-bearing: `terraform apply/destroy`, `kubectl apply/delete`,
`helm install/upgrade`, and any cloud `* delete *`/`* terminate *` stay in deny;
the `/deploy` skill performs them only after the approval gate. Add IaC file
writes (`Edit/Write(./**/*.tf)`, `.tfvars`, `.yaml/.yml`, `.j2`, `Dockerfile*`)
the implementer touches. Add per-tool CLI from intake (`cdk *` / `pulumi *` with
their `destroy` denied). Generate `settings.local.json` for machine-specific tool
paths and credential references; `.gitignore` it. `.claudeignore`: `*.tfstate*`,
`.terraform/`, `*.pem`, `*.key`, `*credentials*`, `*secret*`, cloud caches.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Terraform plan not reviewed before apply -- agent runs
  terraform apply directly without showing plan output. Mitigation: /deploy skill
  enforces plan-then-approve gate; PreToolUse hook blocks raw apply.
- [PATTERN] (pre-seeded) State file conflicts in shared environments -- concurrent
  work on the same state causes lock contention/corruption. Mitigation: detect
  lock errors, suggest locking backend (S3+DynamoDB, GCS, Azure Blob), never
  force-unlock without approval.
- [PATTERN] (pre-seeded) Credential exposure in IaC files -- implementer hardcodes
  keys/passwords/tokens in tfvars, manifests, or CI configs. Mitigation: reviewer
  checks for hardcoded creds; .claudeignore excludes sensitive patterns; deny
  rules block reading credential files.
- [PATTERN] (pre-seeded) Blast radius underestimated -- plan shows "1 to change"
  but triggers a replacement (destroy+create) causing downtime. Mitigation:
  planner calls out force-new attributes; reviewer flags replacement markers (~).
- [PATTERN] (pre-seeded) Runbook not updated after incident -- fix applied but the
  failure-mode runbook not created/updated. Mitigation: /incident prompts for a
  runbook update at every resolution.
```

## Hook Suggestions

- **PreToolUse infra-mutation guard** (recommended, domain-unique): exit-code-2
  block on raw `terraform apply|destroy`, `kubectl delete`, `pulumi destroy`,
  `cdk destroy`, redirecting to `/deploy`. Domain-specific matcher --
  see `Docs/Templates/Optional/hooks-template.md` for the exit-2 pattern; matcher
  string is `Bash`.
- **PreCompact auto-save** (recommended) -- preserve incident/deployment state.
- **Stop hook self-review** (recommended) -- scan changed plans/manifests/CI for
  security misconfig, exposed ports, over-permissive IAM before accepting.
- Optional **PostToolUse validate reminder** on `.tf/.yaml/.hcl/.j2` edits.
  All templated in `Docs/Templates/Optional/hooks-template.md`. Bash hooks need a
  Unix shell on Windows; prefer `"type": "prompt"`/`"agent"` if WSL/Git Bash absent.

## Cost / Model Notes

Opus for planner/reviewer/researcher/incident-responder (reasoning prevents outage
escalation and cost surprises); Sonnet for implementer (established-pattern IaC).
Defaults: balanced (compaction 95%, CLAUDE.md ~200 lines). Cost-conscious override:
all-Sonnet except incident-responder (keep Opus), consider merging researcher into
planner, compaction 85%, CLAUDE.md ~150, full RTK in GETTING_STARTED (filters
verbose `terraform plan` / `kubectl describe` output). Infra workflows are serial,
so subagents (~4x) are the default; teams ~15x. Summarize large plan output before
passing to reviewer; incident response is Bash-call-heavy (10-20 calls). Monitor
with `/cost`.

## Special Patterns

- **Infrastructure safety gate** (the key distinction from other profiles): every
  mutation runs plan/dry-run first (`terraform plan -out`, `kubectl diff`,
  `ansible-playbook --check`, `cfn --no-execute-changeset`), presents blast radius
  (CREATE low / MODIFY check-replacement / DESTROY high + cost), then STOPS for
  APPROVE/REJECT/MODIFY. Production always requires explicit approval; dev/staging
  may proceed after plan review. Lives in the `infrastructure-safety` rule + change
  log (what/why/blast radius/rollback/approver).
- **Pattern G (Pipeline skill)** -- `/deploy` wraps the per-tool plan-apply CLI flow.

## Customization Points

Cloud provider(s) + IaC tool (drives ecosystem permissions, validate/dry-run
commands, hook matchers); production vs dev gating policy (auto-approve dev?);
monitoring/alerting platform (Datadog/Grafana/PagerDuty -> WebFetch read-only);
secret backend (Vault/Secrets Manager -> read-only, never log values); GitHub
Actions present (-> `/install-github-app`, validation workflows); team shape.

## Team-architecture pattern

Producer-Reviewer (implement -> review) inside a Pipeline (plan -> implement ->
review -> deploy); incident response is a Supervisor pattern (incident-responder
drives, pulls in researcher/implementer). Subagents are the default. Consider
Agent Teams only when a deployment cleanly splits across non-overlapping module
layers (networking / compute / observability) with distinct file ownership --
prefer sequential subagents otherwise.

# Bundled Domain: Security Audit

Adapted from revfactory/harness-100 28-security-audit. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim). A starting point the architect adapts -- it points at templates, it does
not inline them. Builds on the Software Development base profile; specializes it
for code/dependency/infrastructure security auditing of authorized targets.

**Audience framing:** this seeds a tool FOR authorized security work -- AppSec
and pentest consultants, security engineers, and dev teams auditing systems they
OWN or have written permission to test. It produces **draft findings a human
security owner must verify and act on**; it is not a license to probe arbitrary
systems. The tool assists authorized testing only and REFUSES active testing of
third-party or live targets without recorded permission (see Safeguards).

## Profile Metadata

- **Target audience**: security engineers, AppSec/pentest consultants, and dev
  teams commissioning a code/dependency/infrastructure security audit of systems
  they own or are authorized to test
- **Primary tools**: SAST + dependency scanners (npm audit, pip-audit, Trivy,
  Snyk, Bandit, gitleaks/trufflehog), OWASP Top 10 / CWE / CVSS frameworks,
  NVD/OSV/GHSA advisory lookups via WebFetch, the target codebase's own language
  toolchain (read-mostly)
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**:
  conservative (audits are read-and-report; never auto-remediate, never run
  payloads, never probe an out-of-scope host) | **VCS**: Git

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| vulnerability-scanner | sonnet | Scan dependencies/containers/IaC for CVEs, misconfig, leaked secrets; generate the SBOM (dependency inventory); tag each finding provenance + record scanner DB/advisory date; CVSS-rank from published scores (read-only) | custom (closest: researcher.md) -- investigation/inventory, no code changes |
| code-analyst | opus | SAST: trace user-input source->sink, confirm reachability before any severity, map findings to OWASP Top 10 / CWE (current taxonomy), propose fix snippets (read-only) | reviewer.md |
| pentest-reporter | opus | Chain findings into attack scenarios (MITRE ATT&CK), write reachability/verification-only PoC steps (never destructive payloads), score business impact | custom (closest: drafter.md) -- attack-scenario report writing |
| security-consultant | opus | Build remediation roadmap (now/3mo/12mo), map to NIST CSF / ISO 27001 / CIS, cost-vs-risk priority, drive coordinated disclosure for not-owned components | custom (closest: drafter.md) -- remediation plan deliverable |
| audit-reviewer | opus | QA cross-validation: finding-provenance audit, severity/CVSS consistency, OWASP coverage, every Critical/High has a fix; final report | reviewer.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (conservative -- read-and-report default), context-management,
self-learning, error-handling (with diagnostic discipline), memory-management,
`vcs-git.md`. **Required domain rules:** (1) a pinned, always-loaded
authorization-scope + no-exploitation rule (template: `Optional/authorization-scope-rule.md`; see Safeguards) -- assists only
authorized testing, gates active testing to the in-scope asset list, and pins the
no-exploitation / no-exfiltration / no-destructive-payload constraint; (2)
`sensitive-data-rule.md` -- audits surface secrets, credentials, and PII;
discovered secrets and raw finding evidence are Restricted and redacted in every
artifact (see Safeguards).

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/security-audit` (pipeline
orchestrator), plus three knowledge skills carried over from the source harness:
`/owasp-testing-guide`, `/cve-analysis`, `/threat-modeling`. The three knowledge
skills follow Pattern B (reference skill -- methodology + checklists loaded on
demand by the analysis agents); author them from `Docs/Templates/Skills/review.md`
as the closest structural template. The carried-over harness content is stale and
must be REGENERATED to current standards, not lightly edited: refresh CWE mappings
and OWASP references (e.g., OWASP A06 "Vulnerable and Outdated Components" is a
Top-10 CATEGORY, not a CWE -- do not emit it as a CWE), and align CVE/CVSS guidance
to CVSS v4.0 with v3.1 fallback.

## Domain Routing Table

The orchestrator NEVER assigns a severity to the user's specific code, and NEVER
reports a CVE, from memory. Any specific authority (a CVE, a CVSS score, a
severity verdict on real code) routes to the agent that confirms it via a scanner
run, an NVD/OSV/GHSA retrieval, or source->sink reachability analysis.

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | "Run a full security audit" | /security-audit -> Phase-0 scope/authorization -> scanner + analyst (parallel) -> pentest -> consultant -> reviewer | Confirm authorization + capture in-scope/out-of-scope first; deliverables land in `Docs/_working/audit/` | clarify scope + authorization (if either unspecified) |
| 2 | "Scan dependencies / npm audit / Trivy" | vulnerability-scanner | Manifest files (package.json, requirements.txt, go.mod, Dockerfile); local source-only -- advisory authorization | /cve-analysis (methodology only, no code) |
| 3 | "Analyze this code for vulnerabilities" (SAST) | code-analyst -> audit-reviewer | Source->sink data-flow; reachability before severity; OWASP/CWE mapping; fix snippets | /owasp-testing-guide (methodology only, if code not provided) |
| 4 | "Find a specific OWASP issue" (XSS, SQLi, SSRF, IDOR) | code-analyst (guided by /owasp-testing-guide) | Per-category test cases + remediation pattern | answer directly -- explain the pattern only; no severity on the user's code without reachability confirmation |
| 5 | "Build attack scenarios / write a pentest report" | pentest-reporter | Needs scan + code-analysis results as input; reachability/verification-only PoC; never destructive payloads | code-analyst first (if no findings yet) |
| 6 | "Threat-model this system / STRIDE / attack surface" | security-consultant (guided by /threat-modeling) | DFD + trust boundaries; STRIDE/DREAD scoring | pentest-reporter (if attack-path focused) |
| 7 | "What CVEs affect this dependency" / CVSS score | vulnerability-scanner (guided by /cve-analysis) | Retrieve from NVD/OSV/GHSA; report published Base score + vector verbatim; record advisory date + affected-range vs installed version | answer directly ONLY for methodology; a named CVE must be retrieved, never recalled |
| 8 | "Recommend remediations / roadmap" | security-consultant -> audit-reviewer | Risk = exploitability x business impact; framework mapping; coordinated disclosure for not-owned components | scanner+analyst first (if no findings on disk) |
| 9 | "Review/validate an existing audit report" | audit-reviewer | Reads prior `0X_*.md`; finding-provenance + severity-consistency + fix-coverage checks | answer directly (single-doc skim, no new authority) |
| 10 | "Did we leak secrets / scan for credentials" | vulnerability-scanner (gitleaks/trufflehog --redact) | Classify Restricted; redact values in every artifact; flag rotation; others' secrets -> disclose to owner, never use/test | sensitive-data-rule escalation |
| 11 | "Triage / prioritize these findings" | security-consultant | CVSS Base + separate Priority/Environmental figure; exposure x exploitability; now/week/month buckets | answer directly (<5 findings, provenance already on file) |
| 12 | "Map findings to NIST CSF / ISO 27001 / CIS" | security-consultant | Identify/Protect/Detect/Respond/Recover gap analysis | /threat-modeling (control selection) |
| 13 | "Re-audit / track remediation since last report" | /security-audit (delta mode) -> consultant + reviewer | Reconfirm scope still authorized; load prior report from `Docs/_working/audit/`; track resolved vs open | full audit (if no prior baseline) |
| 14 | "Is finding X a true positive" | code-analyst | Confirm reachability/data flow before reporting; minimize false positives | pentest-reporter (exploitability check) |
| 15 | "Test / probe this live site or third-party service" | REFUSE unless host is on the recorded in-scope list | No active testing of not-owned/live targets without recorded permission; offer passive source/dependency review instead | capture authorization + in-scope asset (Phase-0) before any active step |

Complexity scaling: Simple (1 agent: single-CVE retrieval, one-file SAST, report
skim) | Standard (2-3 agents: dependency scan + review, targeted SAST + PoC) |
Complex (5-agent pipeline: scope->scan+analyze->pentest->remediate->review, with
up to 2 reviewer-driven correction rounds).

## Ecosystem Permissions

Base + Universal Deny + Git -- all in `Docs/Templates/References/ecosystem-permissions.md`.
Add the **language ecosystem(s) of the audited codebase** (Python, Node, Java,
Go, etc.) for the *read/scan* subcommands only. This domain is read-and-report:
treat the target codebase as read-mostly and keep auditor tooling in `allow`
while gating any write-back. Domain-specific permissions to add (not in the
reference):

- allow (read-only, local/source-only scanners): `npm audit *`, `pip-audit *`,
  `safety check *`, `bandit *`, `trivy fs *`, `trivy config *`, `grype *`,
  `gitleaks * --redact`, `trufflehog * --redact`, `semgrep *`, `osv-scanner *`,
  `syft *` (SBOM)
- gated (network/live-touching) -- NOT a blanket allow: `snyk test *`,
  `trivy image *`, and any scanner that reaches a remote host or registry are
  gated by the PreToolUse authorization hook to the host allow-list in
  `settings.local.json`. Deterministic by default for network/live targets.
- deny (no auto-remediation): `npm audit fix *`, `snyk monitor`, any
  `* --fix *` on the target, and writes to the audited source tree
- Confine all generated reports to `Docs/_working/audit/`; deny report writes
  elsewhere. Generate `settings.local.json` for machine-specific scanner paths
  (Snyk auth, private CVE DB endpoints) AND the `AUTHORIZED_HOSTS` allow-list the
  authorization hook reads.

## Safeguards (authorization, no-exploitation, provenance, disclosure, secrets)

Security-audit material -- live targets, discovered secrets, exploit detail -- is
the most dangerous data this library handles. These are NOT optional for the domain.

- **Authorization & scope (rules of engagement):** the tool assists ONLY
  authorized testing of systems the user owns or has written permission to test.
  Before ANY scan, probe, or PoC, the `/security-audit` Phase-0 step confirms
  authorization and captures `Docs/_working/audit/00_scope.md`: the in-scope asset
  list (hosts/repos/registries/cloud accounts) and explicit out-of-scope
  exclusions. The orchestrator REFUSES active testing of any third-party or live
  target not on the recorded in-scope list. **Out-of-scope by default** (carried
  from the harness): no live network penetration, no active exploitation, no
  real-time intrusion -- only static/source/dependency review -- unless the host
  appears on the authorized in-scope list.
- **No exploitation / no exfiltration / no destructive payload (pinned,
  always-loaded):** a PoC demonstrates reachability or verifies a finding only. It
  NEVER runs a payload that alters, deletes, exfiltrates, or persists on the
  target. pentest-reporter writes verification-only steps; the self-learning rule
  treats any drift toward a working destructive payload as a regression.
- **Finding provenance (mirrors legal citation integrity -- Rule 3.3 analog):**
  every CVE/finding is tagged TOOL-CONFIRMED (emitted by a named scanner run, OR
  retrieved from NVD/OSV/GHSA via WebFetch with the source URL + retrieval date
  recorded) vs UNVERIFIED-RECALL (remembered, not retrieved). An UNVERIFIED-RECALL
  CVE may NEVER appear as a reported finding -- only on a clearly separated "Leads
  to verify (NOT findings)" list. On retrieval failure, do NOT proceed from general
  security knowledge as if authoritative -- report the gap.
- **CVSS handling:** report the published NVD/vendor Base score + vector VERBATIM
  (do not recompute from a recalled vector). Present any exposure/exploitability-
  adjusted number as a SEPARATE, clearly labeled Priority/Environmental figure --
  never overwriting the Base score. Use CVSS v4.0 (fall back to v3.1); record the
  version and the full vector string. Record the scanner DB / advisory date per
  finding, and state the installed version vs the affected range per CVE (a CVE on
  a version you do not run is not a finding).
- **Responsible disclosure:** findings affecting components or systems the user
  does NOT own (upstream library CVEs, third-party services, another party's leaked
  secret) follow coordinated disclosure -- report to the owner/vendor, do not
  publish a PoC before remediation, and NEVER use or test another party's secret;
  flag it to the owner for rotation. security-consultant owns the disclosure path
  in the roadmap.
- **Secret / evidence handling (`sensitive-data-rule.md`, required):** classify
  discovered secrets, credentials, PII, and raw finding evidence as Restricted.
  Redact secret values when summarizing scanner output into ANY artifact -- not
  only at final report-write -- using `gitleaks/trufflehog --redact`. EXCLUDE secret
  values, raw evidence, and PoC payloads from `Docs/_working/retro/`, `/state-save`
  output, and PreCompact summaries; keep them only in the audit deliverable under
  `Docs/_working/audit/`. Report location + type + rotation action, not the value.
- **Enforcement:** the PreToolUse gates (below) default DETERMINISTIC for live/
  network targets and for secret redaction; advisory is acceptable only for
  local/source-only scanning where no payload and no remote host are involved.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Active test without recorded permission -- a scan/probe ran
  against a live or third-party host not on the in-scope list. Mitigation: Phase-0
  00_scope.md gates all active testing; refuse not-owned/live targets absent recorded
  authorization.
- [PATTERN] (pre-seeded) UNVERIFIED-RECALL CVE reported as a finding -- a remembered CVE
  appeared in the report without a scanner run or NVD/OSV/GHSA retrieval. Mitigation:
  tag every CVE TOOL-CONFIRMED vs UNVERIFIED-RECALL; UNVERIFIED-RECALL never appears as
  a finding, only as a lead to verify.
- [PATTERN] (pre-seeded) CVE currency / version mismatch -- a CVE was reported against a
  version the target does not run, or a recomputed CVSS overwrote the Base score.
  Mitigation: record advisory date + installed-vs-affected range; report Base score +
  vector verbatim; keep exposure-adjusted risk as a separate Priority figure.
- [PATTERN] (pre-seeded) Missed responsible disclosure -- a not-owned upstream/third-party
  finding (or another party's leaked secret) was treated as the user's to publish/test.
  Mitigation: coordinated disclosure -- report to owner/vendor, no PoC before fix, never
  use another party's secret; flag rotation.
- [PATTERN] (pre-seeded) Secret or PoC payload leaked into retro/state/compaction -- a live
  credential or destructive payload was written to a long-lived store. Mitigation: redact
  at every summarization step; exclude secret values, raw evidence, and PoC from
  retro/state/PreCompact; keep them only in the audit deliverable.
- [PATTERN] (pre-seeded) PoC drifts into real exploitation -- pentest-reporter wrote
  destructive/exfiltration/persistence steps. Mitigation: reachability/verification-only;
  no payloads that alter, delete, exfiltrate, or persist.
- [PATTERN] (pre-seeded) False positives from pattern-only matching -- a flagged sink is
  unreachable. Mitigation: code-analyst confirms source->sink reachability before any
  severity; mark "needs data-flow confirmation" otherwise.
- [PATTERN] (pre-seeded) Severity drift across reports -- scanner CVSS, code-analyst rating,
  and pentest impact disagree on the same finding. Mitigation: audit-reviewer reconciles by
  stable vulnerability ID before the final report.
- [PATTERN] (pre-seeded) Critical finding with no fix -- a Critical/High shipped without a
  remediation entry. Mitigation: reviewer blocks the final report until every Critical/High
  maps to a remediation item.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- preserve audit scope (00_scope.md
  reference), open findings, and provenance tags across compaction. EXCLUDE secret
  values, raw evidence, and PoC payloads. See `Docs/Templates/Optional/hooks-template.md`.
- **PreToolUse authorization gate** (domain-unique, recommended; DETERMINISTIC by
  default for network/live targets, advisory for local source-only) -- intercepts
  network-touching scanners (`snyk test`, `trivy image`, anything reaching a remote
  host/registry) and blocks the run unless the target host is on the
  `AUTHORIZED_HOSTS` allow-list in `settings.local.json` (populated from
  00_scope.md). Without it, scope enforcement is advisory only.
- **PreToolUse secret-redaction gate** (domain-unique, recommended) -- scans
  outbound writes to ANY artifact for live-secret patterns (AWS `AKIA...`, GitHub
  `ghp_...`, JWT, PRIVATE KEY blocks) and blocks/redacts before write. Pair with
  `sensitive-data-rule.md`. Without it, redaction is advisory only.
- **PreToolUse finding-integrity gate** (domain-unique, recommended) -- on writes
  to the report deliverable, block/warn if a CVE token does not trace to a scanner
  run or a recorded NVD/OSV/GHSA retrieval artifact (no UNVERIFIED-RECALL CVE as a
  finding).
- Optional **Stop hook** coverage check -- warn if a final report references a
  Critical/High vulnerability ID that has no matching remediation entry.

## Cost / Model Notes

Opus for the reasoning roles -- code-analyst (data-flow + false-positive judgment),
pentest-reporter (attack-chain construction), security-consultant (risk
prioritization + framework + disclosure), audit-reviewer (cross-validation).
Sonnet for vulnerability-scanner (running scanners, retrieving advisories, and
tabulating published-CVSS output is established-pattern execution). Defaults:
balanced (Opus on judgment roles, Sonnet on scanning; compaction 95%; CLAUDE.md
~200 lines). Quality-first override appropriate when the audit is compliance-bearing
(all-Opus, reviewer gets 2 correction rounds). The 5-agent serial pipeline is ~4x a
direct conversation per full audit -- reserve it for full audits, not single lookups.

## Customization Points

- Audit target shape (source code / dependencies / IaC+containers / live URL)
  -- drives which scanner permissions and which OWASP categories apply, and
  whether the authorization gate runs deterministic (live/network) or advisory
  (local source-only).
- **Authorization enforcement strength**: deterministic for any live/network
  target (gate blocks scanners against hosts not on the allow-list); advisory only
  when the engagement is strictly local source/dependency review with no remote
  host and no payload. Records of authorization (00_scope.md + AUTHORIZED_HOSTS)
  are mandatory regardless.
- Audited codebase language(s) -- drives the ecosystem permission set and which
  dependency scanner (npm audit / pip-audit / dependency-check / Trivy).
- Compliance frameworks in scope (NIST CSF / ISO 27001 / CIS / GDPR / PCI) --
  drives the consultant's mapping tables and roadmap fields.
- Deterministic vs advisory secret handling -- whether the PreToolUse redaction
  hook is generated or `sensitive-data-rule.md` stays advisory.
- Regenerate (do not lightly edit) the three carried-over knowledge skills
  (`/owasp-testing-guide`, `/cve-analysis`, `/threat-modeling`): refresh CWE
  mappings, fix the OWASP-category-vs-CWE error (A06 is a category), and align to
  CVSS v4.0 (v3.1 fallback). Add SBOM generation to the vulnerability-scanner role.
- One-shot audit vs recurring re-audit -- recurring adds delta/baseline tracking
  in `Docs/_working/audit/` and the Stop coverage hook; reconfirm scope each run.

## Team-architecture pattern

Pipeline (scope -> scan + analyze -> pentest -> remediate -> review) with a
Producer-Reviewer gate at the end: audit-reviewer cross-validates the upstream
deliverables (including finding provenance) and can bounce a phase back for up to
2 correction rounds. Phase 0 captures authorization/scope (00_scope.md) before any
active step. Phase 1 fans out -- vulnerability-scanner and code-analyst run in
parallel (no data dependency) before converging into the pentest-reporter.
Subagents are the default and sufficient here; the only candidate for Agent Teams
is the parallel Phase-1 scan+analyze split, and even that is cheaper as two
concurrent subagent calls than a full team -- reserve teams for audits large enough
that scanner and analyst must exchange intermediate findings live.

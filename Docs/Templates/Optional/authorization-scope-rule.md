# Authorization & Scope Rule (Template)

<!-- ANNOTATION: Generate this rule for ANY security-testing / offensive /
     red-team / vulnerability-assessment domain (GENESIS indicates pentest,
     security audit, scanning, exploit work). It is the offensive-domain analogue
     of sensitive-data-rule.md: an always-loaded advisory rule plus a bridge to an
     optional deterministic PreToolUse authorization gate. The Harness Generator only assists
     AUTHORIZED security testing -- this rule is what enforces that in a generated
     environment. Pair it with the secret-redaction PreToolUse gate. -->

<!-- QUALITY: Must state the authorized-only posture, require a recorded scope +
     authorization before active testing, pin the no-exploitation constraint
     (always-loaded, not just a self-learning seed), and cover responsible
     disclosure. Under 120 lines. -->

## Example: Authorization & Scope Rule (`.codex/rules/0X-authorization-scope.md`)

````markdown
# Authorization and scope

This environment assists ONLY authorized security testing -- of systems the
operator owns or has explicit written permission to test. It is not for testing
systems the operator does not own or lacks authorization for.

## Before any active testing

Before running a scanner, probe, request, or proof-of-concept against a target,
confirm and record (in `Docs/_working/audit/00_scope.md`):
- the in-scope asset list (hosts, repos, URLs, accounts) the operator is authorized to test;
- explicit out-of-scope exclusions;
- the authorization basis (engagement letter / written permission / "I own this").

If authorization for a target is not recorded, REFUSE active testing of it and ask
for it. Static analysis of source the operator provided is lower-risk; active
scanning/probing of live or third-party hosts requires recorded authorization.

## No exploitation (always applies)

A proof-of-concept demonstrates reachability/verification ONLY. Never run a payload
that alters, deletes, exfiltrates, or persists on a target. No live network
penetration, active exploitation, or real-time intrusion against any host not on
the authorized in-scope list. Reproduction steps are recorded as non-executable
descriptions, not copy-paste-runnable destructive commands.

## Responsible disclosure

Findings affecting components/systems the operator does not own (upstream CVEs,
third-party services, another party's leaked secret) follow coordinated
disclosure: report to the owner/vendor, do not publish PoC or exploit detail
before remediation, and never use or test another party's secret -- flag rotation
as the owner's action.

## Finding integrity

Report a CVE/vulnerability only when it is tool-confirmed (a named scanner emitted
it) or retrieved from an authoritative advisory (NVD/OSV/GHSA) with the source
recorded -- never a CVE recalled from memory. Report the published Base CVSS score
+ vector verbatim; present exposure-adjusted risk as a separate, labeled figure.
````

<!-- VARIATION: For a deterministic posture (live/network targets), pair this rule
     with a PreToolUse authorization gate that blocks network-touching scanner
     commands unless the target matches an authorized-host allow-list in
     local config profile. For local source-only audits the rule may stay advisory.
     See hooks-template.md for the PreToolUse gate structure. -->

<!-- QUALITY: Validation checklist:
     - [ ] Authorized-only posture stated up front
     - [ ] Recorded scope + authorization required before active testing
     - [ ] No-exploitation / no-exfiltration constraint pinned (always-loaded)
     - [ ] Responsible-disclosure handling present
     - [ ] Finding-provenance (tool-confirmed vs recalled) present
     - [ ] Rule body under 120 lines
-->

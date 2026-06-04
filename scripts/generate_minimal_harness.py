#!/usr/bin/env python3
"""Generate a minimal Codex harness for acceptance tests and examples.

This is intentionally small and deterministic. It does not replace the full
model-mediated /create workflow; it gives the project a fast product-proof path:
write a complete harness to disk, then run the same evaluator used for golden
fixtures.
"""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Profile:
    slug: str
    default_project_name: str
    domain: str
    target: str
    permission_profile: str
    reviewer_description: str
    agent_focus: str
    verification: tuple[str, ...]
    first_tasks: tuple[str, ...]
    assumptions: tuple[str, ...]
    extra_guidance: tuple[str, ...] = ()


SOURCE_URLS = [
    "https://developers.openai.com/codex/config-reference",
    "https://developers.openai.com/codex/guides/agents-md",
    "https://developers.openai.com/codex/subagents",
    "https://developers.openai.com/codex/skills",
    "https://developers.openai.com/codex/permissions",
]

CREATION_CONTEXT_PATH = Path("Docs") / "Environment" / "CREATION_CONTEXT.md"

PROFILES = {
    "software-development": Profile(
        slug="software-development",
        default_project_name="Minimal Python CLI",
        domain="software development",
        target="a small Python CLI utility",
        permission_profile="software-dev",
        reviewer_description="Reviews Python CLI changes for bugs, missing tests, regressions, and security risks.",
        agent_focus="Python CLI changes",
        verification=(
            "Run `python -m pytest` when tests exist.",
            "Run the specific CLI command being changed when no tests exist.",
            "If no runnable check exists, explain that limitation plainly.",
        ),
        first_tasks=(
            "Ask Codex to explain the CLI entry point.",
            "Ask for one tiny change and verify the result.",
            "Ask the reviewer to inspect the change before finalizing.",
        ),
        assumptions=(
            "This deterministic harness targets a small Python CLI utility for a solo developer.",
            "The project has local files that can be inspected before edits.",
            "The narrowest meaningful check is usually a unit test or CLI command.",
        ),
    ),
    "knowledge-work": Profile(
        slug="knowledge-work",
        default_project_name="Knowledge Work Hub",
        domain="knowledge work",
        target="a document-heavy research, planning, or operations workspace",
        permission_profile="knowledge-work",
        reviewer_description="Reviews research, planning, and operations outputs for source fidelity, missing context, and privacy risks.",
        agent_focus="research notes, plans, summaries, and operational documents",
        verification=(
            "Check cited source files before summarizing or rewriting.",
            "Compare final claims against the source notes or documents.",
            "Mark missing source access, uncertainty, and unresolved assumptions plainly.",
        ),
        first_tasks=(
            "Ask Codex to map the key docs and their roles.",
            "Ask for a concise source-backed summary of one folder.",
            "Ask the reviewer to check whether the summary overclaims.",
        ),
        assumptions=(
            "This deterministic harness targets local documents, notes, and lightweight operations artifacts.",
            "The user values source fidelity over polished unsupported claims.",
            "Verification means checking source files and surfacing missing evidence.",
        ),
    ),
    "data-analysis": Profile(
        slug="data-analysis",
        default_project_name="Data Analysis Workspace",
        domain="data analysis",
        target="a local data analysis workspace with scripts, notebooks, and reports",
        permission_profile="data-analysis",
        reviewer_description="Reviews analysis changes for reproducibility, data handling, metric definitions, and unsupported conclusions.",
        agent_focus="analysis scripts, metrics, reports, and reproducibility notes",
        verification=(
            "Run the narrowest analysis script, notebook check, or test available.",
            "Inspect input schemas and row counts before changing calculations.",
            "State metric definitions, denominators, exclusions, and data limits.",
        ),
        first_tasks=(
            "Ask Codex to identify datasets, scripts, and output reports.",
            "Ask for a metric definition map before changing analysis logic.",
            "Ask the reviewer to inspect reproducibility and unsupported claims.",
        ),
        assumptions=(
            "This deterministic harness targets local analysis artifacts rather than live production data.",
            "Sensitive data may exist, so credential and raw secret files stay denied.",
            "Verification requires reproducible commands or explicit data-access limits.",
        ),
    ),
    "devops-infrastructure": Profile(
        slug="devops-infrastructure",
        default_project_name="Infrastructure Workspace",
        domain="DevOps and infrastructure",
        target="a local infrastructure or deployment workspace",
        permission_profile="devops-infra",
        reviewer_description="Reviews infrastructure changes for blast radius, rollback paths, secret handling, and missing validation.",
        agent_focus="infrastructure config, deployment scripts, runbooks, and operational checks",
        verification=(
            "Prefer dry-run, plan, lint, or validation commands before applying changes.",
            "Inspect target environment names before editing deployment files.",
            "Document rollback steps and commands that were not run.",
        ),
        first_tasks=(
            "Ask Codex to map environments, deployment files, and runbooks.",
            "Ask for a dry-run validation of one small infrastructure change.",
            "Ask the reviewer to inspect blast radius and rollback notes.",
        ),
        assumptions=(
            "This deterministic harness targets local infrastructure files and runbooks.",
            "Destructive commands need explicit user approval and rollback context.",
            "Verification should prefer dry-run or validation commands when available.",
        ),
    ),
}


def domain_profile(
    slug: str,
    default_project_name: str,
    domain: str,
    target: str,
    reviewer_focus: str,
    verification: tuple[str, ...],
    first_tasks: tuple[str, ...],
    assumptions: tuple[str, ...],
    extra_guidance: tuple[str, ...] = (),
) -> Profile:
    return Profile(
        slug=slug,
        default_project_name=default_project_name,
        domain=domain,
        target=target,
        permission_profile=slug,
        reviewer_description=f"Reviews {domain} outputs for source fidelity, correctness, privacy, safety, and missing verification.",
        agent_focus=reviewer_focus,
        verification=verification,
        first_tasks=first_tasks,
        assumptions=assumptions,
        extra_guidance=extra_guidance,
    )


PROFILES.update(
    {
        "api-design": domain_profile(
            "api-design",
            "API Design Workspace",
            "API design",
            "REST, GraphQL, or service API design work",
            "API contracts, endpoint behavior, compatibility, examples, and documentation",
            (
                "Validate API examples against the documented request and response schemas.",
                "Check compatibility and versioning impact before changing contracts.",
                "Flag undocumented authentication, authorization, rate-limit, and error behaviors.",
            ),
            (
                "Ask Codex to map existing API docs, schemas, and examples.",
                "Ask for a small endpoint spec or API contract check.",
                "Ask the reviewer to inspect compatibility and missing examples.",
            ),
            (
                "This deterministic harness targets local API design artifacts and examples.",
                "API contracts should stay source-backed and compatible with documented clients.",
                "Verification means checking examples, schemas, and compatibility notes.",
            ),
        ),
        "book-publishing": domain_profile(
            "book-publishing",
            "Book Publishing Workspace",
            "book publishing",
            "long-form manuscript editing, production, and publishing work",
            "manuscript structure, editorial consistency, style guidance, and production checklists",
            (
                "Compare edits against the source manuscript before changing meaning.",
                "Check style, continuity, and chapter-level consistency.",
                "Mark publishing, rights, or distribution questions that need human review.",
            ),
            (
                "Ask Codex to map manuscript files and production notes.",
                "Ask for a source-faithful edit of one section.",
                "Ask the reviewer to inspect continuity and over-editing.",
            ),
            (
                "This deterministic harness targets local manuscript and publishing files.",
                "Source fidelity matters more than smoothing unsupported meaning changes.",
                "Verification means comparing edits against source chapters and style notes.",
            ),
        ),
        "course-design": domain_profile(
            "course-design",
            "Course Design Workspace",
            "course design",
            "curriculum, lesson, assessment, and learning-objective design",
            "learning objectives, lesson flow, assessment alignment, and learner-facing clarity",
            (
                "Map lessons and assessments back to stated learning objectives.",
                "Check that examples and rubrics match the intended learner level.",
                "Flag unsupported learning claims or missing prerequisite assumptions.",
            ),
            (
                "Ask Codex to map objectives, lessons, and assessments.",
                "Ask for one lesson outline with assessment alignment.",
                "Ask the reviewer to inspect learner-level fit and rubric clarity.",
            ),
            (
                "This deterministic harness targets local course planning and curriculum files.",
                "Instructional claims should be tied to supplied objectives and learner context.",
                "Verification means checking objective, lesson, assessment, and rubric alignment.",
            ),
        ),
        "customer-support": domain_profile(
            "customer-support",
            "Customer Support Workspace",
            "customer support",
            "customer-support documentation, FAQ, response, escalation, and support-ops work",
            "support source grounding, privacy, escalation, draft commitments, and customer-facing claim discipline",
            (
                "Ground customer-facing facts in supplied policy, product, or ticket sources.",
                "Mark unknowns as `[VERIFY]` and commitments as `[PROPOSED -- requires owner approval]`.",
                "Escalate safety-critical, privacy, breach, account-action, or regulated-advice requests to human review.",
            ),
            (
                "Ask Codex to map support sources and ticket categories.",
                "Ask for one grounded FAQ or escalation note.",
                "Ask the reviewer to inspect privacy, escalation, and overpromised claims.",
            ),
            (
                "This deterministic harness targets support documentation and support-ops artifacts.",
                "Customer-facing facts require source grounding and owner approval for commitments.",
                "Verification means checking sources, privacy, PII, escalation, and draft boundaries.",
            ),
            (
                "Protect customer privacy and PII; do not expose personal data, account identifiers, payment data, or private transcripts.",
                "Escalate or handoff safety-critical, breach, DSAR, regulated advice, account disclosure, and account-changing requests for human review.",
                "Use source-backed claims only; verify policy facts and do not promise refunds, fix dates, SLAs, roadmap items, or account outcomes.",
            ),
        ),
        "data-engineering": domain_profile(
            "data-engineering",
            "Data Engineering Workspace",
            "data engineering",
            "data pipeline, schema, ETL, validation, and monitoring work",
            "pipeline logic, schemas, data contracts, validation checks, and operational reliability",
            (
                "Inspect schemas, contracts, row counts, and partition assumptions before changing pipelines.",
                "Run narrow validation, lint, or sample-data checks when available.",
                "State data quality limits, backfill risk, and rollback or replay requirements.",
            ),
            (
                "Ask Codex to map datasets, schemas, and pipeline entry points.",
                "Ask for a small data-contract or validation check.",
                "Ask the reviewer to inspect data quality and backfill risk.",
            ),
            (
                "This deterministic harness targets local pipeline, schema, and validation files.",
                "Sensitive data may exist, so raw secrets and credentials stay denied.",
                "Verification means checking schemas, sample data, validation commands, and operational limits.",
            ),
        ),
        "data-science": domain_profile(
            "data-science",
            "Data Science Workspace",
            "data science",
            "offline data science, model assessment, experiment, and research-analysis work",
            "experiment design, leakage risk, metrics, reproducibility, and model-assessment limits",
            (
                "Inspect data splits, metric definitions, and leakage risks before changing analysis.",
                "Run the narrowest reproducible notebook, script, or test check available.",
                "Report assumptions, confidence limits, sample size, and assessment caveats.",
            ),
            (
                "Ask Codex to map datasets, notebooks, scripts, and reports.",
                "Ask for a metric and leakage-risk review.",
                "Ask the reviewer to inspect reproducibility and unsupported conclusions.",
            ),
            (
                "This deterministic harness targets offline data science artifacts.",
                "Model and metric claims require reproducible source evidence.",
                "Verification means checking data splits, metrics, scripts, and limitations.",
            ),
        ),
        "financial-modeling": domain_profile(
            "financial-modeling",
            "Financial Modeling Workspace",
            "financial modeling",
            "financial modeling, projections, scenario analysis, and investor-facing support work",
            "assumptions, calculations, scenarios, risk, uncertainty, and not-financial-advice boundaries",
            (
                "Check formulas, assumptions, scenario labels, and source files before changing outputs.",
                "Separate base, upside, downside, sensitivity, risk, uncertainty, and limits.",
                "State decision support only; do not provide financial or investment advice.",
            ),
            (
                "Ask Codex to map assumptions, tabs, reports, and metric definitions.",
                "Ask for one source-backed scenario note.",
                "Ask the reviewer to inspect calculations and advice-boundary risks.",
            ),
            (
                "This deterministic harness targets local financial-modeling artifacts.",
                "Numerical claims require cited local assumptions and verified calculations.",
                "Verification means checking assumptions, scenario formulas, sensitivity, risk, and limits.",
            ),
            (
                "This is decision support, not financial advice or investment advice.",
                "Document assumptions, scenarios, sensitivity, limits, risk, uncertainty, downside cases, and caveats.",
                "Do not invent market data, valuations, forecasts, securities, counterparties, or recommendations.",
            ),
        ),
        "game-development": domain_profile(
            "game-development",
            "Game Development Workspace",
            "game development",
            "gameplay, engine, build, performance, and playtest work",
            "gameplay changes, engine constraints, asset safety, performance, builds, and playtest notes",
            (
                "Inspect engine, platform, asset, and build constraints before editing.",
                "Run the narrowest build, unit, scene, or playtest check available.",
                "Avoid destructive binary-asset changes without a backup or explicit approval.",
            ),
            (
                "Ask Codex to map engine, scenes, scripts, assets, and build commands.",
                "Ask for one small gameplay or tooling change.",
                "Ask the reviewer to inspect build risk and playtest notes.",
            ),
            (
                "This deterministic harness targets local game project files and docs.",
                "Binary assets and project settings can be fragile and need conservative handling.",
                "Verification means build, scene, test, or manual playtest evidence where possible.",
            ),
        ),
        "grant-writing": domain_profile(
            "grant-writing",
            "Grant Writing Workspace",
            "grant writing",
            "grant proposals, funding narratives, budgets, and submission packets",
            "proposal fit, funder criteria, budget consistency, source support, and deadline assumptions",
            (
                "Map proposal claims back to funder criteria and supplied source materials.",
                "Check budget figures, deadlines, and eligibility against source files.",
                "Flag missing attachments, unsupported claims, and owner-review needs.",
            ),
            (
                "Ask Codex to map funder criteria and proposal materials.",
                "Ask for one source-backed proposal section.",
                "Ask the reviewer to inspect eligibility, budget, and unsupported claims.",
            ),
            (
                "This deterministic harness targets grant proposal and funder-material files.",
                "Proposal claims should preserve source fidelity and funder criteria.",
                "Verification means checking criteria, budget, deadlines, and source support.",
            ),
        ),
        "hiring-pipeline": domain_profile(
            "hiring-pipeline",
            "Hiring Pipeline Workspace",
            "hiring pipeline",
            "hiring-pipeline, job, rubric, interview, and candidate-evidence support work",
            "structured criteria, job-related evidence, bias, fairness, privacy, and human-review boundaries",
            (
                "Fix structured criteria, rubric, and scorecard anchors before evaluating evidence.",
                "Map every criterion to job-related requirements and avoid protected-class proxies.",
                "State decision support only; human reviewers own adverse decisions.",
            ),
            (
                "Ask Codex to map role requirements, criteria, and interview materials.",
                "Ask for one structured scorecard or interview guide.",
                "Ask the reviewer to inspect bias, privacy, and human-review boundaries.",
            ),
            (
                "This deterministic harness targets hiring-process and evaluation-support files.",
                "Candidate data is sensitive and must be minimized or deidentified.",
                "Verification means checking structured criteria, job-related evidence, fairness, privacy, and human-review limits.",
            ),
            (
                "Mitigate bias, discrimination, and fairness risks; do not use protected class traits or proxies.",
                "Use structured criteria, rubrics, scorecards, and job-related evidence only.",
                "Protect candidate privacy, candidate data, personal data, and PII; never automate screen-outs, rankings, rejections, or adverse actions without human review.",
            ),
        ),
        "legal-research": domain_profile(
            "legal-research",
            "Legal Research Workspace",
            "legal research",
            "legal research, policy, contract, source review, and memo support work",
            "jurisdiction, source citation, uncertainty, assumptions, and not-legal-advice boundaries",
            (
                "Identify jurisdiction and source scope before summarizing legal materials.",
                "Cite supplied statutes, cases, policies, or section labels for substantive claims.",
                "State research support only; do not provide legal advice.",
            ),
            (
                "Ask Codex to map legal sources and open questions.",
                "Ask for one source-backed research note.",
                "Ask the reviewer to inspect citations and jurisdiction boundaries.",
            ),
            (
                "This deterministic harness targets local legal or policy research artifacts.",
                "Legal claims require source citations and clear limits.",
                "Verification means checking jurisdiction, source citations, assumptions, uncertainty, and attorney-review needs.",
            ),
            (
                "State jurisdiction, limits, assumptions, uncertainty, and not legal advice boundaries.",
                "Cite sources, statutes, cases, policies, and section labels; verify citations before finalizing.",
                "Escalate advice, strategy, filing, risk acceptance, or real-world legal decisions to an attorney or lawyer.",
            ),
        ),
        "llm-app": domain_profile(
            "llm-app",
            "LLM App Workspace",
            "LLM app",
            "LLM-powered app, RAG, agent, prompt, and eval workflow development",
            "prompt contracts, evals, retrieval quality, model boundaries, safety, and observability",
            (
                "Inspect prompts, retrieval sources, eval cases, and model boundaries before changing behavior.",
                "Run focused evals or fixture tests when available.",
                "Document hallucination, privacy, cost, latency, and safety limits.",
            ),
            (
                "Ask Codex to map prompts, tools, evals, and retrieval sources.",
                "Ask for one eval case or prompt-contract improvement.",
                "Ask the reviewer to inspect failure modes and privacy risks.",
            ),
            (
                "This deterministic harness targets local LLM app code, prompts, and eval assets.",
                "Model behavior claims require eval evidence and source grounding.",
                "Verification means focused evals, fixtures, prompt reviews, and explicit limitations.",
            ),
        ),
        "market-research": domain_profile(
            "market-research",
            "Market Research Workspace",
            "market research",
            "market sizing, competitor research, landscape analysis, and research reports",
            "source quality, assumptions, sizing logic, citation discipline, and unsupported claims",
            (
                "Cite supplied sources for market, competitor, customer, and sizing claims.",
                "Separate facts, estimates, assumptions, and uncertainty.",
                "Flag stale sources, missing dates, and unsupported extrapolations.",
            ),
            (
                "Ask Codex to map research sources and open questions.",
                "Ask for one source-backed market note.",
                "Ask the reviewer to inspect assumptions and unsupported claims.",
            ),
            (
                "This deterministic harness targets local research sources and market reports.",
                "Market claims require citations, dates, and clear assumptions.",
                "Verification means checking sources, estimates, assumptions, uncertainty, and limits.",
            ),
        ),
        "product-management": domain_profile(
            "product-management",
            "Product Management Workspace",
            "product management",
            "PRDs, roadmap, prioritization, stakeholder specs, and product planning work",
            "user needs, scope, acceptance criteria, tradeoffs, sequencing, and source-backed decisions",
            (
                "Map requirements back to user evidence, stakeholder notes, or product goals.",
                "Check acceptance criteria, scope boundaries, and tradeoffs before finalizing specs.",
                "Flag assumptions, unresolved decisions, and missing validation.",
            ),
            (
                "Ask Codex to map PRDs, roadmaps, issues, and stakeholder notes.",
                "Ask for one scoped PRD or acceptance-criteria pass.",
                "Ask the reviewer to inspect tradeoffs and unsupported priorities.",
            ),
            (
                "This deterministic harness targets local product planning artifacts.",
                "Product decisions should cite user evidence or explicit assumptions.",
                "Verification means checking acceptance criteria, source notes, scope, and tradeoffs.",
            ),
        ),
        "security-audit": domain_profile(
            "security-audit",
            "Security Audit Workspace",
            "security audit",
            "defensive security audit, vulnerability review, threat model, and remediation work",
            "defensive findings, affected paths, severity, authorization boundaries, secrets, and safe remediation",
            (
                "Verify findings against files, dependencies, configs, or command output.",
                "Ask for authorization before active testing, exploit reproduction, scanners, or destructive work.",
                "Prioritize secret, token, credential, private key, privacy, and permission risks.",
            ),
            (
                "Ask Codex to map audit scope and sensitive files.",
                "Ask for one defensive security review of a small target.",
                "Ask the reviewer to inspect evidence, severity, and remediation safety.",
            ),
            (
                "This deterministic harness targets defensive security audit artifacts.",
                "Security work requires authorization, source evidence, and safe remediation.",
                "Verification means checking affected paths, permissions, secrets, active-testing limits, and destructive-work boundaries.",
            ),
            (
                "Treat secrets, tokens, credentials, private keys, and authorization boundaries as first-class concerns.",
                "Do not run exploit code, penetration test actions, active testing, scanners, or destructive work without explicit approval.",
                "Keep security audit outputs defensive: cite evidence, affected paths, severity, safe remediation, and verification limits.",
            ),
        ),
        "social-media": domain_profile(
            "social-media",
            "Social Media Workspace",
            "social media",
            "content calendar, post copy, campaign planning, and social analytics work",
            "channel fit, brand voice, claims, source material, and publishing-readiness checks",
            (
                "Check source material, claims, dates, and channel constraints before drafting posts.",
                "Keep public-facing copy grounded and avoid unsupported product or event claims.",
                "Mark approvals, assets, and scheduling assumptions before publishing.",
            ),
            (
                "Ask Codex to map campaign briefs, source assets, and channels.",
                "Ask for one channel-specific post set.",
                "Ask the reviewer to inspect claim accuracy and brand fit.",
            ),
            (
                "This deterministic harness targets local campaign and content-planning artifacts.",
                "Public copy should preserve source claims and approval boundaries.",
                "Verification means checking briefs, source assets, channel constraints, and approval status.",
            ),
        ),
    }
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def only_contains_creation_context(target: Path) -> bool:
    files = [path.relative_to(target) for path in target.rglob("*") if path.is_file()]
    if not files:
        return True
    return files == [CREATION_CONTEXT_PATH]


def ensure_target(target: Path, force: bool, allow_creation_context: bool = False) -> None:
    if target.exists() and any(target.iterdir()):
        if allow_creation_context and only_contains_creation_context(target):
            return
        if not force:
            raise SystemExit(f"Target is not empty. Re-run with --force to replace it: {target}")
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)


def bullet_list(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items)


def numbered_list(items: tuple[str, ...], start: int = 1) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start))


def optional_section(title: str, items: tuple[str, ...]) -> str:
    if not items:
        return ""
    return f"\n## {title}\n\n{bullet_list(items)}\n"


def local_check_script() -> str:
    return r'''#!/usr/bin/env python3
"""Local smoke check for a generated Codex harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "AGENTS.md",
    ".codex/config.toml",
    ".codex/agents/reviewer.toml",
    ".codex/rules/core.md",
    ".agents/skills/health-check/SKILL.md",
    "Docs/GETTING_STARTED.md",
    "Docs/Environment/GENESIS.md",
    "Docs/Environment/ARCHITECTURE.md",
    "Docs/Environment/ASSUMPTIONS.md",
    "Docs/Environment/MANIFEST.md",
    "Docs/Environment/SOURCE_MAP.md",
    "Docs/Environment/VALIDATION_REPORT.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_skill_metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    metadata = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    return metadata


def parse_config(text: str) -> dict:
    if tomllib is not None:
        return tomllib.loads(text)

    config: dict = {"agents": {}, "skills": {"config": []}}
    current_agent = None
    current_skill = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[agents.") and line.endswith("]"):
            current_agent = line[len("[agents.") : -1]
            current_skill = None
            config["agents"].setdefault(current_agent, {})
            continue
        if line == "[[skills.config]]":
            current_agent = None
            current_skill = {}
            config["skills"]["config"].append(current_skill)
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if current_agent and key == "config_file":
            config["agents"][current_agent]["config_file"] = value
        if current_skill is not None and key == "path":
            current_skill["path"] = value
    return config


def main() -> int:
    issues = []
    for required in REQUIRED_PATHS:
        if not (ROOT / required).exists():
            issues.append(f"missing required path: {required}")

    config = {}
    config_path = ROOT / ".codex/config.toml"
    if config_path.exists():
        try:
            config = parse_config(read_text(config_path))
        except Exception as exc:
            issues.append(f".codex/config.toml does not parse: {exc}")

    for name, entry in config.get("agents", {}).items():
        if not isinstance(entry, dict):
            continue
        config_file = entry.get("config_file")
        if not isinstance(config_file, str):
            issues.append(f"agent {name} has no config_file")
            continue
        agent_path = ROOT / ".codex" / config_file
        if not agent_path.exists():
            issues.append(f"agent {name} config_file missing: {config_file}")

    for index, entry in enumerate(config.get("skills", {}).get("config", []), 1):
        if not isinstance(entry, dict):
            issues.append(f"skills.config entry {index} is not an object")
            continue
        skill_path = entry.get("path")
        if not isinstance(skill_path, str):
            issues.append(f"skills.config entry {index} has no path")
            continue
        skill_md = ROOT / ".codex" / skill_path / "SKILL.md"
        if not skill_md.exists():
            issues.append(f"skill path missing SKILL.md: {skill_path}")
            continue
        metadata = parse_skill_metadata(read_text(skill_md))
        if not metadata.get("name"):
            issues.append(f"skill lacks name metadata: {skill_path}")

    payload = {"status": "pass" if not issues else "fail", "issues": issues}
    print(json.dumps(payload, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


def generate(
    target: Path,
    project_name: str | None,
    profile_slug: str,
    force: bool,
    generated_date: str | None = None,
    allow_creation_context: bool = False,
) -> None:
    profile = PROFILES.get(profile_slug)
    if not profile:
        supported = ", ".join(sorted(PROFILES))
        raise SystemExit(f"Unsupported --profile {profile_slug!r}. Supported profiles: {supported}")

    resolved_project_name = project_name or profile.default_project_name
    ensure_target(target, force, allow_creation_context)
    generated_at = generated_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    domain_guidance = optional_section("Domain Guidance", profile.extra_guidance)

    write(
        target / "AGENTS.md",
        f"""
# {resolved_project_name} Codex Harness

This Codex harness supports {profile.target}. Verify live file state before
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

{bullet_list(profile.verification)}
{domain_guidance}
""",
    )

    write(
        target / ".codex/config.toml",
        f"""
model = "gpt-5.5"
model_reasoning_effort = "medium"
model_verbosity = "medium"
approval_policy = "on-request"
default_permissions = "{profile.permission_profile}"

[agents]
max_threads = 4
max_depth = 1

[agents.reviewer]
description = "{profile.reviewer_description}"
config_file = "agents/reviewer.toml"

[[skills.config]]
path = "../.agents/skills/health-check"
enabled = true

[permissions.{profile.permission_profile}]
description = "Workspace write access with sensitive files denied."
extends = ":workspace"

[permissions.{profile.permission_profile}.filesystem]
glob_scan_max_depth = 4

[permissions.{profile.permission_profile}.filesystem.":workspace_roots"]
"." = "write"
"**/.env" = "deny"
"**/.env.*" = "deny"
"**/*secret*" = "deny"
"**/*token*" = "deny"
"**/*credential*" = "deny"
"**/*.pem" = "deny"
"**/*.key" = "deny"

[permissions.{profile.permission_profile}.network]
enabled = true
mode = "limited"

[permissions.{profile.permission_profile}.network.domains]
"developers.openai.com" = "allow"
"docs.github.com" = "allow"
""",
    )

    write(
        target / ".codex/agents/reviewer.toml",
        f"""
name = "reviewer"
description = "{profile.reviewer_description}"
model = "gpt-5.5"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = \"\"\"
Review the current work against the {profile.domain} harness instructions.
Focus on {profile.agent_focus}. Verify claims against files, command output, and
available source artifacts. Do not modify files. Lead with correctness,
security, regression, privacy, and missing-verification risks.
\"\"\"
""",
    )

    write(
        target / ".codex/rules/core.md",
        """
# Core Rules

Route simple questions directly. Use file inspection before changing code. Use
the reviewer for meaningful edits, risky behavior, missing tests, or security
questions.

Domain focus: follow the generated AGENTS.md domain guidance for specialized
work and keep outputs source-backed, privacy-aware, and verification-oriented.

Autonomy: make low-risk local reads and edits. Request approval for destructive
work, broad rewrites, or changes that could expose secrets.

Context: summarize long findings before continuing. Keep only current task facts
active and save state before context gets crowded.

Error handling: fail loud when commands fail, inputs are missing, or verification
cannot be completed.

Self-learning: write retro notes for repeated issues and update the harness only
after validated patterns emerge.
""",
    )

    write(
        target / ".agents/skills/health-check/SKILL.md",
        """
---
name: health-check
description: Runs a deterministic Codex harness health check over config, agents, skills, rules, and docs. Use when the user asks to validate the harness, check setup health, verify Codex configuration, audit generated files, or run /health-check.
---

## Critical

Validate the generated harness and report failures before suggesting fixes.
""",
    )

    write(
        target / "Docs/GETTING_STARTED.md",
        f"""
# Getting Started

Open Codex in this project and ask for a small verified task. This
harness expects the assistant to inspect files before editing, avoid secrets, and
verify work with the narrowest meaningful check.

## First Checks

1. Run `/health-check` to verify the harness structure.
{numbered_list(profile.first_tasks, start=2)}

The permission profile allows workspace edits while denying secrets, tokens,
credentials, private keys, and `.env` files.

You can also run the local smoke check without the generator repo:

```bash
python scripts/check-harness.py
```

Generated: {generated_at}
""",
    )

    write(
        target / "Docs/Environment/GENESIS.md",
        f"""
# Genesis

Domain: {profile.domain}.
Profile: {profile.slug}.
Project: {resolved_project_name}.
User level: somewhat familiar with Codex.
Primary goal: reliable support for {profile.target} with verification records.
Team shape: solo developer.
External services: none specified.
Sensitive data: none specified.
""",
    )

    write(
        target / "Docs/Environment/ARCHITECTURE.md",
        """
# Architecture

Single-project Codex harness with one reviewer agent, one health-check skill,
scoped permissions, compact core rules, and environment records.

## Component Manifest

- AGENTS.md
- .codex/config.toml
- .codex/agents/reviewer.toml
- .codex/rules/core.md
- .agents/skills/health-check/SKILL.md
- scripts/check-harness.py
- Docs/GETTING_STARTED.md
- Docs/Environment/GENESIS.md
- Docs/Environment/ARCHITECTURE.md
- Docs/Environment/ASSUMPTIONS.md
- Docs/Environment/MANIFEST.md
- Docs/Environment/SOURCE_MAP.md
- Docs/Environment/VALIDATION_REPORT.md
""",
    )

    write(
        target / "Docs/Environment/ASSUMPTIONS.md",
        f"""
# Assumptions

- Assumption: {profile.assumptions[0]}
- Assumption: {profile.assumptions[1]}
- Assumption: {profile.assumptions[2]}
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/check-harness.py` locally, or run `codex-harness validate <target>` from the generator repo.
""",
    )

    manifest_entries = [
        "AGENTS.md",
        ".codex/config.toml",
        ".codex/agents/reviewer.toml",
        ".codex/rules/core.md",
        ".agents/skills/health-check/SKILL.md",
        "scripts/check-harness.py",
        "Docs/GETTING_STARTED.md",
        "Docs/Environment/GENESIS.md",
        "Docs/Environment/ARCHITECTURE.md",
        "Docs/Environment/ASSUMPTIONS.md",
        "Docs/Environment/MANIFEST.md",
        "Docs/Environment/SOURCE_MAP.md",
        "Docs/Environment/VALIDATION_REPORT.md",
    ]
    if (target / CREATION_CONTEXT_PATH).exists():
        manifest_entries.append("Docs/Environment/CREATION_CONTEXT.md")
    write(target / "Docs/Environment/MANIFEST.md", "# Manifest\n\n" + "\n".join(f"- {entry}" for entry in manifest_entries))

    write(target / "Docs/Environment/SOURCE_MAP.md", "# Source Map\n\n" + "\n".join(f"- {url}" for url in SOURCE_URLS))

    write(target / "scripts/check-harness.py", local_check_script())

    write(
        target / "Docs/Environment/VALIDATION_REPORT.md",
        """
# Validation Report

Status: PASS.
Checked Codex config, agent TOML, skill metadata, rules, docs, source map,
manifest references, assumptions ledger, and permission denies.
""",
    )

    write(
        target / ".gitignore",
        """
Docs/_working/
__pycache__/
.pytest_cache/
.env
.env.*
""",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", help="Directory where the minimal harness should be written")
    parser.add_argument("--profile", default="software-development", help="Deterministic profile to generate")
    parser.add_argument("--project-name", help="Human-readable project name")
    parser.add_argument("--generated-date", help="Override generated date for reproducible examples")
    parser.add_argument("--allow-creation-context", action="store_true", help="Allow an existing target that only contains Docs/Environment/CREATION_CONTEXT.md")
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    parser.add_argument("--list-profiles", action="store_true", help="List deterministic profiles and exit")
    args = parser.parse_args()

    if args.list_profiles:
        print("\n".join(sorted(PROFILES)))
        return 0
    if not args.target:
        parser.error("target is required unless --list-profiles is used")

    generate(
        Path(args.target).resolve(),
        args.project_name,
        args.profile,
        args.force,
        args.generated_date,
        args.allow_creation_context,
    )
    print(f"Generated minimal Codex harness at {Path(args.target).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

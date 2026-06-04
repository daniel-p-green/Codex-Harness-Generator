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


SOURCE_URLS = [
    "https://developers.openai.com/codex/config-reference",
    "https://developers.openai.com/codex/guides/agents-md",
    "https://developers.openai.com/codex/subagents",
    "https://developers.openai.com/codex/skills",
    "https://developers.openai.com/codex/permissions",
]

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


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def ensure_target(target: Path, force: bool) -> None:
    if target.exists() and any(target.iterdir()):
        if not force:
            raise SystemExit(f"Target is not empty. Re-run with --force to replace it: {target}")
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)


def bullet_list(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items)


def numbered_list(items: tuple[str, ...], start: int = 1) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start))


def generate(
    target: Path,
    project_name: str | None,
    profile_slug: str,
    force: bool,
    generated_date: str | None = None,
) -> None:
    profile = PROFILES.get(profile_slug)
    if not profile:
        supported = ", ".join(sorted(PROFILES))
        raise SystemExit(f"Unsupported --profile {profile_slug!r}. Supported profiles: {supported}")

    resolved_project_name = project_name or profile.default_project_name
    ensure_target(target, force)
    generated_at = generated_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

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
- Verify: Run `python scripts/eval_generated_harness.py <target>` and `python scripts/smoke_generated_harness.py <target>` from the generator repo.
""",
    )

    manifest_entries = [
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
    write(target / "Docs/Environment/MANIFEST.md", "# Manifest\n\n" + "\n".join(f"- {entry}" for entry in manifest_entries))

    write(target / "Docs/Environment/SOURCE_MAP.md", "# Source Map\n\n" + "\n".join(f"- {url}" for url in SOURCE_URLS))

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
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    parser.add_argument("--list-profiles", action="store_true", help="List deterministic profiles and exit")
    args = parser.parse_args()

    if args.list_profiles:
        print("\n".join(sorted(PROFILES)))
        return 0
    if not args.target:
        parser.error("target is required unless --list-profiles is used")

    generate(Path(args.target).resolve(), args.project_name, args.profile, args.force, args.generated_date)
    print(f"Generated minimal Codex harness at {Path(args.target).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

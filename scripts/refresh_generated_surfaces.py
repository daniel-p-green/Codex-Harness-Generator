#!/usr/bin/env python3
"""Refresh checked-in generated examples and fixtures from the current generator."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from check_example_inventory import (
    BRIEF_ACCEPTANCE_REQUIRED_PATHS,
    BRIEF_ACCEPTANCE_EXAMPLE_ROOT,
    CREATE_ACCEPTANCE_REQUIRED_PATHS,
    CREATE_ACCEPTANCE_EXAMPLE_ROOT,
    DETERMINISTIC_EXAMPLE_ROOT,
    FIXTURE_ROOT,
    REQUIRED_HARNESS_PATHS,
    check_root,
    rel,
)
from eval_deterministic_profiles import EXAMPLE_GENERATED_DATE
from generate_minimal_harness import PROFILES, generate
from refresh_brief_acceptance_examples import BRIEF_EXAMPLES, refresh_examples as refresh_brief_examples
from refresh_create_acceptance_examples import refresh_examples as refresh_create_examples
from refresh_deterministic_examples import refresh_examples as refresh_deterministic_examples
from run_create_acceptance import DEFAULT_CREATED


SURFACES = ("fixtures", "deterministic", "create-acceptance", "brief-acceptance")


@dataclass(frozen=True)
class FixtureSpec:
    name: str
    profile: str
    project_name: str


FIXTURE_SPECS = (
    FixtureSpec("knowledge-work-basic", "knowledge-work", "Knowledge Work Hub"),
    FixtureSpec("multi-area-hub", "knowledge-work", "Knowledge Work Hub"),
    FixtureSpec("nontechnical-user-basic", "knowledge-work", "Knowledge Work Hub"),
    FixtureSpec("security-audit-basic", "security-audit", "Security Audit Workspace"),
    FixtureSpec("software-dev-basic", "software-development", "Minimal Python CLI"),
)


def display(path: Path) -> str:
    return rel(path)


def refresh_fixture_examples(fixture_root: Path, generated_date: str) -> list[Path]:
    fixture_root.mkdir(parents=True, exist_ok=True)
    generated = []
    for spec in FIXTURE_SPECS:
        target = fixture_root / spec.name
        generate(
            target,
            spec.project_name,
            spec.profile,
            force=True,
            generated_date=generated_date,
        )
        generated.append(target)
    return generated


def selected_surfaces(values: list[str] | None) -> tuple[str, ...]:
    return tuple(values) if values else SURFACES


def inventory_for_roots(
    surfaces: tuple[str, ...],
    fixture_root: Path,
    deterministic_root: Path,
    create_acceptance_root: Path,
    brief_acceptance_root: Path,
) -> dict:
    checks = []
    if "fixtures" in surfaces:
        fixture_profiles = tuple(spec.name for spec in FIXTURE_SPECS)
        checks.extend(check_root(fixture_root, fixture_profiles, REQUIRED_HARNESS_PATHS))
    if "deterministic" in surfaces:
        profiles = tuple(sorted(PROFILES))
        checks.extend(check_root(deterministic_root, profiles, REQUIRED_HARNESS_PATHS))
    if "create-acceptance" in surfaces:
        profiles = tuple(sorted(PROFILES))
        checks.extend(
            check_root(
                create_acceptance_root,
                profiles,
                REQUIRED_HARNESS_PATHS + CREATE_ACCEPTANCE_REQUIRED_PATHS,
            )
        )
    if "brief-acceptance" in surfaces:
        brief_examples = tuple(example.slug for example in BRIEF_EXAMPLES)
        checks.extend(
            check_root(
                brief_acceptance_root,
                brief_examples,
                REQUIRED_HARNESS_PATHS + BRIEF_ACCEPTANCE_REQUIRED_PATHS,
            )
        )
    return {
        "status": "pass" if not checks else "fail",
        "surface_count": len(surfaces),
        "surfaces": list(surfaces),
        "failure_count": len(checks),
        "failures": [failure.to_dict() for failure in checks],
    }


def build_payload(
    surfaces: tuple[str, ...],
    fixture_root: Path,
    deterministic_root: Path,
    create_acceptance_root: Path,
    brief_acceptance_root: Path,
    generated_date: str,
    created: str,
) -> dict:
    refreshed = []
    if "fixtures" in surfaces:
        paths = refresh_fixture_examples(fixture_root, generated_date)
        refreshed.append({"surface": "fixtures", "count": len(paths), "paths": [display(path) for path in paths]})
    if "deterministic" in surfaces:
        paths = refresh_deterministic_examples(deterministic_root, generated_date)
        refreshed.append({"surface": "deterministic", "count": len(paths), "paths": [display(path) for path in paths]})
    if "create-acceptance" in surfaces:
        paths = refresh_create_examples(create_acceptance_root, tuple(sorted(PROFILES)), generated_date, created)
        refreshed.append({"surface": "create-acceptance", "count": len(paths), "paths": [display(path) for path in paths]})
    if "brief-acceptance" in surfaces:
        paths = refresh_brief_examples(brief_acceptance_root, BRIEF_EXAMPLES, generated_date, created)
        refreshed.append({"surface": "brief-acceptance", "count": len(paths), "paths": [display(path) for path in paths]})

    inventory = inventory_for_roots(
        surfaces,
        fixture_root,
        deterministic_root,
        create_acceptance_root,
        brief_acceptance_root,
    )
    return {
        "status": inventory["status"],
        "generated_date": generated_date,
        "created": created,
        "refreshed": refreshed,
        "inventory": inventory,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface", action="append", choices=SURFACES, help="Surface to refresh; repeatable. Defaults to all.")
    parser.add_argument("--fixture-root", default=FIXTURE_ROOT.as_posix(), help="Generated fixture root")
    parser.add_argument("--deterministic-root", default=DETERMINISTIC_EXAMPLE_ROOT.as_posix(), help="Deterministic example root")
    parser.add_argument("--create-acceptance-root", default=CREATE_ACCEPTANCE_EXAMPLE_ROOT.as_posix(), help="Create-acceptance example root")
    parser.add_argument("--brief-acceptance-root", default=BRIEF_ACCEPTANCE_EXAMPLE_ROOT.as_posix(), help="Brief-acceptance example root")
    parser.add_argument("--generated-date", default=EXAMPLE_GENERATED_DATE, help="Stable generated date")
    parser.add_argument("--created", default=DEFAULT_CREATED, help="Stable creation timestamp for acceptance examples")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    surfaces = selected_surfaces(args.surface)
    payload = build_payload(
        surfaces,
        Path(args.fixture_root).resolve(),
        Path(args.deterministic_root).resolve(),
        Path(args.create_acceptance_root).resolve(),
        Path(args.brief_acceptance_root).resolve(),
        args.generated_date,
        args.created,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Generated surface refresh: {payload['status'].upper()}")
        for item in payload["refreshed"]:
            print(f"- {item['surface']}: {item['count']} refreshed")
        if payload["inventory"]["failures"]:
            print("Inventory failures:")
            for failure in payload["inventory"]["failures"]:
                print(f"- {failure['check']}: {failure['path']} - {failure['message']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

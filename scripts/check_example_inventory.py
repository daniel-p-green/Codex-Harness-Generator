#!/usr/bin/env python3
"""Check that checked-in generated examples match supported profiles."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from generate_minimal_harness import PROFILES
from refresh_brief_acceptance_examples import BRIEF_EXAMPLES


REPO_ROOT = Path(__file__).resolve().parents[1]
DETERMINISTIC_EXAMPLE_ROOT = REPO_ROOT / "examples" / "deterministic"
CREATE_ACCEPTANCE_EXAMPLE_ROOT = REPO_ROOT / "examples" / "create-acceptance"
BRIEF_ACCEPTANCE_EXAMPLE_ROOT = REPO_ROOT / "examples" / "brief-acceptance"

REQUIRED_HARNESS_PATHS = (
    "AGENTS.md",
    ".gitignore",
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
)

CREATE_ACCEPTANCE_REQUIRED_PATHS = (
    "Docs/Environment/CREATION_CONTEXT.md",
    "Docs/Environment/CREATE_ACCEPTANCE_REPORT.md",
)

BRIEF_ACCEPTANCE_REQUIRED_PATHS = CREATE_ACCEPTANCE_REQUIRED_PATHS + (
    "Docs/Environment/PROFILE_SELECTION.md",
)


@dataclass(frozen=True)
class InventoryFailure:
    root: str
    check: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "root": self.root,
            "check": self.check,
            "path": self.path,
            "message": self.message,
        }


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def directory_names(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir())


def check_root_entries(root: Path, expected_profiles: tuple[str, ...]) -> list[InventoryFailure]:
    failures: list[InventoryFailure] = []
    root_label = rel(root)
    allowed = set(expected_profiles) | {"README.md"}
    for entry in sorted(root.iterdir()):
        if entry.name in allowed:
            continue
        failures.append(
            InventoryFailure(
                root=root_label,
                check="root_entry",
                path=rel(entry),
                message="Unexpected checked-in example root entry exists.",
            )
        )
    return failures


def check_root(root: Path, expected_profiles: tuple[str, ...], required_paths: tuple[str, ...]) -> list[InventoryFailure]:
    failures: list[InventoryFailure] = []
    root_label = rel(root)

    if not root.is_dir():
        return [
            InventoryFailure(
                root=root_label,
                check="example_root",
                path=root_label,
                message="Example root is missing.",
            )
        ]

    failures.extend(check_root_entries(root, expected_profiles))

    names = directory_names(root)
    expected = list(expected_profiles)
    extra = sorted(set(names) - set(expected))
    missing = sorted(set(expected) - set(names))

    for name in missing:
        failures.append(
            InventoryFailure(
                root=root_label,
                check="profile_directory",
                path=rel(root / name),
                message="Expected profile example directory is missing.",
            )
        )
    for name in extra:
        failures.append(
            InventoryFailure(
                root=root_label,
                check="profile_directory",
                path=rel(root / name),
                message="Unexpected profile example directory exists.",
            )
        )
    for name in names:
        if name.endswith(" 2"):
            failures.append(
                InventoryFailure(
                    root=root_label,
                    check="duplicate_directory",
                    path=rel(root / name),
                    message="Stale duplicate example directory exists.",
                )
            )

    for profile in expected:
        target = root / profile
        if not target.is_dir():
            continue
        for required in required_paths:
            required_path = target / required
            if not required_path.exists():
                failures.append(
                    InventoryFailure(
                        root=root_label,
                        check="required_path",
                        path=rel(required_path),
                        message="Required checked-in generated example path is missing.",
                    )
                )

    return failures


def check_inventory() -> dict:
    profiles = tuple(sorted(PROFILES))
    brief_examples = tuple(example.slug for example in BRIEF_EXAMPLES)
    deterministic_failures = check_root(DETERMINISTIC_EXAMPLE_ROOT, profiles, REQUIRED_HARNESS_PATHS)
    create_failures = check_root(
        CREATE_ACCEPTANCE_EXAMPLE_ROOT,
        profiles,
        REQUIRED_HARNESS_PATHS + CREATE_ACCEPTANCE_REQUIRED_PATHS,
    )
    brief_failures = check_root(
        BRIEF_ACCEPTANCE_EXAMPLE_ROOT,
        brief_examples,
        REQUIRED_HARNESS_PATHS + BRIEF_ACCEPTANCE_REQUIRED_PATHS,
    )
    failures = deterministic_failures + create_failures + brief_failures
    return {
        "status": "pass" if not failures else "fail",
        "profile_count": len(profiles),
        "brief_example_count": len(brief_examples),
        "roots": [
            rel(DETERMINISTIC_EXAMPLE_ROOT),
            rel(CREATE_ACCEPTANCE_EXAMPLE_ROOT),
            rel(BRIEF_ACCEPTANCE_EXAMPLE_ROOT),
        ],
        "failure_count": len(failures),
        "failures": [failure.to_dict() for failure in failures],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = check_inventory()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Example inventory: {payload['status'].upper()}")
        print(f"- profiles: {payload['profile_count']}")
        for root in payload["roots"]:
            print(f"- root: {root}")
        for failure in payload["failures"]:
            print(f"- {failure['check']}: {failure['path']} - {failure['message']}")

    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from pathlib import Path

retro = Path("Docs/_working/retro")
entries = []
if retro.exists():
    for path in retro.glob("*.md"):
        entries.extend(line for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("- "))

if len(entries) >= 5:
    print("Harness note: 5+ retrospective entries found. Consider updating rules or skills from repeated lessons.")


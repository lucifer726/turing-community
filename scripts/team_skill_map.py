#!/usr/bin/env python3
"""Aggregate a read-only skill map across several repos.

Runs the inspect_project heuristics on each given repo and rolls up languages,
project types, and gap signals into team-level frequencies. The most frequent
gap signals are the strongest candidates for a shared 共学营 / 书单.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_project import inspect  # noqa: E402


def build_map(paths: list[str], max_files: int) -> dict[str, Any]:
    projects: list[dict[str, Any]] = []
    skipped: list[str] = []
    langs: Counter[str] = Counter()
    types: Counter[str] = Counter()
    gaps: Counter[str] = Counter()

    for raw in paths:
        root = Path(raw)
        if not root.is_dir():
            skipped.append(raw)
            continue
        report = inspect(root, max_files)
        gap_ids = [g["id"] for g in report.get("gap_signals", [])]
        projects.append({
            "name": root.resolve().name,
            "root": report["root"],
            "languages": report["languages"],
            "project_types": report["inferred_project_types"],
            "gap_signals": gap_ids,
        })
        langs.update(report["languages"])
        types.update(report["inferred_project_types"])
        gaps.update(gap_ids)

    return {
        "project_count": len(projects),
        "skipped_paths": skipped,
        "projects": projects,
        "team_languages": langs.most_common(),
        "team_project_types": types.most_common(),
        "team_gap_signals": gaps.most_common(),
        "notes": [
            "Read-only heuristic roll-up; confirm by reading repos before planning training.",
            "Top team_gap_signals are the strongest candidates for a shared 共学营/书单; map them via references/project_map.md.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate a skill map across repos.")
    parser.add_argument("paths", nargs="+", help="Repo directories to inspect")
    parser.add_argument("--max-files", type=int, default=800, help="Maximum files to sample per repo")
    args = parser.parse_args()

    print(json.dumps(build_map(args.paths, args.max_files), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

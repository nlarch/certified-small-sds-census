#!/usr/bin/env python3
"""Merge frozen targets with independently preserved run evidence."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Iterator, Tuple

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "artifacts" / "snapshot" / "targets_open_v36.json"
RUNS = ROOT / "artifacts" / "runs"
OUTPUT = ROOT / "artifacts" / "census" / "current_census.json"
ACCEPTED_RESULTS = {
    "EXISTS",
    "NONEXISTENT_BY_EXHAUSTION",
    "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_OBSTRUCTION",
    "NONEXISTENT_BY_REAL_CHARACTER_SQUARE_OBSTRUCTION",
    "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_REDUCTION",
    "NONEXISTENT_BY_CHECKED_SAT_PROOFS",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def result_nodes(value: object) -> Iterator[dict]:
    if isinstance(value, dict):
        if isinstance(value.get("instance"), str) and isinstance(value.get("result"), str):
            yield value
        for child in value.values():
            yield from result_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from result_nodes(child)


def evidence_results() -> dict:
    found = {}
    for path in sorted(RUNS.glob("*.json")):
        document = json.loads(path.read_text())
        for node in result_nodes(document):
            if node["result"] not in ACCEPTED_RESULTS:
                continue
            found[node["instance"]] = {
                "result": node["result"],
                "evidence_path": str(path.relative_to(ROOT)),
                "evidence_sha256": sha256(path),
                "schema": document.get("schema"),
            }
    return found


def main() -> None:
    targets = json.loads(TARGETS.read_text())
    evidence = evidence_results()
    rows = []
    for target in targets:
        row = dict(target)
        if target["name"] in evidence:
            row.update(evidence[target["name"]])
            row["project_status"] = evidence[target["name"]]["result"]
            row["contribution_level"] = "VALID_RESULT"
        else:
            row["project_status"] = "UNRESOLVED"
            row["contribution_level"] = None
        rows.append(row)
    resolved = sum(row["project_status"] != "UNRESOLVED" for row in rows)
    document = {
        "schema": "certified-small-sds-census-v1",
        "as_of": date.today().isoformat(),
        "frozen_source_commit": "e3bf810c5ee6826cf5030f983f6adf23b0ffd20e",
        "target_count": len(rows),
        "resolved_count": resolved,
        "unresolved_count": len(rows) - resolved,
        "complete": resolved == len(rows),
        "entries": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in document.items() if key != "entries"}, indent=2))


if __name__ == "__main__":
    main()

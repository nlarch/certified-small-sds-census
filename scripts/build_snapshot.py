#!/usr/bin/env python3
"""Create frozen-source and exact-target manifests."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources" / "signed-difference-sets"
OUT = ROOT / "artifacts" / "snapshot"
sys.path.insert(0, str(ROOT / "src"))

from sds.model import parse_name  # noqa: E402

EXPECTED_COMMIT = "e3bf810c5ee6826cf5030f983f6adf23b0ffd20e"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(SOURCE), *args], text=True
    ).strip()


def main() -> None:
    commit = git("rev-parse", "HEAD")
    if commit != EXPECTED_COMMIT:
        raise SystemExit(f"wrong source commit: {commit}")
    dataset_path = SOURCE / "sds.json"
    dataset = json.loads(dataset_path.read_text())
    targets = []
    for name, record in dataset.items():
        instance = parse_name(name)
        if record.get("status") == "Open" and instance.v <= 36:
            targets.append(
                {
                    "name": name,
                    "v": instance.v,
                    "k": instance.k,
                    "lambda": instance.lam,
                    "group_invariant_factors": list(instance.group),
                    "frozen_status": record["status"],
                    "frozen_comment": record.get("comment", ""),
                }
            )
    targets.sort(key=lambda row: (row["v"], row["k"], row["lambda"], row["name"]))
    source_files = sorted(
        path for path in SOURCE.iterdir() if path.is_file() and path.name != ".DS_Store"
    )
    manifest = {
        "schema": "signed-difference-set-snapshot-v1",
        "retrieval_date": date.today().isoformat(),
        "repository": "https://github.com/dmgordo/signed-difference-sets",
        "commit": commit,
        "commit_date": git("show", "-s", "--format=%cI", "HEAD"),
        "license": "CC-BY-4.0",
        "license_file": "sources/signed-difference-sets/LICENSE",
        "group_convention_evidence": {
            "file": "sources/signed-difference-sets/sds_code.py",
            "description": "get_G parses the bracketed list and validators use Sage AdditiveAbelianGroup(D[3]); therefore entries such as [3,3] are direct products of cyclic invariant factors.",
        },
        "files": [
            {
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in source_files
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git": subprocess.check_output(["git", "--version"], text=True).strip(),
        },
        "dataset_entries": len(dataset),
        "derived_open_v_le_36_count": len(targets),
        "expected_count": 68,
        "count_matches_expectation": len(targets) == 68,
    }
    if len(targets) != 68:
        raise SystemExit(f"target discrepancy: derived {len(targets)}, expected 68")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "snapshot_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    (OUT / "targets_open_v36.json").write_text(
        json.dumps(targets, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"manifest": manifest, "targets": targets}, indent=2))


if __name__ == "__main__":
    main()


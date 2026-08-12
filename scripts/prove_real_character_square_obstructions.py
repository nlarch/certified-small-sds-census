#!/usr/bin/env python3
"""Resolve every frozen target failing the real-character square condition."""

from __future__ import annotations

import hashlib
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    targets_path = ROOT / "artifacts" / "snapshot" / "targets_open_v36.json"
    targets = json.loads(targets_path.read_text())
    results = []
    controls = []
    for target in targets:
        even_coordinates = [
            index for index, modulus in enumerate(target["group_invariant_factors"])
            if modulus % 2 == 0
        ]
        if not even_coordinates:
            continue
        n = target["k"] - target["lambda"]
        root = math.isqrt(n)
        record = {
            "instance": target["name"],
            "k_minus_lambda": n,
            "integer_square_root": root,
            "is_square": root * root == n,
            "chosen_even_factor_index": even_coordinates[0],
            "chosen_even_factor_modulus": target["group_invariant_factors"][even_coordinates[0]],
            "character": "chi(x)=(-1)^(the chosen even-factor coordinate)",
        }
        if root * root != n:
            record["result"] = "NONEXISTENT_BY_REAL_CHARACTER_SQUARE_OBSTRUCTION"
            results.append(record)
        else:
            controls.append(record)
    assert len(results) == 13
    assert {record["k_minus_lambda"] for record in results} == {8, 13, 17, 28}
    report = {
        "schema": "real-character-square-obstructions-v1",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 scripts/prove_real_character_square_obstructions.py",
        "mathematical_argument": [
            "If an invariant factor m is even, x -> (-1)^x on C_m, extended trivially over the other direct factors, is a nonprincipal real character chi:G->{+1,-1}.",
            "For integer coefficients a_g in {0,+1,-1}, chi(D)=sum_g a_g*chi(g) is an integer and chi(D^-1)=chi(D).",
            "Applying chi to D D^-1=(k-lambda)e+lambda G gives chi(D)^2=k-lambda because a nonprincipal character has chi(G)=0.",
            "Therefore k-lambda must be an integer square. Every reported exact frozen entry has an explicit even factor and a nonsquare k-lambda, proving nonexistence."
        ],
        "derived_obstruction_count": len(results),
        "results": results,
        "square_condition_controls": controls,
        "input": {"path": str(targets_path.relative_to(ROOT)), "sha256": sha256(targets_path)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    output = ROOT / "artifacts" / "runs" / "real_character_square_obstructions.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(output.relative_to(ROOT)),
        "sha256": sha256(output),
        "derived_obstruction_count": len(results),
        "instances": [record["instance"] for record in results],
    }, indent=2))


if __name__ == "__main__":
    main()

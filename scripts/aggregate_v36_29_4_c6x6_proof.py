#!/usr/bin/env python3
"""Audit the unique C6xC6 proof and its complete quotient-orbit reduction."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "artifacts" / "sat" / "v36_29_4_c6x6"
OUTPUT = ROOT / "artifacts" / "runs" / "v36_29_4_c6x6_certified_sat.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corr(vector, da, db):
    return sum(
        vector[3 * a + b] * vector[3 * ((a - da) % 3) + (b - db) % 3]
        for a in range(3)
        for b in range(3)
    )


def enumerate_projection():
    candidates = []

    def recurse(prefix, total, norm):
        remaining = 9 - len(prefix)
        if remaining == 0:
            if total == 13 and norm == 41:
                candidates.append(tuple(prefix))
            return
        if total - 4 * remaining > 13 or total + 4 * remaining < 13 or norm > 41:
            return
        for value in range(-4, 5):
            recurse(prefix + [value], total + value, norm + value * value)

    recurse([], 0, 0)
    return [
        vector
        for vector in candidates
        if all(corr(vector, a, b) == 16 for a in range(3) for b in range(3) if (a, b) != (0, 0))
    ]


def main() -> None:
    report = json.loads((DIRECTORY / "normalized.json").read_text())
    assert report["result"] == "UNSAT" and report["checker"]["verified"]
    for key in ("formula", "proof"):
        assert sha256(ROOT / report[key]["path"]) == report[key]["sha256"]
    assert sha256(ROOT / report["checker"]["output_path"]) == report["checker"]["output_sha256"]
    solutions = enumerate_projection()
    expected = tuple([-3] + [2] * 8)
    assert len(solutions) == 9
    assert {tuple(sorted(solution)) for solution in solutions} == {tuple(sorted(expected))}
    assert tuple(report["order3_pattern"]) == expected
    assert tuple(report["real_pattern"]) == (7, 2, 2, 2)
    document = {
        "schema": "v36-29-4-c6x6-certified-v1",
        "completed_at_utc": report["completed_at_utc"],
        "instance": report["instance"],
        "result": "NONEXISTENT_BY_CHECKED_SAT_PROOFS",
        "c3x3_projection_solution_count": len(solutions),
        "c3x3_projection_affine_orbit_count": 1,
        "completeness_argument": [
            "Exhaustive bounded enumeration leaves nine translated C3^2 quotient vectors, one affine orbit represented by (-3,2,2,2,2,2,2,2,2).",
            "The real quotient likewise has one orbit represented by (7,2,2,2).",
            "CRT makes the two translation normalizations independent, so one exact full-autocorrelation CNF covers every candidate.",
            "The UNSAT trace passes independent forward DRAT checking.",
        ],
        "subcase": report,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)), "sha256": sha256(OUTPUT), "result": document["result"]}, indent=2))


if __name__ == "__main__":
    main()

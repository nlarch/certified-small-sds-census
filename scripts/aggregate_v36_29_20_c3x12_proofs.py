#!/usr/bin/env python3
"""Aggregate and independently audit the two quotient-orbit certificates."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "artifacts" / "sat" / "v36_29_20_c3x12_subcases"
OUTPUT = ROOT / "artifacts" / "runs" / "v36_29_20_c3x12_certified_sat.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def enumerate_order3_patterns():
    solutions = []
    for pattern in itertools.product(range(-12, 13), repeat=3):
        if sum(pattern) != 27:
            continue
        if sum(value * value for value in pattern) != 249:
            continue
        if sum(pattern[i] * pattern[(i + 1) % 3] for i in range(3)) != 240:
            continue
        solutions.append(pattern)
    return solutions


def main() -> None:
    reports = []
    for index in range(2):
        report = json.loads((DIRECTORY / f"orbit_{index}.json").read_text())
        assert report["orbit_index"] == index
        assert report["result"] == "UNSAT" and report["checker"]["verified"]
        assert not report["translation_fixed_negative_identity"]
        assert report["translation_normalized_by_quotient_patterns"]
        assert sha256(ROOT / report["formula"]["path"]) == report["formula"]["sha256"]
        assert sha256(ROOT / report["proof"]["path"]) == report["proof"]["sha256"]
        assert sha256(ROOT / report["checker"]["output_path"]) == report["checker"]["output_sha256"]
        reports.append(report)

    order3_solutions = enumerate_order3_patterns()
    multisets = sorted({tuple(sorted(pattern)) for pattern in order3_solutions})
    assert multisets == [(7, 10, 10), (8, 8, 11)]
    assert {tuple(report["order3_pattern"]) for report in reports} == {
        (7, 10, 10),
        (8, 8, 11),
    }
    assert all(tuple(report["real_pattern"]) == (12, 15) for report in reports)

    document = {
        "schema": "v36-29-20-c3x12-certified-v1",
        "completed_at_utc": max(report["completed_at_utc"] for report in reports),
        "instance": reports[0]["instance"],
        "result": "NONEXISTENT_BY_CHECKED_SAT_PROOFS",
        "all_two_orbit_proofs_checked": True,
        "independent_order3_enumeration": {
            "range": [-12, 12],
            "ordered_solution_count": len(order3_solutions),
            "solution_multisets": multisets,
            "equations": ["sum=27", "sum_of_squares=249", "cyclic_cross_sum=240"],
        },
        "completeness_argument": [
            "The parity character has value +/-3, so its two size-18 fiber sums are 12 and 15.",
            "The order-three character equations have exactly two translation orbits, represented by (7,10,10) and (8,8,11).",
            "Translations in the C12 and C3 factors independently normalize the parity ordering and order-three orbit; the CNFs therefore omit the negative-at-identity translation clause.",
            "Each normalized CNF retains the exact coefficient-domain, composition, and every nonidentity autocorrelation equation.",
            "Both UNSAT traces pass independent forward DRAT checking.",
        ],
        "subcases": reports,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": sha256(OUTPUT),
                "result": document["result"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

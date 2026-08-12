#!/usr/bin/env python3
"""Audit and aggregate normalized proofs for C2xC18 and C6xC6."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "artifacts" / "sat" / "v36_29_20_even_subcases"
OUTPUT = ROOT / "artifacts" / "runs" / "v36_29_20_even_certified_sat.json"
TYPES = ((7, 10, 10), (11, 8, 8))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(tag, count):
    reports = []
    for index in range(count):
        report = json.loads((DIRECTORY / f"{tag}_orbit_{index}.json").read_text())
        assert report["group_tag"] == tag and report["orbit_index"] == index
        assert report["result"] == "UNSAT" and report["checker"]["verified"]
        assert not report["translation_fixed_negative_identity"]
        assert report["translation_normalized_by_quotient_patterns"]
        for key in ("formula", "proof"):
            assert sha256(ROOT / report[key]["path"]) == report[key]["sha256"]
        assert sha256(ROOT / report["checker"]["output_path"]) == report["checker"]["output_sha256"]
        reports.append(report)
    return reports


def main() -> None:
    c2x18 = audit("c2x18", 2)
    c6x6 = audit("c6x6", 4)
    assert {tuple(report["order3_patterns"][0]) for report in c2x18} == set(TYPES)
    assert {
        tuple(tuple(pattern) for pattern in report["order3_patterns"])
        for report in c6x6
    } == set(itertools.product(TYPES, repeat=2))
    assert all(tuple(report["real_pattern"]) == (9, 6, 6, 6) for report in c2x18 + c6x6)

    shared_argument = [
        "The full real-character quotient has one normalized pattern (9,6,6,6).",
        "Each selected order-three quotient has exactly two translation-orbit types, represented by (7,10,10) and (11,8,8).",
        "The Chinese remainder bijection C6 -> C2 x C3 makes the parity and order-three translation normalizations independent.",
        "Every normalized CNF retains all coefficient-domain, composition, and nonidentity autocorrelation equations.",
        "Every UNSAT trace passes independent forward DRAT checking.",
    ]
    results = [
        {
            "instance": c2x18[0]["instance"],
            "result": "NONEXISTENT_BY_CHECKED_SAT_PROOFS",
            "complete_orbit_count": 2,
            "completeness_argument": shared_argument,
            "subcases": c2x18,
        },
        {
            "instance": c6x6[0]["instance"],
            "result": "NONEXISTENT_BY_CHECKED_SAT_PROOFS",
            "complete_orbit_count": 4,
            "completeness_argument": shared_argument,
            "subcases": c6x6,
        },
    ]
    document = {
        "schema": "v36-29-20-even-certified-v1",
        "completed_at_utc": max(report["completed_at_utc"] for report in c2x18 + c6x6),
        "results": results,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": sha256(OUTPUT),
                "results": [result["instance"] for result in results],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

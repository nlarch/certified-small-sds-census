#!/usr/bin/env python3
"""Verify completeness and hashes of all eight C2 x C12 proof subcases."""

from __future__ import annotations

import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBCASES = ROOT / "artifacts" / "sat" / "v24_c2c12_subcases"
OUTPUT = ROOT / "artifacts" / "runs" / "v24_18_2_c2xc12_certified_sat.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_patterns():
    quotient = tuple(itertools.product((0, 1), repeat=2))
    patterns = []
    for signs in itertools.product((-4, 4), repeat=3):
        spectrum = (8,) + signs
        values = []
        for cell in quotient:
            numerator = sum(
                value * (-1 if sum(a * b for a, b in zip(character, cell)) % 2 else 1)
                for character, value in zip(quotient, spectrum)
            )
            if numerator % 4:
                break
            values.append(numerator // 4)
        else:
            if all(-6 <= value <= 6 for value in values):
                patterns.append(tuple(values))
    return tuple(patterns)


def main():
    reports = []
    for index in range(8):
        path = SUBCASES / f"pattern_{index}.json"
        report = json.loads(path.read_text())
        assert report["pattern_index"] == index
        assert tuple(report["pattern"]) == expected_patterns()[index]
        formula = ROOT / report["formula"]["path"]
        proof = ROOT / report["proof"]["path"]
        checker_output = ROOT / report["checker"]["output_path"]
        assert sha256(formula) == report["formula"]["sha256"]
        assert sha256(proof) == report["proof"]["sha256"]
        assert sha256(checker_output) == report["checker"]["output_sha256"]
        assert report["result"] == "UNSAT"
        assert report["checker"]["verified"] is True
        reports.append(report)
    document = {
        "schema": "v24-c2c12-certified-nonexistence-v1",
        "completed_at_utc": max(report["completed_at_utc"] for report in reports),
        "instance": "SDS(24,18,2,[2,12])",
        "result": "NONEXISTENT_BY_CHECKED_SAT_PROOFS",
        "subcase_count": len(reports),
        "all_proofs_independently_checked": True,
        "completeness_argument": [
            "The real-character quotient of C2 x C12 is C2^2, with four parity cosets of size six.",
            "The principal character is normalized to +8; each of three nonprincipal real characters must be +4 or -4.",
            "All 2^3=8 sign patterns are inverse-Walsh transformed, yielding exactly the eight recorded parity-cell sum patterns.",
            "Each subcase CNF represents the coefficient domain, exact positive/negative counts, every full autocorrelation equation, and one of those parity patterns.",
            "All eight formulas are UNSAT and every emitted proof passes the independent drat-trim checker.",
            "Therefore no signed (24,18,2)-difference set exists in the exact group C2 x C12."
        ],
        "encoding_validation": "The same two CNF encodings reproduce exhaustive SAT/UNSAT baselines at orders 5 and 9; see artifacts/runs/sat_baselines.json.",
        "subcases": [
            {
                "pattern_index": report["pattern_index"],
                "pattern": report["pattern"],
                "formula": report["formula"],
                "proof": report["proof"],
                "checker": report["checker"],
                "solve_seconds": report["solve_seconds"],
            }
            for report in reports
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "instance": document["instance"],
        "result": document["result"],
        "subcase_count": document["subcase_count"],
        "all_proofs_independently_checked": document["all_proofs_independently_checked"],
        "output": str(OUTPUT.relative_to(ROOT)),
        "sha256": sha256(OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    main()

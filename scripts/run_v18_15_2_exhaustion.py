#!/usr/bin/env python3
"""Two-path exact exhaustion of SDS(18,15,2,[3,6])."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import elements, parse_name  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402

INSTANCE = parse_name("SDS(18,15,2,[3,6])")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tuple_difference_table() -> List[List[int]]:
    elts = elements(INSTANCE.group)
    rank = {element: i for i, element in enumerate(elts)}
    return [
        [
            rank[
                tuple(
                    (elts[left][j] - elts[right][j]) % INSTANCE.group[j]
                    for j in range(len(INSTANCE.group))
                )
            ]
            for right in range(INSTANCE.v)
        ]
        for left in range(INSTANCE.v)
    ]


def method_a() -> dict:
    """Tuple-derived weighted-defect difference enumeration."""
    started = time.perf_counter()
    differences = tuple_difference_table()
    tested = 0
    solutions = []
    universe = range(INSTANCE.v)
    for zeros in itertools.combinations(universe, 3):
        zero_set = set(zeros)
        available = [i for i in universe if i not in zero_set]
        for negatives in itertools.combinations(available, 4):
            tested += 1
            positions = zeros + negatives
            weights = (1, 1, 1, 2, 2, 2, 2)
            correlation = [0] * INSTANCE.v
            for i, left in enumerate(positions):
                left_weight = weights[i]
                difference_row = differences[left]
                for j, right in enumerate(positions):
                    correlation[difference_row[right]] += left_weight * weights[j]
            # a=1-b, sum(b)=11: C_a(h)=18-22+C_b(h), target 2 => C_b(h)=6.
            if all(value == 6 for value in correlation[1:]):
                vector = [1] * INSTANCE.v
                for position in zeros:
                    vector[position] = 0
                for position in negatives:
                    vector[position] = -1
                solutions.append(tuple(vector))
    return {
        "name": "precomputed_tuple_difference_weighted_defect_search",
        "assignments_tested": tested,
        "solutions": solutions,
        "runtime_seconds": time.perf_counter() - started,
        "identity_check": "sum(b_g^2)=3+4*4=19; C_a(0)=18-2*11+19=15",
        "nonidentity_check": "C_a(h)=18-2*11+C_b(h)=2 iff C_b(h)=6",
    }


def mixed_radix_subtraction_table() -> List[List[int]]:
    moduli = INSTANCE.group
    digits = []
    for raw in range(INSTANCE.v):
        quotient = raw
        row = [0] * len(moduli)
        for j in range(len(moduli) - 1, -1, -1):
            row[j] = quotient % moduli[j]
            quotient //= moduli[j]
        digits.append(row)

    def rank(row: Sequence[int]) -> int:
        value = 0
        for digit, modulus in zip(row, moduli):
            value = value * modulus + digit
        return value

    return [
        [
            rank([(digits[left][j] - digits[shift][j]) % moduli[j] for j in range(len(moduli))])
            for left in range(INSTANCE.v)
        ]
        for shift in range(INSTANCE.v)
    ]


def direct_check(vector: Sequence[int], subtraction: Sequence[Sequence[int]]) -> bool:
    for shift, row in enumerate(subtraction):
        total = sum(vector[left] * vector[row[left]] for left in range(INSTANCE.v))
        if total != (INSTANCE.k if shift == 0 else INSTANCE.lam):
            return False
    return True


def method_b() -> dict:
    """Reverse-nested direct enumeration of both augmentation signs."""
    started = time.perf_counter()
    subtraction = mixed_radix_subtraction_table()
    positive_tested = 0
    negative_tested = 0
    solutions = []
    universe = range(INSTANCE.v)
    for negatives in itertools.combinations(universe, 4):
        negative_set = set(negatives)
        available = [i for i in universe if i not in negative_set]
        for zeros in itertools.combinations(available, 3):
            vector = [1] * INSTANCE.v
            for position in negatives:
                vector[position] = -1
            for position in zeros:
                vector[position] = 0
            positive_tested += 1
            if direct_check(vector, subtraction):
                solutions.append(tuple(vector))
            negated = [-value for value in vector]
            negative_tested += 1
            if direct_check(negated, subtraction):
                solutions.append(tuple(negated))
    return {
        "name": "direct_both_signs_flat_mixed_radix_search",
        "positive_sum_assignments_tested": positive_tested,
        "negative_sum_assignments_tested": negative_tested,
        "total_assignments_tested": positive_tested + negative_tested,
        "solutions": solutions,
        "runtime_seconds": time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "runs" / "v18_15_2_c3xc6_exhaustion.json",
    )
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    a = method_a()
    b = method_b()
    expected = math.comb(18, 3) * math.comb(15, 4)
    assert expected == 1113840
    assert a["assignments_tested"] == expected
    assert b["positive_sum_assignments_tested"] == expected
    assert b["negative_sum_assignments_tested"] == expected
    assert set(a["solutions"]) == {tuple(v) for v in b["solutions"] if sum(v) == 7}
    for vector in b["solutions"]:
        assert validate_reference(INSTANCE, vector)["valid"]
        assert validate_independent(INSTANCE, vector)["valid"]
    dataset = ROOT / "sources" / "signed-difference-sets" / "sds.json"
    report = {
        "schema": "v18-15-2-c3xc6-exhaustion-v1",
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 scripts/run_v18_15_2_exhaustion.py --output artifacts/runs/v18_15_2_c3xc6_exhaustion.json",
        "instance": INSTANCE.name,
        "result": "EXISTS" if a["solutions"] else "NONEXISTENT_BY_EXHAUSTION",
        "method_a": a,
        "method_b": b,
        "completeness_argument": [
            "The unreduced support-15 domain has C(18,15)*2^15=26738688 vectors.",
            "The trivial character gives (sum a_g)^2=15+2*(18-1)=49, so the sum is +7 or -7.",
            "For sum +7, support 15 forces eleven +1, four -1, and three zeros: C(18,3)*C(15,4)=1113840 vectors.",
            "Global sign bijects the two augmentation signs and preserves autocorrelation.",
            "Method B directly checks all 2227680 forced vectors of both signs."
        ],
        "validator_acceptance": {
            "reference": all(validate_reference(INSTANCE, v)["valid"] for v in b["solutions"]),
            "independent": all(validate_independent(INSTANCE, v)["valid"] for v in b["solutions"]),
            "vacuous_if_no_witness": not bool(b["solutions"])
        },
        "deterministic_enumeration": True,
        "seed": None,
        "input": {"path": str(dataset.relative_to(ROOT)), "sha256": sha256(dataset)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()}
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

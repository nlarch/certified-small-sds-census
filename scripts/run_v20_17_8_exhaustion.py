#!/usr/bin/env python3
"""Two-path exact exhaustion of SDS(20,17,8,[2,10])."""

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
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import Instance, elements, parse_name  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402


INSTANCE = parse_name("SDS(20,17,8,[2,10])")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tuple_difference_index(instance: Instance) -> Dict[Tuple[int, ...], int]:
    return {element: i for i, element in enumerate(elements(instance.group))}


def defect_search(instance: Instance) -> Dict[str, object]:
    """Enumerate three weight-1 and two weight-2 defects from all +1."""
    started = time.perf_counter()
    elts = elements(instance.group)
    index = tuple_difference_index(instance)
    tested = 0
    solutions: List[Tuple[int, ...]] = []
    universe = range(instance.v)
    for zeros in itertools.combinations(universe, 3):
        zero_set = set(zeros)
        available = [i for i in universe if i not in zero_set]
        for negatives in itertools.combinations(available, 2):
            tested += 1
            defects = [(position, 1) for position in zeros] + [
                (position, 2) for position in negatives
            ]
            defect_corr = [0] * instance.v
            for left, left_weight in defects:
                for right, right_weight in defects:
                    difference = tuple(
                        (elts[left][j] - elts[right][j]) % instance.group[j]
                        for j in range(len(instance.group))
                    )
                    defect_corr[index[difference]] += left_weight * right_weight
            # For a=1-b and sum(b)=7, C_a(h)=20-14+C_b(h).
            if all(value == 2 for value in defect_corr[1:]):
                vector = [1] * instance.v
                for position in zeros:
                    vector[position] = 0
                for position in negatives:
                    vector[position] = -1
                solutions.append(tuple(vector))
    return {
        "name": "weighted_defect_pair_difference_search",
        "assignments_tested": tested,
        "solutions": solutions,
        "runtime_seconds": time.perf_counter() - started,
        "identity_check": "sum(b_g^2)=3*1+2*4=11, hence C_a(0)=20-2*7+11=17",
        "nonidentity_check": "C_a(h)=20-2*7+C_b(h)=8 iff C_b(h)=2",
    }


def flat_subtraction_table(instance: Instance) -> List[List[int]]:
    """Mixed-radix subtraction table constructed without tuple group code."""
    moduli = instance.group
    digits = []
    for raw in range(instance.v):
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
            for left in range(instance.v)
        ]
        for shift in range(instance.v)
    ]


def exact_flat_check(
    instance: Instance, vector: Sequence[int], subtraction: Sequence[Sequence[int]]
) -> bool:
    if sum(x != 0 for x in vector) != instance.k:
        return False
    for shift in range(instance.v):
        total = sum(vector[left] * vector[subtraction[shift][left]] for left in range(instance.v))
        if total != (instance.k if shift == 0 else instance.lam):
            return False
    return True


def direct_signed_search(instance: Instance) -> Dict[str, object]:
    """Independently enumerate both augmentation signs with flat arithmetic."""
    started = time.perf_counter()
    subtraction = flat_subtraction_table(instance)
    positive_sum_tested = 0
    negative_sum_tested = 0
    solutions: List[Tuple[int, ...]] = []
    universe = range(instance.v)
    # Reverse the combinatorial nesting used by defect_search.
    for negatives in itertools.combinations(universe, 2):
        negative_set = set(negatives)
        available = [i for i in universe if i not in negative_set]
        for zeros in itertools.combinations(available, 3):
            vector = [1] * instance.v
            for position in zeros:
                vector[position] = 0
            for position in negatives:
                vector[position] = -1
            positive_sum_tested += 1
            if exact_flat_check(instance, vector, subtraction):
                solutions.append(tuple(vector))
            negated = [-value for value in vector]
            negative_sum_tested += 1
            if exact_flat_check(instance, negated, subtraction):
                solutions.append(tuple(negated))
    return {
        "name": "direct_both_signs_flat_mixed_radix_search",
        "positive_sum_assignments_tested": positive_sum_tested,
        "negative_sum_assignments_tested": negative_sum_tested,
        "total_assignments_tested": positive_sum_tested + negative_sum_tested,
        "solutions": solutions,
        "runtime_seconds": time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "runs" / "v20_17_8_c2xc10_exhaustion.json",
    )
    args = parser.parse_args()
    started_at = datetime.now(timezone.utc).isoformat()
    a = defect_search(INSTANCE)
    b = direct_signed_search(INSTANCE)
    normalized_expected = math.comb(20, 3) * math.comb(17, 2)
    assert normalized_expected == 155040
    assert a["assignments_tested"] == normalized_expected
    assert b["positive_sum_assignments_tested"] == normalized_expected
    assert b["negative_sum_assignments_tested"] == normalized_expected
    normalized_b = {tuple(v) for v in b["solutions"] if sum(v) == 13}
    assert set(a["solutions"]) == normalized_b
    for vector in b["solutions"]:
        assert validate_reference(INSTANCE, vector)["valid"]
        assert validate_independent(INSTANCE, vector)["valid"]
    dataset = ROOT / "sources" / "signed-difference-sets" / "sds.json"
    report = {
        "schema": "v20-17-8-c2xc10-exhaustion-v1",
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 scripts/run_v20_17_8_exhaustion.py --output artifacts/runs/v20_17_8_c2xc10_exhaustion.json",
        "instance": INSTANCE.name,
        "result": "EXISTS" if a["solutions"] else "NONEXISTENT_BY_EXHAUSTION",
        "method_a": a,
        "method_b": b,
        "completeness_argument": [
            "The unreduced support-17 domain has C(20,17)*2^17=149422080 vectors.",
            "The trivial character gives (sum a_g)^2=17+8*(20-1)=169, so the sum is +13 or -13.",
            "For sum +13, support 17 forces fifteen +1, two -1, and three zeros: C(20,3)*C(17,2)=155040 vectors.",
            "Global sign bijects the two augmentation signs and preserves autocorrelation.",
            "Method B directly checks all 310080 forced vectors of both signs, without quotienting global sign.",
        ],
        "validator_acceptance": {
            "reference": all(validate_reference(INSTANCE, v)["valid"] for v in b["solutions"]),
            "independent": all(validate_independent(INSTANCE, v)["valid"] for v in b["solutions"]),
            "vacuous_if_no_witness": not bool(b["solutions"]),
        },
        "deterministic_enumeration": True,
        "seed": None,
        "input": {"path": str(dataset.relative_to(ROOT)), "sha256": sha256(dataset)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

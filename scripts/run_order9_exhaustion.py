#!/usr/bin/env python3
"""Auditable exhaustion for the open [3,3] pilot and cyclic No baseline."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import Instance, elements, parse_name, witness_from_record  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_assignments() -> Sequence[Tuple[int, ...]]:
    """The 9*C(8,2)=252 vectors with one zero, two -1, and six +1."""
    assignments = []
    for zero in range(9):
        remaining = [i for i in range(9) if i != zero]
        for negative_pair in itertools.combinations(remaining, 2):
            vector = [1] * 9
            vector[zero] = 0
            for index in negative_pair:
                vector[index] = -1
            assignments.append(tuple(vector))
    return assignments


def tuple_autocorrelation(
    group: Sequence[int], coefficients: Sequence[int]
) -> Tuple[int, ...]:
    """Search-local tuple implementation, separate from both final validators."""
    elts = tuple(itertools.product(*(range(n) for n in group)))
    index = {element: i for i, element in enumerate(elts)}
    values = []
    for shift in elts:
        total = 0
        for i, left in enumerate(elts):
            right = tuple((left[j] - shift[j]) % group[j] for j in range(len(group)))
            total += coefficients[i] * coefficients[index[right]]
        values.append(total)
    return tuple(values)


def method_a(instance: Instance) -> Dict[str, object]:
    assignments = normalized_assignments()
    expected = instance.k + instance.lam * (instance.v - 1)
    solutions = []
    for vector in assignments:
        corr = tuple_autocorrelation(instance.group, vector)
        if corr[0] == instance.k and all(x == instance.lam for x in corr[1:]):
            solutions.append(vector)
    return {
        "name": "zero_position_and_negative_pair_tuple_search",
        "normalized_assignments_tested": len(assignments),
        "expected_trivial_character_square": expected,
        "normalized_coefficient_sum": 4,
        "solutions": solutions,
    }


def method_b(instance: Instance) -> Dict[str, object]:
    full_domain = 0
    support_eight = 0
    forced_by_character = 0
    normalized = 0
    solutions = []
    normalized_solutions = []
    for vector in itertools.product((-1, 0, 1), repeat=instance.v):
        full_domain += 1
        if sum(value != 0 for value in vector) != instance.k:
            continue
        support_eight += 1
        if abs(sum(vector)) != 4:
            continue
        forced_by_character += 1
        if sum(vector) == 4:
            normalized += 1
        report = validate_independent(instance, vector)
        if report["valid"]:
            solutions.append(vector)
            if sum(vector) == 4:
                normalized_solutions.append(vector)
    return {
        "name": "full_ternary_product_mixed_radix_validation",
        "full_ternary_domain_tested": full_domain,
        "support_eight_assignments": support_eight,
        "forced_abs_sum_four_assignments_tested": forced_by_character,
        "positive_sum_normalized_assignments": normalized,
        "solutions": solutions,
        "normalized_solutions": normalized_solutions,
    }


def run_exhaustion(instance: Instance) -> Dict[str, object]:
    started = time.perf_counter()
    a = method_a(instance)
    b = method_b(instance)
    assert a["normalized_assignments_tested"] == 9 * math.comb(8, 2) == 252
    assert b["full_ternary_domain_tested"] == 3**9 == 19683
    assert b["support_eight_assignments"] == 9 * 2**8 == 2304
    assert b["forced_abs_sum_four_assignments_tested"] == 504
    assert b["positive_sum_normalized_assignments"] == 252
    assert set(a["solutions"]) == set(b["normalized_solutions"])
    for vector in a["solutions"]:
        assert validate_reference(instance, vector)["valid"]
        assert validate_independent(instance, vector)["valid"]
    return {
        "instance": instance.name,
        "result": "EXISTS" if a["solutions"] else "NONEXISTENT_BY_EXHAUSTION",
        "method_a": a,
        "method_b": b,
        "runtime_seconds": time.perf_counter() - started,
        "completeness_argument": [
            "There are 3^9 total coefficient vectors and 9*2^8 with support 8.",
            "The augmentation/trivial-character equation gives (sum a_g)^2 = k + lambda*(v-1) = 16, hence sum a_g is +4 or -4.",
            "Support 8 and sum +4 force six +1, two -1, and one zero, giving 9*C(8,2)=252 assignments.",
            "Global sign is a fixed-point-free bijection between sums +4 and -4 and preserves every autocorrelation, so the normalized 252 cover all 504 forced assignments.",
            "Method B additionally enumerates and validates all 504 assignments without applying the global-sign quotient.",
        ],
    }


def positive_smoke(dataset: Dict[str, object]) -> Dict[str, object]:
    name = "SDS(5,4,-1,[5])"
    instance = parse_name(name)
    record = dataset[name]
    positive, negative = record["sets"][0]
    vector = witness_from_record(instance, positive, negative)
    reference = validate_reference(instance, vector)
    independent = validate_independent(instance, vector)
    if not reference["valid"] or not independent["valid"]:
        raise AssertionError("known-positive smoke test failed")
    return {
        "instance": name,
        "repository_status": record["status"],
        "coefficient_vector": vector,
        "reference_report": reference,
        "independent_report": independent,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "runs" / "order9_exhaustion.json",
    )
    args = parser.parse_args()
    dataset_path = ROOT / "sources" / "signed-difference-sets" / "sds.json"
    dataset = json.loads(dataset_path.read_text())
    report = {
        "schema": "order9-exhaustion-v1",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 scripts/run_order9_exhaustion.py --output artifacts/runs/order9_exhaustion.json",
        "deterministic_enumeration": True,
        "seed": None,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pid": os.getpid(),
        },
        "inputs": {"dataset_path": str(dataset_path.relative_to(ROOT)), "sha256": sha256(dataset_path)},
        "known_positive_smoke": positive_smoke(dataset),
        "open_pilot": run_exhaustion(parse_name("SDS(9,8,1,[3,3])")),
        "known_negative_baseline": run_exhaustion(parse_name("SDS(9,8,1,[9])")),
    }
    report["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""Order-3 character obstructions resolving six order-27 frozen entries."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REJECTED_PARAMETERS = ((12, 2), (23, 1), (23, 13))
GROUPS = ((3, 3, 3), (3, 9))
CONTROL_PARAMETERS = ((10, 1), (14, 5), (17, 4), (17, 8), (22, 3), (22, 9), (25, 16))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def requirements(k, lam):
    principal_square = k + lam * 26
    principal = math.isqrt(principal_square)
    assert principal * principal == principal_square
    norm = k - lam
    assert (principal_square - norm) % 3 == 0
    off = (principal_square - norm) // 3
    identity = norm + off
    return principal, norm, identity, off


def valid(sequence, principal, identity, off):
    return (
        sum(sequence) == principal
        and sum(value * value for value in sequence) == identity
        and all(
            sum(sequence[j] * sequence[(j - shift) % 3] for j in range(3)) == off
            for shift in (1, 2)
        )
    )


def method_a(k, lam):
    started = time.perf_counter()
    principal, _, identity, off = requirements(k, lam)
    tested = 0
    solutions = []
    for sequence in itertools.product(range(-9, 10), repeat=3):
        tested += 1
        if valid(sequence, principal, identity, off):
            solutions.append(sequence)
    return {
        "name": "full_bounded_three_tuple_product",
        "bounded_tuples_tested": tested,
        "solutions": solutions,
        "runtime_seconds": time.perf_counter() - started,
    }


def method_b(k, lam):
    started = time.perf_counter()
    principal, _, identity, off = requirements(k, lam)
    prefixes = 0
    completed = 0
    square_candidates = 0
    solutions = []
    for first, second in itertools.product(range(-9, 10), repeat=2):
        prefixes += 1
        third = principal - first - second
        if not -9 <= third <= 9:
            continue
        completed += 1
        sequence = (first, second, third)
        if sum(value * value for value in sequence) != identity:
            continue
        square_candidates += 1
        if all(
            sum(sequence[j] * sequence[(j - shift) % 3] for j in range(3)) == off
            for shift in (1, 2)
        ):
            solutions.append(sequence)
    return {
        "name": "two_tuple_with_derived_third_coordinate",
        "prefixes_tested": prefixes,
        "bounded_completed_tuples": completed,
        "identity_square_sum_candidates": square_candidates,
        "solutions": solutions,
        "runtime_seconds": time.perf_counter() - started,
    }


def analyze_parameters(k, lam):
    principal, norm, identity, off = requirements(k, lam)
    a = method_a(k, lam)
    b = method_b(k, lam)
    assert a["bounded_tuples_tested"] == 19**3 == 6859
    assert b["prefixes_tested"] == 19**2 == 361
    assert set(map(tuple, a["solutions"])) == set(map(tuple, b["solutions"]))
    return {
        "parameters": [27, k, lam],
        "principal_sum_normalized": principal,
        "nonprincipal_character_norm": norm,
        "required_fiber_autocorrelation": [identity, off, off],
        "method_a": a,
        "method_b": b,
    }


def main():
    started_at = datetime.now(timezone.utc).isoformat()
    rejected = []
    entries = []
    for k, lam in REJECTED_PARAMETERS:
        analysis = analyze_parameters(k, lam)
        assert not analysis["method_a"]["solutions"]
        rejected.append(analysis)
        for group in GROUPS:
            group_text = ",".join(map(str, group))
            entries.append({
                "instance": f"SDS(27,{k},{lam},[{group_text}])",
                "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_OBSTRUCTION",
                "parameter_analysis": [27, k, lam],
            })
    controls = []
    for k, lam in CONTROL_PARAMETERS:
        analysis = analyze_parameters(k, lam)
        assert analysis["method_a"]["solutions"]
        controls.append({
            "parameters": [27, k, lam],
            "allowed_fiber_sums": analysis["method_a"]["solutions"],
            "allowed_count": len(analysis["method_a"]["solutions"]),
        })
    dataset = ROOT / "sources" / "signed-difference-sets" / "sds.json"
    report = {
        "schema": "v27-order3-character-obstructions-v1",
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 scripts/prove_v27_order3_character_obstructions.py",
        "mathematical_argument": [
            "Each target group C3^3 or C3 x C9 has a nonprincipal order-three character with three fibers of size nine; their integer coefficient sums lie in [-9,9].",
            "Applying that character to the signed-difference-set equation gives |sum s_j*omega^j|^2=n=k-lambda.",
            "Writing the three cyclic fiber correlations as c_h, the degree-two polynomial sum c_h*x^h-n vanishes at a primitive cube root, so it is an integer multiple of Phi_3=1+x+x^2.",
            "Consequently c_1=c_2=t, c_0=n+t, and the normalized principal sum fixes t through principal_sum^2=n+3t.",
            "Method A exhausts all 19^3 bounded integer fiber-sum triples; Method B independently exhausts 19^2 prefixes and derives the third coordinate.",
            "Both methods find an empty feasible set for each rejected parameter triple, so no coefficient vector can satisfy even this necessary character equation in either exact target group."
        ],
        "rejected_parameter_analyses": rejected,
        "results": entries,
        "positive_parameter_controls": controls,
        "input": {"path": str(dataset.relative_to(ROOT)), "sha256": sha256(dataset)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "deterministic_enumeration": True,
        "seed": None,
    }
    output = ROOT / "artifacts" / "runs" / "v27_order3_character_obstructions.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(output.relative_to(ROOT)),
        "sha256": sha256(output),
        "resolved_entries": [entry["instance"] for entry in entries],
        "positive_control_count": len(controls),
    }, indent=2))


if __name__ == "__main__":
    main()
